import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from functools import wraps
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from dotenv import load_dotenv
import secrets
import re

from flask import Flask, jsonify, request, session, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash

load_dotenv()

from backend.db import (
    init_db,
    list_classes,
    list_results,
    get_class_by_id,
    get_class_by_room,
    get_latest_test,
    create_class as db_create_class,
    set_live_status,
    create_test as db_create_test,
    get_test,
    save_test_result,
    create_student,
    list_students,
    list_students_with_courses,
    set_student_courses,
    update_student_account,
    delete_student,
    auth_student,
    get_student_by_id,
    find_student_by_contact,
    list_courses,
    get_course_by_slug,
    get_course_by_id,
    unlock_course,
    list_lessons_for_course,
    get_lesson,
    create_lesson,
    create_course_from_live,
    create_course,
    list_tests_for_practice,
    summarize_test_results,
    ensure_class_for_course,
    create_teacher,
    list_teachers,
    delete_teacher,
    auth_teacher,
    get_teacher_by_id,
    log_live_join,
    live_stats_summary,
    admin_overview_summary,
    get_db,
    is_integrity_error,
    is_operational_error,
)


def load_local_env():
    env_path = Path(__file__).resolve().parent / '.env'
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding='utf-8', errors='ignore').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value

load_local_env()

ADMIN_LOGIN = os.environ.get('ADMIN_LOGIN', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change-me-now')
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-now')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
TELEGRAM_LINK = os.environ.get('TELEGRAM_LINK', 'https://t.me/mominov9969')
LIVE_ROOM_PASSWORD = os.environ.get('LIVE_ROOM_PASSWORD', 'change-me-now')
TEACHER_LOGIN = os.environ.get('TEACHER_LOGIN', 'teacher')
TEACHER_PASSWORD = os.environ.get('TEACHER_PASSWORD', 'change-me-now')

UPLOAD_DIR = Path(os.environ.get('UPLOAD_DIR') or (Path(__file__).resolve().parent / 'uploads'))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

frontend_origins = [
    origin.strip().rstrip('/')
    for origin in os.environ.get(
        'CORS_ORIGINS',
        'http://localhost:5173,http://127.0.0.1:5173'
    ).split(',')
    if origin.strip()
]

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Netlify frontend va Railway backend alohida HTTPS domenlarda ishlaydi.
# Productionda cross-site session cookie saqlanishi uchun Secure + SameSite=None kerak.
is_production = bool(
    os.environ.get('RAILWAY_ENVIRONMENT')
    or os.environ.get('RAILWAY_PUBLIC_DOMAIN')
    or os.environ.get('RAILWAY_STATIC_URL')
)
default_cookie_secure = '1' if is_production else '0'
cookie_secure = os.environ.get('COOKIE_SECURE', default_cookie_secure) == '1'
default_cookie_samesite = 'None' if cookie_secure else 'Lax'

app.config.update(
    SECRET_KEY=SECRET_KEY,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=cookie_secure,
    SESSION_COOKIE_SAMESITE=os.environ.get('COOKIE_SAMESITE', default_cookie_samesite),
    MAX_CONTENT_LENGTH=int(os.environ.get('MAX_UPLOAD_MB', '300')) * 1024 * 1024,
)
CORS(app, supports_credentials=True, origins=frontend_origins)
socketio = SocketIO(app, cors_allowed_origins=frontend_origins, async_mode='threading')

teacher_sid_by_room = {}
student_sid_map = {}
online_student_sid_map = {}


PHONE_RE = re.compile(r'^(?:\+998|998)?\d{9}$')
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def normalize_phone(value: str):
    raw = re.sub(r'\D', '', (value or '').strip())
    if raw.startswith('998') and len(raw) == 12:
        raw = raw[3:]
    if len(raw) != 9:
        return ''
    return raw


def generate_room_code(prefix: str = 'LIVE'):
    while True:
        candidate = f"{prefix}{secrets.token_hex(3).upper()}"
        if not get_class_by_room(candidate):
            return candidate


def is_valid_email(value: str):
    return bool(EMAIL_RE.match((value or '').strip().lower()))


def latest_uploaded_file_url():
    files = [p for p in UPLOAD_DIR.glob('*') if p.is_file()]
    if not files:
        return ''
    latest = max(files, key=lambda p: p.stat().st_mtime)
    return f"/uploads/{latest.name}"


def normalize_video_url(url: str):
    value = (url or '').strip()
    if not value:
        return ''
    if value.startswith('/uploads/'):
        return value
    if '/uploads/' in value:
        return '/uploads/' + value.split('/uploads/', 1)[1]
    return value


def room_participant_count(room_code):
    room_code = (room_code or '').upper()
    return sum(1 for s in student_sid_map.values() if s['room'] == room_code)




def active_students_payload():
    # Bir o‘quvchi bir nechta tab ochsa ham admin panelda 1 ta hisoblanadi.
    unique = {}
    for sid, info in online_student_sid_map.items():
        key = str(info.get('id') or sid)
        unique[key] = info
    students = sorted(unique.values(), key=lambda item: item.get('connected_at') or '', reverse=True)
    return {
        'active_students_count': len(students),
        'active_students': students,
    }




def admin_full_info_payload():
    conn = get_db()
    today = datetime.utcnow().strftime('%Y-%m-%d')
    current_month = datetime.utcnow().strftime('%Y-%m')
    current_year = datetime.utcnow().strftime('%Y')
    daily_students_count = conn.execute("SELECT COUNT(*) FROM students WHERE substr(created_at, 1, 10) = ?", (today,)).fetchone()[0]
    monthly_students_count = conn.execute("SELECT COUNT(*) FROM students WHERE substr(created_at, 1, 7) = ?", (current_month,)).fetchone()[0]
    yearly_students_count = conn.execute("SELECT COUNT(*) FROM students WHERE substr(created_at, 1, 4) = ?", (current_year,)).fetchone()[0]
    daily_purchases_count = conn.execute("SELECT COUNT(*) FROM unlocked_courses WHERE substr(unlocked_at, 1, 10) = ?", (today,)).fetchone()[0]
    monthly_purchases_count = conn.execute("SELECT COUNT(*) FROM unlocked_courses WHERE substr(unlocked_at, 1, 7) = ?", (current_month,)).fetchone()[0]
    yearly_purchases_count = conn.execute("SELECT COUNT(*) FROM unlocked_courses WHERE substr(unlocked_at, 1, 4) = ?", (current_year,)).fetchone()[0]
    purchases = conn.execute("""
        SELECT uc.id, uc.unlocked_at, s.first_name, s.last_name, s.phone, s.email, c.title as course_title, c.level, c.track, c.price
        FROM unlocked_courses uc
        JOIN students s ON s.id = uc.student_id
        JOIN courses c ON c.id = uc.course_id
        ORDER BY uc.id DESC
    """).fetchall()
    conn.close()
    return {
        'daily_students_count': daily_students_count,
        'monthly_students_count': monthly_students_count,
        'yearly_students_count': yearly_students_count,
        'daily_purchases_count': daily_purchases_count,
        'monthly_purchases_count': monthly_purchases_count,
        'yearly_purchases_count': yearly_purchases_count,
        'purchases': [dict(row) for row in purchases],
    }


def html_table(title, subtitle, headers, rows):
    from html import escape
    head = ''.join(f'<th>{escape(str(h))}</th>' for h in headers)
    body = []
    for row in rows:
        body.append('<tr>' + ''.join(f'<td>{escape(str(cell if cell is not None else ""))}</td>' for cell in row) + '</tr>')
    return f"""
    <section>
      <h2>{escape(title)}</h2>
      <p>{escape(subtitle)}</p>
      <table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>
    </section>
    """


def excel_response(filename, tables_html):
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
    body{{font-family:Arial,sans-serif;background:#f8fafc;color:#0f172a;padding:18px}}
    h1{{color:#1e3a8a;margin:0 0 8px}} h2{{color:#4f46e5;margin:24px 0 6px}} p{{color:#475569;margin:0 0 12px}}
    table{{border-collapse:collapse;width:100%;margin:8px 0 20px;background:#fff}}
    th{{background:linear-gradient(135deg,#3B82F6,#8B5CF6,#EC4899);color:white;padding:12px;border:1px solid #c7d2fe;font-weight:800}}
    td{{padding:10px;border:1px solid #cbd5e1}} tr:nth-child(even) td{{background:#f1f5f9}} tr:nth-child(odd) td{{background:#ffffff}}
    .meta{{background:#eef2ff;border:1px solid #c7d2fe;border-radius:12px;padding:12px;margin:10px 0 18px}}
    </style></head><body><h1>EduLive Pro — Excel hisobot</h1><div class="meta">Yuklangan vaqt: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</div>{tables_html}</body></html>"""
    resp = app.response_class(html, mimetype='application/vnd.ms-excel; charset=utf-8')
    resp.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return resp


def emit_admin_realtime():
    payload = active_students_payload()
    socketio.emit('admin-overview-live', payload, room='admins')


def enrich_course_live_data(data):
    payload = dict(data)
    # Live yozuv kurslari alohida “Live darslar” bo‘limida ko‘rinishi uchun.
    payload['is_live_class'] = 1 if (payload.get('is_live_class') or str(payload.get('track') or '').lower() == 'live') else 0
    payload['live_participants_count'] = room_participant_count(payload.get('room_code')) if payload.get('room_code') else 0
    return payload


def send_registration_to_telegram(student):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    message = (
        "🆕 Yangi registratsiya\n"
        f"Ism: {student.get('first_name', '')}\n"
        f"Familiya: {student.get('last_name', '')}\n"
        f"Telefon: {student.get('phone', '') or '-'}\n"
        f"Email: {student.get('email', '') or '-'}\n"
        f"Login: {student.get('username', '') or '-'}\n"
        f"Vaqt: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
    )
    try:
        data = urlencode({'chat_id': TELEGRAM_CHAT_ID, 'text': message}).encode('utf-8')
        req = Request(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage', data=data)
        with urlopen(req, timeout=10) as response:
            return 200 <= getattr(response, 'status', 200) < 300
    except Exception:
        return False


def ok(data=None, status=200):
    payload = {'ok': True}
    if data:
        payload.update(data)
    return jsonify(payload), status


def error(message, status=400):
    return jsonify({'ok': False, 'error': message}), status


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            return error('Admin login kerak.', 401)
        return f(*args, **kwargs)
    return wrapper


def teacher_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Built-in teacher login uses only username/password and has no row in DB.
        # So we keep a separate session flag; created teachers still use teacher_id.
        if not session.get('is_admin') and not session.get('teacher_id') and not session.get('is_teacher'):
            return error('Ustoz login kerak.', 401)
        return f(*args, **kwargs)
    return wrapper


def student_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        student_id = session.get('student_id')
        if not student_id:
            return error('Avval registratsiyadan o‘ting.', 401)
        student = get_student_by_id(student_id)
        if not student:
            session.pop('student_id', None)
            return error('Student topilmadi.', 401)
        request.student = student
        return f(*args, **kwargs)
    return wrapper


def serialize_course(course, include_lessons=False, student_id=None, include_secret=False):
    if not course:
        return None
    data = enrich_course_live_data(dict(course))
    if not include_secret:
        data.pop('purchase_password', None)
    if include_lessons:
        lessons = list_lessons_for_course(course['id'], include_preview=True)
        if data.get('is_unlocked'):
            data['lessons'] = lessons
        else:
            data['lessons'] = [{
                'id': lesson['id'],
                'title': lesson['title'],
                'summary': lesson['summary'],
                'order_no': lesson['order_no'],
                'is_preview': lesson['is_preview'],
                'is_locked': 0 if lesson['is_preview'] else 1,
            } for lesson in lessons]
    return data


@app.get('/api/health')
def health():
    return ok({'service': 'vue-live-class-platform-backend', 'telegram_link': TELEGRAM_LINK, 'live_room_password_hint': 'set'})

@app.get('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=False)


@app.post('/api/admin/uploads/live-recording')
@teacher_required
def upload_live_recording():
    uploaded = request.files.get('file')
    if not uploaded or not uploaded.filename:
        return error('Video fayl topilmadi.')
    ext = Path(uploaded.filename).suffix.lower() or '.webm'
    safe_name = f"live_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}{ext}"
    destination = UPLOAD_DIR / safe_name
    uploaded.save(destination)
    file_url = '/uploads/' + safe_name
    return ok({'url': file_url, 'filename': safe_name}, 201)



@app.post('/api/admin/login')
def admin_login():
    data = request.get_json(silent=True) or {}
    if (data.get('username','') or '').strip().lower() != ADMIN_LOGIN.lower() or data.get('password', '') != ADMIN_PASSWORD:
        return error('Login yoki parol noto‘g‘ri.', 401)
    session['is_admin'] = True
    session.pop('teacher_id', None)
    session.pop('is_teacher', None)
    session.pop('student_id', None)
    return ok({'message': 'Kirish muvaffaqiyatli.'})


@app.post('/api/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    session.pop('is_teacher', None)
    session.pop('teacher_id', None)
    return ok({'message': 'Tizimdan chiqildi.'})


@app.get('/api/admin/session')
def admin_session():
    return ok({'is_admin': bool(session.get('is_admin'))})


@app.post('/api/student/register')
def student_register():
    return error('Ochiq registratsiya o‘chirilgan. Login va parolni admin beradi.', 403)


@app.post('/api/access/login')
def access_login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip().lower()
    password = (data.get('password') or '').strip()

    if username == ADMIN_LOGIN.lower() and password == ADMIN_PASSWORD:
        session['is_admin'] = True
        session.pop('teacher_id', None)
        session.pop('is_teacher', None)
        session.pop('student_id', None)
        session.pop('pending_student_id', None)
        return ok({'role': 'admin', 'message': 'Admin paneliga xush kelibsiz.'})

    if username == TEACHER_LOGIN.lower() and password == TEACHER_PASSWORD:
        session['teacher_id'] = None
        session['is_teacher'] = True
        session['is_admin'] = False
        session.pop('student_id', None)
        session.pop('pending_student_id', None)
        return ok({'role': 'teacher', 'teacher': {'full_name': 'Bosh ustoz', 'username': TEACHER_LOGIN}, 'message': 'Ustoz paneliga xush kelibsiz.'})

    teacher = auth_teacher(username, password)
    if teacher:
        session['teacher_id'] = teacher['id']
        session['is_teacher'] = True
        session['is_admin'] = False
        session.pop('student_id', None)
        session.pop('pending_student_id', None)
        safe_teacher = {key: value for key, value in teacher.items() if key != 'password'}
        return ok({'role': 'teacher', 'teacher': safe_teacher, 'message': 'Ustoz paneliga xush kelibsiz.'})

    student = auth_student(username, password)
    if student:
        session['student_id'] = student['id']
        session.pop('teacher_id', None)
        session.pop('is_teacher', None)
        session.pop('is_admin', None)
        safe_student = {key: value for key, value in student.items() if key != 'password'}
        return ok({'role': 'student', 'student': safe_student, 'message': 'O‘quvchi paneliga xush kelibsiz.'})

    return error('Login yoki parol xato.', 401)


@app.post('/api/student/login')
def student_login():
    return access_login()


@app.post('/api/student/logout')
def student_logout():
    session.pop('student_id', None)
    session.pop('pending_student_id', None)
    session.pop('teacher_id', None)
    session.pop('is_teacher', None)
    session.pop('is_admin', None)
    return ok({'message': 'Tizimdan chiqildi.'})


@app.get('/api/access/session')
def access_session():
    student = get_student_by_id(session.get('student_id')) if session.get('student_id') else None
    teacher = get_teacher_by_id(session.get('teacher_id')) if session.get('teacher_id') else None
    if not teacher and session.get('is_teacher'):
        teacher = {'id': None, 'full_name': 'Bosh ustoz', 'username': TEACHER_LOGIN}
    role = 'admin' if session.get('is_admin') else ('teacher' if teacher or session.get('is_teacher') else ('student' if student else None))
    safe_student = {key: value for key, value in student.items() if key != 'password'} if student else None
    safe_teacher = {key: value for key, value in teacher.items() if key != 'password'} if teacher else None
    return ok({'role': role, 'student': safe_student, 'teacher': safe_teacher, 'is_admin': bool(session.get('is_admin'))})


@app.get('/api/student/session')
def student_session():
    student = get_student_by_id(session.get('student_id')) if session.get('student_id') else None
    teacher = get_teacher_by_id(session.get('teacher_id')) if session.get('teacher_id') else None
    if not teacher and session.get('is_teacher'):
        teacher = {'id': None, 'full_name': 'Bosh ustoz', 'username': TEACHER_LOGIN}
    role = 'admin' if session.get('is_admin') else ('teacher' if teacher or session.get('is_teacher') else ('student' if student else None))
    safe_student = {key: value for key, value in student.items() if key != 'password'} if student else None
    safe_teacher = {key: value for key, value in teacher.items() if key != 'password'} if teacher else None
    return ok({'student': safe_student, 'teacher': safe_teacher, 'role': role, 'is_admin': bool(session.get('is_admin'))})


@app.get('/api/courses')
def courses_list():
    courses = [serialize_course(course) for course in list_courses(session.get('student_id'))]
    return ok({'courses': courses})


@app.get('/api/admin/courses')
@teacher_required
def admin_courses_list():
    courses = []
    for course in list_courses():
        item = serialize_course(course, include_lessons=True, include_secret=True)
        item['lessons_count'] = len(item.get('lessons', []))
        courses.append(item)
    return ok({'courses': courses})


@app.get('/api/courses/<slug>')
def course_detail(slug):
    course = get_course_by_slug(slug, session.get('student_id'))
    if not course:
        return error('Kurs topilmadi.', 404)
    linked_class = get_class_by_room(course['room_code']) if course.get('room_code') else None
    latest_test = get_latest_test(linked_class['id']) if linked_class else None
    if linked_class:
        linked_class['participants_count'] = room_participant_count(linked_class.get('room_code'))
    return ok({'course': serialize_course(course, include_lessons=True), 'class': linked_class, 'latest_test': latest_test})


@app.get('/api/courses/<slug>/lessons/<int:lesson_id>')
def lesson_detail(slug, lesson_id):
    course = get_course_by_slug(slug, session.get('student_id'))
    if not course:
        return error('Kurs topilmadi.', 404)
    lesson = get_lesson(lesson_id)
    if not lesson or lesson['course_id'] != course['id']:
        return error('Darslik topilmadi.', 404)
    if not course.get('is_unlocked') and not lesson.get('is_preview'):
        return error('Avval kursni oching.', 403)
    return ok({'course': serialize_course(course), 'lesson': lesson})


@app.post('/api/courses/<slug>/unlock')
@student_required
def course_unlock(slug):
    course = get_course_by_slug(slug, request.student['id'])
    if not course:
        return error('Kurs topilmadi.', 404)
    return error('Kurs faqat admin tomonidan o‘quvchi akkauntiga biriktiriladi.', 403)


@app.post('/api/admin/courses/<int:course_id>/lessons')
@teacher_required
def add_lesson(course_id):
    course = get_course_by_id(course_id)
    if not course:
        return error('Kurs topilmadi.', 404)
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    summary = (data.get('summary') or '').strip()
    video_url = (data.get('video_url') or '').strip()
    order_no = int(data.get('order_no') or 1)
    is_preview = 1 if data.get('is_preview') else 0
    if not title or not video_url:
        return error('Dars nomi va video link kerak.')
    lesson = create_lesson(course_id, title, summary, video_url, order_no, is_preview)
    return ok({'lesson': lesson, 'message': 'Video darslik qo‘shildi.'}, 201)


@app.get('/api/classes')
def classes_list():
    classes = list_classes()
    enriched = []
    for klass in classes:
        latest_test = get_latest_test(klass['id'])
        enriched.append({**klass, 'latest_test_id': latest_test['id'] if latest_test else None})
    return ok({'classes': enriched})


@app.post('/api/classes')
@admin_required
def create_class():
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    room_code = (data.get('room_code') or '').strip().upper() or generate_room_code()
    description = (data.get('description') or '').strip()
    if not title:
        return error('Sarlavha kerak.')
    try:
        klass = db_create_class(title, room_code, description)
    except Exception as exc:
        if is_integrity_error(exc):
            return error('Bu live dars kodi allaqachon mavjud.', 409)
        raise
    return ok({'class': klass}, 201)



@app.get('/api/live/active')
def active_live_class():
    classes = [item for item in list_classes() if item.get('is_live')]
    if not classes:
        return ok({'class': None})
    klass = classes[0]
    latest_test = get_latest_test(klass['id'])
    klass['participants_count'] = room_participant_count(klass.get('room_code'))
    return ok({'class': klass, 'latest_test': latest_test})


@app.get('/api/admin/live/default-class')
@teacher_required
def default_live_class():
    classes = list_classes()
    if classes:
        klass = classes[0]
    else:
        klass = db_create_class('Asosiy live dars', 'LIVE001', 'Ustoz panelidan tezkor live dars o‘tish xonasi')
    klass['participants_count'] = room_participant_count(klass.get('room_code'))
    return ok({'class': klass, 'latest_test': get_latest_test(klass['id'])})


@app.get('/api/classes/<room_code>')
def class_by_room(room_code):
    klass = get_class_by_room(room_code.upper())
    if not klass:
        return error('Bunday xona topilmadi.', 404)
    latest_test = get_latest_test(klass['id'])
    klass['participants_count'] = room_participant_count(klass.get('room_code'))
    return ok({'class': klass, 'latest_test': latest_test})




@app.post('/api/classes/<room_code>/join-live')
def join_live_room(room_code):
    klass = get_class_by_room(room_code.upper())
    if not klass:
        return error('Bunday xona topilmadi.', 404)
    if not klass.get('is_live'):
        return error('Live dars hozir yoqilmagan.', 409)
    data = request.get_json(silent=True) or {}
    session_student = get_student_by_id(session.get('student_id')) if session.get('student_id') else None
    password = (data.get('password') or '').strip()
    # Registered students can join from their panel without a separate live password.
    # If a guest enters directly by room link, keep the old password protection.
    if not session_student and password != LIVE_ROOM_PASSWORD:
        return error('Live dars paroli xato.', 401)
    latest_test = get_latest_test(klass['id'])
    student_name = (data.get('student_name') or '').strip()
    if session_student:
        student_name = f"{session_student.get('first_name', '').strip()} {session_student.get('last_name', '').strip()}".strip()
    if not student_name:
        student_name = 'Noma’lum o‘quvchi'
    log_live_join(klass['id'], klass['room_code'], student_name)
    return ok({'class': klass, 'latest_test': latest_test, 'message': 'Live darsga kirish tasdiqlandi.'})

@app.get('/api/admin/classes/<int:class_id>')
@teacher_required
def admin_class_detail(class_id):
    klass = get_class_by_id(class_id)
    if not klass:
        return error('Dars topilmadi.', 404)
    test = get_latest_test(class_id)
    return ok({'class': klass, 'latest_test': test})


@app.post('/api/admin/classes/<int:class_id>/toggle-live')
@teacher_required
def toggle_live(class_id):
    klass = get_class_by_id(class_id)
    if not klass:
        return error('Dars topilmadi.', 404)
    updated = set_live_status(class_id, not bool(klass['is_live']))
    if updated:
        socketio.emit('live-status-changed', {'class': updated, 'is_live': bool(updated.get('is_live'))})
        if updated.get('room_code'):
            socketio.emit('live-status', {'is_live': bool(updated.get('is_live')), 'class': updated}, room=updated.get('room_code'))
    return ok({'class': updated})




@app.post('/api/admin/classes/<int:class_id>/save-live-course')
@teacher_required
def save_live_course(class_id):
    klass = get_class_by_id(class_id)
    if not klass:
        return error('Dars topilmadi.', 404)
    data = request.get_json(silent=True) or {}
    base_course_id = int(data.get('base_course_id') or 0)
    title = (data.get('title') or '').strip()
    summary = (data.get('summary') or '').strip()
    level = (data.get('level') or '').strip()
    video_url = normalize_video_url(data.get('video_url') or '')
    if not video_url:
        video_url = latest_uploaded_file_url()
    price = data.get('price')
    try:
        price = int(price) if str(price).strip() else None
    except Exception:
        price = None
    if not base_course_id or not title or not video_url or not level:
        return error('Kurs, dars nomi, daraja va live yozuv kerak. Avval darsni to‘xtating, darajasini yozing va saqlang.')
    course = create_course_from_live(base_course_id, title, summary, video_url, None, price, level)
    if not course:
        return error('Asosiy kurs topilmadi.', 404)
    return ok({'course': course, 'message': 'Live dars kurslar bo‘limiga saqlandi.'}, 201)


@app.post('/api/admin/classes/<int:class_id>/tests')
@teacher_required
def create_test(class_id):
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    questions = data.get('questions') or []
    cleaned_questions = []
    for item in questions:
        question = (item.get('question') or '').strip()
        options = item.get('options') or {}
        correct = (item.get('correct') or '').strip().upper()
        if not question or correct not in {'A', 'B', 'C', 'D'}:
            continue
        normalized = {k: (options.get(k) or '').strip() for k in ['A', 'B', 'C', 'D']}
        if not all(normalized.values()):
            continue
        cleaned_questions.append({'question': question, 'options': normalized, 'correct': correct})
    if not title or not cleaned_questions:
        return error('Test nomi va kamida 1 ta to‘liq savol kerak.')
    test = db_create_test(class_id, title, cleaned_questions)
    return ok({'test': test}, 201)


@app.post('/api/admin/practice-tests/import')
@teacher_required
def import_practice_test():
    data = request.get_json(silent=True) or {}
    course_id = int(data.get('course_id') or 0)
    title = (data.get('title') or '').strip()
    questions = data.get('questions') or []
    if not course_id or not title or not isinstance(questions, list):
        return error('Kurs, test nomi va savollar kerak.')
    course = get_course_by_id(course_id)
    if not course:
        return error('Kurs topilmadi.', 404)
    cleaned_questions = []
    for item in questions:
        question = (item.get('question') or '').strip()
        options = item.get('options') or {}
        correct = (item.get('correct') or '').strip().upper()
        normalized = {k: (options.get(k) or '').strip() for k in ['A','B','C','D']}
        if question and all(normalized.values()) and correct in {'A','B','C','D'}:
            cleaned_questions.append({'question': question, 'options': normalized, 'correct': correct})
    if not cleaned_questions:
        return error('Excel test savollari topilmadi.')
    klass = ensure_class_for_course(course_id)
    test = db_create_test(klass['id'], title, cleaned_questions)
    return ok({'test': test, 'class': klass, 'message': 'Test saqlandi.'}, 201)


@app.get('/api/practice-tests')
def practice_tests():
    track = (request.args.get('track') or '').strip().lower() or None
    level = (request.args.get('level') or '').strip() or None
    tests = list_tests_for_practice(track, level)
    return ok({'tests': tests})


@app.get('/api/admin/tests/<int:test_id>/summary')
@teacher_required
def admin_test_summary(test_id):
    test = get_test(test_id)
    if not test:
        return error('Test topilmadi.', 404)
    summary = summarize_test_results(test_id)
    return ok({'summary': summary, 'test': test})


@app.get('/api/tests/<int:test_id>')
def test_detail(test_id):
    test = get_test(test_id)
    if not test:
        return error('Test topilmadi.', 404)
    klass = get_class_by_id(test['class_id'])
    return ok({'test': test, 'class': klass})


@app.post('/api/tests/<int:test_id>/submit')
def submit_test(test_id):
    test = get_test(test_id)
    if not test:
        return error('Test topilmadi.', 404)
    data = request.get_json(silent=True) or {}
    session_student = get_student_by_id(session.get('student_id')) if session.get('student_id') else None
    if session_student:
        student_name = f"{session_student.get('first_name', '').strip()} {session_student.get('last_name', '').strip()}".strip()
    else:
        student_name = (data.get('student_name') or '').strip() or 'Noma’lum'
    submitted_answers = data.get('answers') or {}
    score = 0
    answers = []
    for idx, q in enumerate(test['questions']):
        key = str(idx)
        ans = (submitted_answers.get(key) or '').strip().upper()
        is_correct = ans == q['correct']
        if is_correct:
            score += 1
        answers.append({'question': q['question'], 'selected': ans, 'correct': q['correct'], 'is_correct': is_correct})
    result = save_test_result(test_id, student_name, score, len(test['questions']), answers)
    return ok({'result': result, 'score': score, 'total': len(test['questions'])})


@app.get('/api/admin/results')
@teacher_required
def results_list():
    track = (request.args.get('track') or '').strip().lower() or None
    return ok({'results': list_results(track)})


@app.get('/api/admin/class/<room_code>/participants')
@teacher_required
def participants(room_code):
    room_code = room_code.upper()
    users = [
        {'sid': sid, 'name': info['name'], 'joined_at': info.get('joined_at')}
        for sid, info in student_sid_map.items() if info['room'] == room_code
    ]
    return ok({'participants': users})



@socketio.on('admin-watch')
def on_admin_watch():
    join_room('admins')
    emit('admin-overview-live', active_students_payload(), room=request.sid)


@socketio.on('student-online')
def on_student_online(data=None):
    data = data or {}
    student = data.get('student') or {}
    student_id = student.get('id')
    first_name = (student.get('first_name') or '').strip()
    last_name = (student.get('last_name') or '').strip()
    full_name = f"{first_name} {last_name}".strip() or (student.get('username') or 'O‘quvchi')
    online_student_sid_map[request.sid] = {
        'id': student_id,
        'name': full_name,
        'first_name': first_name,
        'last_name': last_name,
        'phone': student.get('phone') or '',
        'email': student.get('email') or '',
        'username': student.get('username') or '',
        'connected_at': datetime.utcnow().isoformat(),
    }
    emit_admin_realtime()


@socketio.on('join-room')
def on_join_room(data):
    room = (data.get('room') or '').upper()
    role = data.get('role')
    name = (data.get('name') or 'Guest').strip() or 'Guest'
    if not room:
        return
    join_room(room)
    if role == 'teacher':
        teacher_sid_by_room[room] = request.sid
        emit('teacher-ready', {'message': 'Teacher connected'}, room=room)
        emit('participants-update', {'count': sum(1 for s in student_sid_map.values() if s['room'] == room)}, room=request.sid)
        for sid, info in student_sid_map.items():
            if info['room'] == room:
                emit('student-joined', {'studentId': sid, 'name': info['name'], 'joinedAt': info.get('joined_at')}, room=request.sid)
    else:
        joined_at = datetime.utcnow().isoformat()
        student_sid_map[request.sid] = {'room': room, 'name': name, 'joined_at': joined_at}
        teacher_sid = teacher_sid_by_room.get(room)
        if teacher_sid:
            emit('student-joined', {'studentId': request.sid, 'name': name, 'joinedAt': joined_at}, room=teacher_sid)
        emit('participants-update', {'count': sum(1 for s in student_sid_map.values() if s['room'] == room)}, room=room)


@socketio.on('webrtc-offer')
def on_offer(data):
    emit('webrtc-offer', {'offer': data.get('offer'), 'from': request.sid}, room=data.get('target'))


@socketio.on('webrtc-answer')
def on_answer(data):
    emit('webrtc-answer', {'answer': data.get('answer'), 'from': request.sid}, room=data.get('target'))


@socketio.on('webrtc-ice-candidate')
def on_ice(data):
    emit('webrtc-ice-candidate', {'candidate': data.get('candidate'), 'from': request.sid}, room=data.get('target'))


@socketio.on('kick-student')
def on_kick_student(data):
    student_id = data.get('studentId')
    if student_id in student_sid_map:
        room = student_sid_map[student_id]['room']
        student_sid_map.pop(student_id, None)
        emit('participants-update', {'count': sum(1 for s in student_sid_map.values() if s['room'] == room)}, room=room)
    emit('kicked', {'message': 'Ustoz sizni xonadan chiqardi.'}, room=student_id)


@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    if sid in online_student_sid_map:
        online_student_sid_map.pop(sid, None)
        emit_admin_realtime()
    if sid in student_sid_map:
        room = student_sid_map[sid]['room']
        teacher_sid = teacher_sid_by_room.get(room)
        if teacher_sid:
            emit('student-left', {'studentId': sid}, room=teacher_sid)
        student_sid_map.pop(sid, None)
        emit('participants-update', {'count': sum(1 for s in student_sid_map.values() if s['room'] == room)}, room=room)
        leave_room(room)
    else:
        for room, teacher_sid in list(teacher_sid_by_room.items()):
            if teacher_sid == sid:
                teacher_sid_by_room.pop(room, None)
                emit('teacher-disconnected', {'message': 'Ustoz chiqib ketdi.'}, room=room)
                leave_room(room)
                break




@app.get('/api/admin/live-stats')
@teacher_required
def admin_live_stats():
    return ok({'stats': live_stats_summary(), 'classes': list_classes()})


@app.get('/api/teacher/students')
@teacher_required
def teacher_students():
    # Ustoz va admin registratsiyadan o‘tgan o‘quvchilarning xavfsiz ma’lumotlarini ko‘radi.
    return ok({'students': list_students()})

@app.get('/api/admin/overview')
@admin_required
def admin_overview():
    data = admin_overview_summary()
    data.update(admin_full_info_payload())
    data.update(active_students_payload())
    # Admin panelda o‘quvchilar ism-familiyasi tez ko‘rinishi uchun oxirgi 3 ta ro‘yxat
    data['recent_students'] = list_students()[:3]
    return ok(data)


@app.get('/api/admin/export/students.csv')
@admin_required
def admin_export_students_csv():
    import csv
    from io import StringIO
    rows = list_students()
    buf = StringIO()
    buf.write('\ufeff')
    writer = csv.writer(buf)
    writer.writerow(['ID', 'Ism', 'Familiya', 'Telefon', 'Email', 'Login', 'Registratsiya vaqti'])
    for item in rows:
        writer.writerow([item.get('id',''), item.get('first_name',''), item.get('last_name',''), item.get('phone',''), item.get('email',''), item.get('username',''), item.get('created_at','')])
    resp = app.response_class(buf.getvalue(), mimetype='text/csv; charset=utf-8')
    resp.headers['Content-Disposition'] = 'attachment; filename=oquvchilar_malumoti.csv'
    return resp

@app.get('/api/admin/export/students.xls')
@admin_required
def admin_export_students_excel():
    # Excel ochadigan chiroyli HTML jadval. Qo‘shimcha kutubxona talab qilmaydi.
    from html import escape
    rows = list_students()
    tr = []
    for i, item in enumerate(rows, 1):
        full_name = f"{item.get('first_name','')} {item.get('last_name','')}".strip()
        tr.append(f"""
        <tr>
          <td>{i}</td>
          <td>{escape(item.get('first_name','') or '')}</td>
          <td>{escape(item.get('last_name','') or '')}</td>
          <td>{escape(full_name)}</td>
          <td>{escape(item.get('phone','') or '')}</td>
          <td>{escape(item.get('email','') or '')}</td>
          <td>{escape(item.get('username','') or '')}</td>
          <td>{escape(item.get('created_at','') or '')}</td>
        </tr>""")
    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; background:#f8fafc; color:#0f172a; }}
  h1 {{ color:#1e40af; margin:18px 0 4px; }}
  p {{ color:#475569; margin:0 0 14px; }}
  table {{ border-collapse:collapse; width:100%; background:white; }}
  th {{ background:linear-gradient(135deg,#3B82F6,#8B5CF6,#EC4899); color:white; font-weight:700; padding:12px; border:1px solid #c7d2fe; }}
  td {{ padding:10px; border:1px solid #cbd5e1; }}
  tr:nth-child(even) td {{ background:#eef2ff; }}
  tr:nth-child(odd) td {{ background:#ffffff; }}
  .meta {{ background:#dbeafe; padding:10px; border:1px solid #bfdbfe; margin-bottom:12px; }}
</style>
</head>
<body>
  <h1>EduLive Pro — O‘quvchilar ma’lumoti</h1>
  <div class="meta">Jami o‘quvchi: <b>{len(rows)}</b></div>
  <table>
    <thead>
      <tr>
        <th>№</th><th>Ism</th><th>Familiya</th><th>To‘liq ism</th><th>Telefon</th><th>Email</th><th>Login</th><th>Registratsiya vaqti</th>
      </tr>
    </thead>
    <tbody>{''.join(tr)}</tbody>
  </table>
</body>
</html>"""
    resp = app.response_class(html, mimetype='application/vnd.ms-excel; charset=utf-8')
    resp.headers['Content-Disposition'] = 'attachment; filename=oquvchilar_malumoti_chiroyli.xls'
    return resp

@app.get('/api/admin/export/summary.csv')
@admin_required
def admin_export_summary():
    import csv
    from io import StringIO
    rows = list_results()
    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(['Ism familiya','Track','Daraja','Test','Togri','Jami','Foiz'])
    for item in rows:
        writer.writerow([item.get('student_name',''), item.get('track',''), item.get('level',''), item.get('test_title',''), item.get('score',0), item.get('total',0), item.get('percent',0)])
    resp = app.response_class(buf.getvalue(), mimetype='text/csv; charset=utf-8')
    resp.headers['Content-Disposition'] = 'attachment; filename=natijalar.csv'
    return resp



@app.get('/api/admin/export/monthly.xls')
@admin_required
def admin_export_monthly_excel():
    rows = list_students()
    cutoff = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff = cutoff.replace(day=1).isoformat()
    monthly = [item for item in rows if (item.get('created_at') or '') >= cutoff]
    table = html_table('Oxirgi oy foydalanuvchilari', 'Joriy oyda ro‘yxatdan o‘tgan o‘quvchilar.', ['№','Ism','Familiya','Telefon','Email','Registratsiya'], [[i+1, r.get('first_name',''), r.get('last_name',''), r.get('phone',''), r.get('email',''), r.get('created_at','')] for i,r in enumerate(monthly)])
    return excel_response('oylik_foydalanuvchilar.xls', table)


@app.get('/api/admin/export/daily.xls')
@admin_required
def admin_export_daily_excel():
    rows = list_students()
    today = datetime.utcnow().strftime('%Y-%m-%d')
    daily_students = [item for item in rows if (item.get('created_at') or '')[:10] == today]
    purchases = [item for item in admin_full_info_payload().get('purchases', []) if (item.get('unlocked_at') or '')[:10] == today]
    table1 = html_table('Kunlik o‘quvchilar', 'Bugun ro‘yxatdan o‘tgan o‘quvchilar.', ['№','Ism','Familiya','Telefon','Email','Registratsiya'], [[i+1, r.get('first_name',''), r.get('last_name',''), r.get('phone',''), r.get('email',''), r.get('created_at','')] for i,r in enumerate(daily_students)])
    table2 = html_table('Kunlik sotuvlar', 'Bugungi kurs ochish / sotib olishlar.', ['№','O‘quvchi','Telefon','Email','Kurs','Narx','Vaqt'], [[i+1, (r.get('first_name','')+' '+r.get('last_name','')).strip(), r.get('phone',''), r.get('email',''), r.get('course_title',''), r.get('price',''), r.get('unlocked_at','')] for i,r in enumerate(purchases)])
    return excel_response('kunlik_hisobot.xls', table1 + table2)


@app.get('/api/admin/export/yearly.xls')
@admin_required
def admin_export_yearly_excel():
    rows = list_students()
    current_year = datetime.utcnow().strftime('%Y')
    yearly_students = [item for item in rows if (item.get('created_at') or '')[:4] == current_year]
    purchases = [item for item in admin_full_info_payload().get('purchases', []) if (item.get('unlocked_at') or '')[:4] == current_year]
    table1 = html_table('Yillik o‘quvchilar', 'Joriy yilda ro‘yxatdan o‘tgan o‘quvchilar.', ['№','Ism','Familiya','Telefon','Email','Registratsiya'], [[i+1, r.get('first_name',''), r.get('last_name',''), r.get('phone',''), r.get('email',''), r.get('created_at','')] for i,r in enumerate(yearly_students)])
    table2 = html_table('Yillik sotuvlar', 'Joriy yildagi kurs ochish / sotib olishlar.', ['№','O‘quvchi','Telefon','Email','Kurs','Daraja','Yo‘nalish','Narx','Vaqt'], [[i+1, (r.get('first_name','')+' '+r.get('last_name','')).strip(), r.get('phone',''), r.get('email',''), r.get('course_title',''), r.get('level',''), r.get('track',''), r.get('price',''), r.get('unlocked_at','')] for i,r in enumerate(purchases)])
    return excel_response('yillik_hisobot.xls', table1 + table2)


@app.get('/api/admin/export/purchases.xls')
@admin_required
def admin_export_purchases_excel():
    purchases = admin_full_info_payload().get('purchases', [])
    table = html_table('Kurs sotib olishlar', 'O‘quvchilar ochgan / sotib olgan kurslar.', ['№','O‘quvchi','Telefon','Email','Kurs','Daraja','Yo‘nalish','Narx','Vaqt'], [[i+1, (r.get('first_name','')+' '+r.get('last_name','')).strip(), r.get('phone',''), r.get('email',''), r.get('course_title',''), r.get('level',''), r.get('track',''), r.get('price',''), r.get('unlocked_at','')] for i,r in enumerate(purchases)])
    return excel_response('kurs_sotib_olishlar.xls', table)


@app.get('/api/admin/export/all-info.xls')
@admin_required
def admin_export_all_info_excel():
    overview = admin_overview_summary()
    overview.update(admin_full_info_payload())
    students = list_students()
    purchases = overview.get('purchases', [])
    table1 = html_table('Umumiy statistika', 'Sayt bo‘yicha asosiy ko‘rsatkichlar.', ['Ko‘rsatkich','Qiymat'], [
        ['Jami o‘quvchi', overview.get('students_count',0)], ['Kunlik o‘quvchi', overview.get('daily_students_count',0)], ['Joriy oy o‘quvchi', overview.get('monthly_students_count',0)], ['Joriy yil o‘quvchi', overview.get('yearly_students_count',0)], ['Jami kurs', overview.get('courses_count',0)], ['Kurs sotib olishlar', overview.get('unlocked_count',0)], ['Kunlik sotuv', overview.get('daily_purchases_count',0)], ['Joriy oy sotuv', overview.get('monthly_purchases_count',0)], ['Joriy yil sotuv', overview.get('yearly_purchases_count',0)], ['Ustozlar', overview.get('teachers_count',0)], ['Test natijalari', overview.get('results_count',0)]
    ])
    table2 = html_table('O‘quvchilar', 'Registratsiya qilgan foydalanuvchilar.', ['№','Ism','Familiya','Telefon','Email','Login','Vaqt'], [[i+1, r.get('first_name',''), r.get('last_name',''), r.get('phone',''), r.get('email',''), r.get('username',''), r.get('created_at','')] for i,r in enumerate(students)])
    table3 = html_table('Kurs sotib olishlar', 'Ochilgan pullik kurslar.', ['№','O‘quvchi','Kurs','Daraja','Narx','Vaqt'], [[i+1, (r.get('first_name','')+' '+r.get('last_name','')).strip(), r.get('course_title',''), r.get('level',''), r.get('price',''), r.get('unlocked_at','')] for i,r in enumerate(purchases)])
    return excel_response('edulive_obshi_malumot.xls', table1 + table2 + table3)




def read_openai_env():
    """Load backend/.env on every AI request so changes are picked up after backend restart."""
    env_path = Path(__file__).resolve().parent / '.env'
    values = {}
    if env_path.exists():
        for line in env_path.read_text(encoding='utf-8', errors='ignore').splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                values[key] = value
                os.environ[key] = value
    return values


def openai_chat_answer(question, lang='uz', history=None):
    """Real OpenAI answer. No hard-coded if/fallback answers are used here."""
    read_openai_env()
    api_key = os.environ.get('OPENAI_API_KEY', '').strip()
    model_name = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini').strip() or 'gpt-4o-mini'

    if not api_key or api_key.startswith('sk-proj-PASTE') or 'YOUR_KEY_HERE' in api_key:
        raise RuntimeError('OPENAI_API_KEY topilmadi. backend/.env ichiga haqiqiy API kalit yozing.')

    lang_name = {
        'uz': 'o‘zbek tilida',
        'ru': 'на русском языке',
        'en': 'in English',
    }.get(lang, 'o‘zbek tilida')

    system_prompt = (
        f'Sen EduLive Pro saytidagi haqiqiy ChatGPT AI yordamchisisan. Har doim {lang_name} javob ber. '
        'Foydalanuvchi nimani so‘rasa, shunga mos ravishda aniq, foydali, tabiiy va to‘liq javob yoz. '
        'Hech qachon barcha savollarga bir xil javob qaytarma. Savol umumiy mavzu bo‘lsa ham, xuddi ChatGPT kabi tushuntir. '
        'Agar savol EduLive Pro haqida bo‘lsa, platformadagi bo‘limlar: kurslar, live darslar, testlar, natijalar, admin panel, ustoz panel, o‘quvchi panel va Excel hisobotlar haqida bosqichma-bosqich yordam ber. '
        'Javobni foydalanuvchi tushunadigan sodda tilda yoz, kerak bo‘lsa misol keltir.'
    )

    messages = [{'role': 'system', 'content': system_prompt}]
    if isinstance(history, list):
        # Only keep a few recent turns. Do not include generated local fallback texts.
        for item in history[-8:]:
            role = 'assistant' if item.get('role') == 'assistant' else 'user'
            text = (item.get('text') or '').strip()
            if not text:
                continue
            if 'OPENAI_API_KEY' in text or 'lokal' in text.lower() or 'fallback' in text.lower():
                continue
            messages.append({'role': role, 'content': text[:1200]})
    messages.append({'role': 'user', 'content': question})

    payload = {
        'model': model_name,
        'messages': messages,
        'temperature': 0.85,
        'max_tokens': 1600,
        'presence_penalty': 0.15,
        'frequency_penalty': 0.2,
    }

    req = Request(
        'https://api.openai.com/v1/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
        method='POST',
    )
    try:
        with urlopen(req, timeout=80) as resp:
            result = json.loads(resp.read().decode('utf-8'))
    except HTTPError as exc:
        body = exc.read().decode('utf-8', errors='ignore')[:500]
        if exc.code == 401:
            raise RuntimeError('OpenAI API kalit noto‘g‘ri yoki bekor qilingan. Yangi kalitni backend/.env ga yozing va backendni qayta yoqing.')
        raise RuntimeError(f'OpenAI HTTP xato {exc.code}: {body}')

    answer = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
    if not answer:
        raise RuntimeError('OpenAI javobi bo‘sh qaytdi.')
    return answer


def smart_local_ai_answer(question, lang='uz'):
    """Friendly backup answer shown only when OpenAI quota/key has a problem.
    It is not a replacement for real ChatGPT, but it prevents the site from showing raw errors to students.
    """
    q = (question or '').lower()
    is_ru = lang == 'ru'
    is_en = lang == 'en'

    if any(w in q for w in ['salom', 'assalom', 'hello', 'hi', 'привет', 'здравствуй']):
        if is_ru:
            return 'Привет! Чем могу помочь? Можете спросить про курсы, live-уроки, тесты, оплату, результаты или как пользоваться платформой EduLive Pro.'
        if is_en:
            return 'Hello! How can I help you? You can ask about courses, live classes, tests, payments, results, or how to use EduLive Pro.'
        return 'Salom! Qalesiz? Nima qilib beray? Kurslar, live dars, testlar, to‘lov, natijalar yoki platformadan foydalanish haqida bemalol savol bering.'

    if any(w in q for w in ['kurs', 'course', 'курс', 'dars', 'урок', 'lesson']):
        if is_ru:
            return 'Курсы в EduLive Pro отображаются в разделе «Курсы». Ученик выбирает нужное направление, смотрит описание, цену и уровень. Если курс платный, его нужно открыть/купить, после этого видео и материалы становятся доступными.'
        if is_en:
            return 'In EduLive Pro, courses are shown in the Courses section. A student selects a direction, checks the description, price, and level. If the course is paid, it must be unlocked before videos and materials become available.'
        return 'EduLive Pro’da kurslar “Kurslar” bo‘limida turadi. O‘quvchi kerakli yo‘nalishni tanlaydi, tavsif, narx va darajasini ko‘radi. Agar kurs pullik bo‘lsa, avval sotib olinadi yoki ochiladi, keyin video va materiallar ko‘rinadi.'

    if any(w in q for w in ['live', 'jonli', 'живо', 'онлайн', 'efir', 'эфир']):
        if is_ru:
            return 'Live-урок работает так: учитель запускает трансляцию, подключает экран и голос. Ученик видит уведомление, заходит в раздел live и подключается. Ученик только смотрит и слушает, говорить может только учитель.'
        if is_en:
            return 'Live class works like this: the teacher starts the live session, shares screen and voice. Students see a notification, open the live section, and join. Students only watch and listen; only the teacher speaks.'
        return 'Live dars ishlashi: ustoz live darsni yoqadi, ekran va ovozni ulaydi. O‘quvchi panelida “Live dars yoqildi” xabari chiqadi va o‘quvchi live bo‘limidan qo‘shiladi. O‘quvchi faqat ko‘radi va eshitadi, faqat ustoz gapiradi.'

    if any(w in q for w in ['test', 'тест', 'savol', 'савол', 'question', 'natija', 'результат', 'result']):
        if is_ru:
            return 'Тесты находятся в разделе «Тест». Ученик решает вопросы, после отправки результат попадает в систему. Учитель и админ могут смотреть результаты, проценты и баллы.'
        if is_en:
            return 'Tests are in the Test section. A student answers questions and submits them. Results are saved in the system, and teachers/admins can view scores and percentages.'
        return 'Testlar “Test” bo‘limida bo‘ladi. O‘quvchi savollarga javob beradi va yuboradi. Natija tizimda saqlanadi, ustoz yoki admin foiz, ball va natijalarni ko‘ra oladi.'

    if any(w in q for w in ['admin', 'ustoz', 'teacher', 'учитель', 'o‘qituvchi', 'oqituvchi']):
        if is_ru:
            return 'Админ может создавать и удалять учителей, видеть статистику, учеников, курсы и Excel-отчёты. Учитель создаёт курсы, тесты и проводит live-уроки.'
        if is_en:
            return 'The admin can create/delete teachers, view statistics, students, courses, and Excel reports. The teacher can create courses, tests, and run live lessons.'
        return 'Admin ustoz yaratadi/o‘chiradi, statistika, o‘quvchilar, kurslar va Excel hisobotlarni ko‘radi. Ustoz esa kurs yaratadi, test qo‘shadi va live dars o‘tadi.'

    if is_ru:
        return f'Вы спросили: “{question}”. Я могу помочь по платформе EduLive Pro. Уточните, пожалуйста: вас интересуют курсы, live-уроки, тесты, результаты, оплата или админ/учитель панель?'
    if is_en:
        return f'You asked: “{question}”. I can help with EduLive Pro. Please clarify whether you need help with courses, live lessons, tests, results, payment, or the admin/teacher panel.'
    return f'Siz “{question}” deb so‘radingiz. EduLive Pro bo‘yicha yordam beraman. Aniqroq ayting: kurslar, live dars, test, natija, to‘lov yoki admin/ustoz paneli haqida so‘rayapsizmi?'


@app.post('/api/student/ask')
@student_required
def student_ask_ai():
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    lang = (data.get('lang') or 'uz').strip().lower()
    if lang not in ('uz', 'ru', 'en'):
        lang = 'uz'
    if len(question) < 2:
        return error('Savol yozing.')

    try:
        answer = openai_chat_answer(question, lang, data.get('history') or [])
        return ok({'answer': answer, 'offline': False, 'source': 'openai'})
    except Exception as exc:
        # OpenAI API quota/key/internet muammosida foydalanuvchiga xom xatoni ko‘rsatmaymiz.
        # Agar API hisobida quota bo‘lsa, yuqoridagi haqiqiy OpenAI javobi ishlaydi.
        # Quota tugagan bo‘lsa ham chat oynasi ChatGPT uslubida foydali javob qaytaradi.
        answer = smart_local_ai_answer(question, lang)
        return ok({'answer': answer, 'offline': True, 'source': 'friendly_backup', 'api_error': str(exc)[:180]})


@app.get('/api/admin/students')
@teacher_required
def admin_students_list():
    return ok({'students': list_students_with_courses(), 'courses': list_courses()})


@app.post('/api/admin/students')
@teacher_required
def admin_students_create():
    data = request.get_json(silent=True) or {}
    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()
    phone_raw = (data.get('phone') or '').strip()
    email = (data.get('email') or '').strip().lower()
    username = (data.get('username') or '').strip().lower()
    password = (data.get('password') or '').strip()
    course_ids = data.get('course_ids') or []
    phone = normalize_phone(phone_raw) if phone_raw else ''

    if len(first_name) < 2 or len(last_name) < 2:
        return error('Ism va familiya kamida 2 ta harf bo‘lishi kerak.')
    if phone_raw and not phone:
        return error('Telefon raqami noto‘g‘ri.')
    if email and not is_valid_email(email):
        return error('Email manzil noto‘g‘ri.')
    if not re.fullmatch(r'[a-z0-9._-]{3,32}', username):
        return error('Login 3–32 ta lotin harfi, raqam, nuqta, chiziqcha yoki pastki chiziqdan iborat bo‘lsin.')
    if username in {ADMIN_LOGIN.lower(), TEACHER_LOGIN.lower()} or any((item.get('username') or '').lower() == username for item in list_teachers()):
        return error('Bu login band. Boshqa login tanlang.', 409)
    if len(password) < 6 or len(password) > 64:
        return error('Parol kamida 6 ta, ko‘pi bilan 64 ta belgidan iborat bo‘lsin.')

    try:
        student = create_student(
            first_name,
            last_name,
            phone,
            email,
            username,
            generate_password_hash(password),
        )
        set_student_courses(student['id'], course_ids)
        safe_student = {key: value for key, value in student.items() if key != 'password'}
        safe_student['course_ids'] = [int(item) for item in course_ids if str(item).isdigit()]
        return ok({'student': safe_student, 'message': 'O‘quvchi login va paroli yaratildi.'}, 201)
    except Exception as exc:
        if is_integrity_error(exc):
            return error('Bu login band.', 409)
        raise


@app.put('/api/admin/students/<int:student_id>')
@admin_required
def admin_students_update(student_id):
    data = request.get_json(silent=True) or {}
    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()
    phone_raw = (data.get('phone') or '').strip()
    email = (data.get('email') or '').strip().lower()
    username = (data.get('username') or '').strip().lower()
    password = (data.get('password') or '').strip()
    course_ids = data.get('course_ids') or []
    phone = normalize_phone(phone_raw) if phone_raw else ''

    if len(first_name) < 2 or len(last_name) < 2:
        return error('Ism va familiya to‘liq bo‘lishi kerak.')
    if phone_raw and not phone:
        return error('Telefon raqami noto‘g‘ri.')
    if email and not is_valid_email(email):
        return error('Email manzil noto‘g‘ri.')
    if not re.fullmatch(r'[a-z0-9._-]{3,32}', username):
        return error('Login formati noto‘g‘ri.')
    if username in {ADMIN_LOGIN.lower(), TEACHER_LOGIN.lower()} or any((item.get('username') or '').lower() == username for item in list_teachers()):
        return error('Bu login band. Boshqa login tanlang.', 409)
    if password and (len(password) < 6 or len(password) > 64):
        return error('Yangi parol kamida 6 ta belgidan iborat bo‘lsin.')

    try:
        updated = update_student_account(
            student_id,
            first_name,
            last_name,
            phone,
            email,
            username,
            generate_password_hash(password) if password else None,
        )
        if not updated:
            return error('O‘quvchi topilmadi.', 404)
        set_student_courses(student_id, course_ids)
        return ok({'student': updated, 'message': 'O‘quvchi ma’lumoti saqlandi.'})
    except Exception as exc:
        if is_integrity_error(exc):
            return error('Bu login band.', 409)
        raise


@app.put('/api/admin/students/<int:student_id>/courses')
@admin_required
def admin_students_courses(student_id):
    data = request.get_json(silent=True) or {}
    result = set_student_courses(student_id, data.get('course_ids') or [])
    if result is None:
        return error('O‘quvchi topilmadi.', 404)
    return ok({'course_ids': result, 'message': 'O‘quvchining kurslari saqlandi.'})


@app.delete('/api/admin/students/<int:student_id>')
@admin_required
def admin_students_delete(student_id):
    removed = delete_student(student_id)
    if not removed:
        return error('O‘quvchi topilmadi.', 404)
    if session.get('student_id') == student_id:
        session.pop('student_id', None)
    return ok({'student': removed, 'message': 'O‘quvchi o‘chirildi.'})


@app.get('/api/admin/teachers')
@teacher_required
def admin_teachers_list():
    teachers = [{key: value for key, value in teacher.items() if key != 'password'} for teacher in list_teachers()]
    return ok({'teachers': teachers})


@app.post('/api/admin/teachers')
@admin_required
def admin_teachers_create():
    data = request.get_json(silent=True) or {}
    full_name = (data.get('full_name') or '').strip()
    username = (data.get('username') or '').strip().lower()
    password = (data.get('password') or '').strip()
    if len(full_name) < 3 or len(username) < 3 or len(password) < 3:
        return error('Ism, login va parol to‘liq bo‘lishi kerak.')
    try:
        teacher = create_teacher(full_name, username, password)
        safe_teacher = {key: value for key, value in teacher.items() if key != 'password'}
        return ok({'teacher': safe_teacher, 'message': 'Yangi ustoz yaratildi.'}, 201)
    except Exception as exc:
        if is_integrity_error(exc):
            return error('Bu login band.', 409)
        raise


@app.delete('/api/admin/teachers/<int:teacher_id>')
@admin_required
def admin_teachers_delete(teacher_id):
    removed = delete_teacher(teacher_id)
    if not removed:
        return error('Ustoz topilmadi.', 404)
    if session.get('teacher_id') == teacher_id:
        session.pop('teacher_id', None)
        session.pop('is_teacher', None)
    return ok({'teacher': removed, 'message': 'Ustoz o‘chirildi.'})


@app.post('/api/admin/courses/create')
@teacher_required
def admin_courses_create():
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    track = (data.get('track') or 'frontend').strip().lower()
    technology = (data.get('technology') or '').strip()
    description = (data.get('description') or '').strip()
    duration = (data.get('duration') or '').strip()
    level = (data.get('level') or '').strip()
    price = data.get('price')
    if not title or not technology:
        return error('Kurs nomi va texnologiya kerak.')
    course = create_course(title, track, technology, description, duration, level, price)
    return ok({'course': course, 'message': 'Yangi kurs yaratildi.'}, 201)


if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', '5000')), allow_unsafe_werkzeug=True)
else:
    init_db()
