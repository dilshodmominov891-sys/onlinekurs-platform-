import json
import os
import re
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'platform.db')
DATABASE_URL = (os.environ.get('DATABASE_URL') or '').strip()
USE_POSTGRES = DATABASE_URL.startswith(('postgres://', 'postgresql://'))

DEMO_VIDEO = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'


class DBRow(dict):
    """PostgreSQL row that supports both row['id'] and row[0]."""

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


class StaticResult:
    def __init__(self, rows=None):
        self.rows = rows or []

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return self.rows


class PostgresResult:
    def __init__(self, cursor):
        self.cursor = cursor

    def _convert(self, row):
        if row is None:
            return None
        names = [col.name if hasattr(col, 'name') else col[0] for col in self.cursor.description]
        return DBRow(zip(names, row))

    def fetchone(self):
        return self._convert(self.cursor.fetchone())

    def fetchall(self):
        return [self._convert(row) for row in self.cursor.fetchall()]


class PostgresConnection:
    def __init__(self, raw):
        self.raw = raw
        self.lastrowid = None

    @staticmethod
    def _translate(sql):
        query = sql.strip()
        query = query.replace("datetime('now', '-7 day')", "CURRENT_TIMESTAMP - INTERVAL '7 days'")
        query = query.replace("datetime('now', '-30 day')", "CURRENT_TIMESTAMP - INTERVAL '30 days'")
        query = re.sub(
            r'INSERT\s+OR\s+IGNORE\s+INTO\s+unlocked_courses',
            'INSERT INTO unlocked_courses',
            query,
            flags=re.IGNORECASE,
        )
        if re.match(r'INSERT\s+INTO\s+unlocked_courses', query, flags=re.IGNORECASE):
            query += ' ON CONFLICT (student_id, course_id) DO NOTHING'
        return query.replace('?', '%s')

    def execute(self, sql, params=()):
        clean = sql.strip()
        if clean.upper().startswith('PRAGMA'):
            return StaticResult([])
        if clean.lower().startswith('select last_insert_rowid()'):
            return StaticResult([DBRow({'last_insert_rowid()': self.lastrowid})])

        query = self._translate(sql)
        cursor = self.raw.cursor()
        is_insert = bool(re.match(r'^\s*INSERT\s+INTO\s+', query, flags=re.IGNORECASE))
        if is_insert and ' RETURNING ' not in query.upper():
            query += ' RETURNING id'

        try:
            cursor.execute(query, tuple(params or ()))
            if is_insert and cursor.description:
                inserted = cursor.fetchone()
                self.lastrowid = inserted[0] if inserted else None
                return StaticResult([])
            return PostgresResult(cursor)
        except Exception:
            self.raw.rollback()
            cursor.close()
            raise

    def executemany(self, sql, seq_of_params):
        query = self._translate(sql)
        cursor = self.raw.cursor()
        try:
            cursor.executemany(query, seq_of_params)
            return StaticResult([])
        except Exception:
            self.raw.rollback()
            cursor.close()
            raise

    def commit(self):
        self.raw.commit()

    def rollback(self):
        self.raw.rollback()

    def close(self):
        self.raw.close()


def get_db():
    if USE_POSTGRES:
        import psycopg2

        url = DATABASE_URL
        if url.startswith('postgres://'):
            url = 'postgresql://' + url[len('postgres://'):]
        return PostgresConnection(psycopg2.connect(url))

    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=15000')
    return conn


def is_integrity_error(exc):
    if isinstance(exc, sqlite3.IntegrityError):
        return True
    try:
        import psycopg2

        return isinstance(exc, psycopg2.IntegrityError)
    except Exception:
        return False


def is_operational_error(exc):
    if isinstance(exc, sqlite3.OperationalError):
        return True
    try:
        import psycopg2

        return isinstance(exc, psycopg2.OperationalError)
    except Exception:
        return False


def row_to_dict(row):
    return dict(row) if row else None


def seed_courses(conn):
    count = conn.execute('SELECT COUNT(*) FROM courses').fetchone()[0]
    if count:
        return
    demo_courses = [
        ('frontend-html-css', 'HTML & CSS Boshlang‘ich', 'frontend', 'HTML & CSS', 'Frontend asoslari, layout, responsive dizayn, animatsiyalar.', '4 hafta', '1-bosqich', 'FRONT01'),
        ('frontend-js', 'JavaScript Praktikum', 'frontend', 'JavaScript', 'DOM, event, fetch, mini loyiha va real mashqlar.', '6 hafta', '2-bosqich', 'FRONT02'),
        ('frontend-vue', 'Vue 3 Pro Kurs', 'frontend', 'Vue', 'Composition API, router, component, admin panel va dashboard.', '8 hafta', '3-bosqich', 'VUE777'),
        ('frontend-react', 'React Start', 'frontend', 'React', 'Component, props, hooks, router va API bilan ishlash.', '8 hafta', '3-bosqich', 'REACT9'),
        ('backend-python', 'Python Backend Start', 'backend', 'Python', 'API, Flask/Django asoslari, auth, CRUD va deploy.', '6 hafta', '1-bosqich', 'BACK01'),
        ('backend-django', 'Django Full Backend', 'backend', 'Django', 'Model, view, auth, postgres, admin panel va REST.', '10 hafta', '2-bosqich', 'DJANGO8'),
        ('backend-postgres', 'PostgreSQL Mastery', 'backend', 'PostgreSQL', 'Jadval, relation, query, index va real project DB.', '5 hafta', '2-bosqich', 'DB2026'),
        ('backend-api', 'REST API & Security', 'backend', 'REST API', 'Token, CORS, permission, test va production tavsiyalar.', '5 hafta', '3-bosqich', 'API555'),
    ]
    conn.executemany(
        """INSERT INTO courses (slug, title, track, technology, description, duration, level, room_code, is_locked, purchase_password, price, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, '123445', 199000, ?)""",
        [(slug, title, track, technology, description, duration, level, room_code, datetime.utcnow().isoformat()) for slug, title, track, technology, description, duration, level, room_code in demo_courses],
    )


def seed_lessons(conn):
    count = conn.execute('SELECT COUNT(*) FROM course_lessons').fetchone()[0]
    if count:
        return
    course_rows = conn.execute('SELECT id, technology FROM courses ORDER BY id').fetchall()
    lesson_rows = []
    for idx, row in enumerate(course_rows, start=1):
        lesson_rows.append((
            row['id'],
            f"{row['technology']} kirish darsi",
            'Bu demo video. Ustoz admin paneldan istagan payt yangi MP4 link qo‘shishi mumkin.',
            DEMO_VIDEO,
            idx,
            0,
            datetime.utcnow().isoformat(),
        ))
    conn.executemany(
        """INSERT INTO course_lessons (course_id, title, summary, video_url, order_no, is_preview, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        lesson_rows,
    )


def ensure_column(conn, table_name, column_name, ddl):
    if USE_POSTGRES:
        exists = conn.execute(
            """SELECT 1 FROM information_schema.columns
               WHERE table_schema = 'public' AND table_name = ? AND column_name = ? LIMIT 1""",
            (table_name, column_name),
        ).fetchone()
        if not exists:
            conn.execute(f'ALTER TABLE {table_name} ADD COLUMN {ddl}')
        return
    cols = [row[1] for row in conn.execute(f'PRAGMA table_info({table_name})').fetchall()]
    if column_name not in cols:
        conn.execute(f'ALTER TABLE {table_name} ADD COLUMN {ddl}')


def init_db():
    conn = get_db()
    if not USE_POSTGRES:
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=15000')

    id_type = 'SERIAL PRIMARY KEY' if USE_POSTGRES else 'INTEGER PRIMARY KEY AUTOINCREMENT'
    created_type = 'TIMESTAMP NOT NULL' if USE_POSTGRES else 'TEXT NOT NULL'

    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS classes (
            id {id_type},
            title TEXT NOT NULL,
            room_code TEXT NOT NULL UNIQUE,
            description TEXT,
            is_live INTEGER DEFAULT 0,
            created_at {created_type}
        )
    """)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS tests (
            id {id_type},
            class_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            questions_json TEXT NOT NULL,
            created_at {created_type},
            FOREIGN KEY (class_id) REFERENCES classes(id)
        )
    """)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS test_results (
            id {id_type},
            test_id INTEGER NOT NULL,
            student_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            submitted_at {created_type},
            answers_json TEXT NOT NULL,
            FOREIGN KEY (test_id) REFERENCES tests(id)
        )
    """)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS students (
            id {id_type},
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at {created_type}
        )
    """)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS courses (
            id {id_type},
            slug TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            track TEXT NOT NULL,
            technology TEXT NOT NULL,
            description TEXT,
            duration TEXT,
            level TEXT,
            room_code TEXT,
            is_locked INTEGER DEFAULT 1,
            purchase_password TEXT DEFAULT '123445',
            price INTEGER DEFAULT 199000,
            is_live_class INTEGER DEFAULT 0,
            created_at {created_type}
        )
    """)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS unlocked_courses (
            id {id_type},
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            unlocked_at {created_type},
            UNIQUE(student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS course_lessons (
            id {id_type},
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            video_url TEXT NOT NULL,
            order_no INTEGER DEFAULT 1,
            is_preview INTEGER DEFAULT 0,
            created_at {created_type},
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS teachers (
            id {id_type},
            full_name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at {created_type}
        )
    """)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS live_join_events (
            id {id_type},
            class_id INTEGER NOT NULL,
            room_code TEXT NOT NULL,
            student_name TEXT NOT NULL,
            joined_at {created_type},
            FOREIGN KEY (class_id) REFERENCES classes(id)
        )
    """)
    ensure_column(conn, 'students', 'email', 'email TEXT')
    ensure_column(conn, 'courses', 'is_live_class', 'is_live_class INTEGER DEFAULT 0')
    seed_courses(conn)
    seed_lessons(conn)
    conn.commit()
    conn.close()

def list_classes():
    conn = get_db()
    rows = conn.execute('SELECT * FROM classes ORDER BY id DESC').fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_class_by_id(class_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM classes WHERE id = ?', (class_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


def get_class_by_room(room_code):
    conn = get_db()
    row = conn.execute('SELECT * FROM classes WHERE room_code = ?', (room_code.upper(),)).fetchone()
    conn.close()
    return row_to_dict(row)


def create_class(title, room_code, description=''):
    conn = get_db()
    conn.execute(
        'INSERT INTO classes (title, room_code, description, created_at) VALUES (?, ?, ?, ?)',
        (title, room_code.upper(), description, datetime.utcnow().isoformat())
    )
    conn.commit()
    class_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    row = conn.execute('SELECT * FROM classes WHERE id = ?', (class_id,)).fetchone()
    conn.close()
    return dict(row)


def set_live_status(class_id, is_live):
    conn = get_db()
    conn.execute('UPDATE classes SET is_live = ? WHERE id = ?', (1 if is_live else 0, class_id))
    conn.commit()
    row = conn.execute('SELECT * FROM classes WHERE id = ?', (class_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


def get_latest_test(class_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM tests WHERE class_id = ? ORDER BY id DESC LIMIT 1', (class_id,)).fetchone()
    conn.close()
    if row:
        data = dict(row)
        data['questions'] = json.loads(data['questions_json'])
        return data
    return None


def create_test(class_id, title, questions):
    conn = get_db()
    conn.execute(
        'INSERT INTO tests (class_id, title, questions_json, created_at) VALUES (?, ?, ?, ?)',
        (class_id, title, json.dumps(questions, ensure_ascii=False), datetime.utcnow().isoformat())
    )
    conn.commit()
    test_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    row = conn.execute('SELECT * FROM tests WHERE id = ?', (test_id,)).fetchone()
    conn.close()
    data = dict(row)
    data['questions'] = json.loads(data['questions_json'])
    return data


def get_test(test_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM tests WHERE id = ?', (test_id,)).fetchone()
    conn.close()
    if row:
        data = dict(row)
        data['questions'] = json.loads(data['questions_json'])
        return data
    return None


def save_test_result(test_id, student_name, score, total, answers):
    conn = get_db()
    conn.execute(
        'INSERT INTO test_results (test_id, student_name, score, total, submitted_at, answers_json) VALUES (?, ?, ?, ?, ?, ?)',
        (test_id, student_name, score, total, datetime.utcnow().isoformat(), json.dumps(answers, ensure_ascii=False))
    )
    conn.commit()
    result_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    row = conn.execute('SELECT * FROM test_results WHERE id = ?', (result_id,)).fetchone()
    conn.close()
    data = dict(row)
    data['answers'] = json.loads(data['answers_json'])
    return data


def list_results(track=None):
    conn = get_db()
    query = """
        SELECT tr.*, t.title AS test_title, c.title AS class_title,
               cr.track AS track, cr.level AS level, cr.technology AS technology
        FROM test_results tr
        JOIN tests t ON t.id = tr.test_id
        JOIN classes c ON c.id = t.class_id
        LEFT JOIN courses cr ON UPPER(cr.room_code) = UPPER(c.room_code)
        WHERE 1=1
    """
    params = []
    if track:
        query += ' AND cr.track = ?'
        params.append(track)
    query += ' ORDER BY tr.id DESC'
    rows = conn.execute(query, params).fetchall()
    conn.close()
    results = []
    for row in rows:
        item = dict(row)
        total = item.get('total') or 0
        score = item.get('score') or 0
        item['percent'] = round((score * 100.0) / total, 1) if total else 0
        item['wrong'] = max(total - score, 0)
        results.append(item)
    return results


def list_tests_for_practice(track=None, level=None):
    conn = get_db()
    query = """
        SELECT t.id, t.title, t.created_at, c.id as class_id, c.title as class_title, c.room_code,
               cr.track, cr.level, cr.technology, cr.title as course_title,
               (SELECT COUNT(*) FROM test_results tr WHERE tr.test_id = t.id) as attempts_count,
               (SELECT AVG((tr.score * 100.0) / NULLIF(tr.total, 0)) FROM test_results tr WHERE tr.test_id = t.id) as avg_percent
        FROM tests t
        JOIN classes c ON c.id = t.class_id
        LEFT JOIN courses cr ON UPPER(cr.room_code) = UPPER(c.room_code)
        WHERE 1=1
    """
    params = []
    if track:
        query += ' AND cr.track = ?'
        params.append(track)
    if level:
        query += ' AND cr.level = ?'
        params.append(level)
    query += ' ORDER BY t.id DESC'
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def summarize_test_results(test_id):
    conn = get_db()
    row = conn.execute("""
        SELECT COUNT(*) as attempts_count,
               COALESCE(SUM(score), 0) as total_correct,
               COALESCE(SUM(total), 0) as total_questions_answered,
               COALESCE(AVG((score * 100.0) / NULLIF(total, 0)), 0) as avg_percent,
               COALESCE(MAX(score), 0) as best_score
        FROM test_results
        WHERE test_id = ?
    """, (test_id,)).fetchone()
    conn.close()
    return dict(row) if row else {
        'attempts_count': 0, 'total_correct': 0, 'total_questions_answered': 0, 'avg_percent': 0, 'best_score': 0
    }


def create_student(first_name, last_name, phone, email, username, password):
    conn = get_db()
    conn.execute(
        'INSERT INTO students (first_name, last_name, phone, email, username, password, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (first_name, last_name, phone, email, username, password, datetime.utcnow().isoformat())
    )
    conn.commit()
    student_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    row = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    conn.close()
    return dict(row)



def list_students():
    conn = get_db()
    rows = conn.execute('''
        SELECT id, first_name, last_name, phone, email, username, created_at
        FROM students
        ORDER BY id DESC
    ''').fetchall()
    conn.close()
    return [dict(row) for row in rows]


def auth_student(username, password):
    conn = get_db()
    row = conn.execute(
        'SELECT * FROM students WHERE LOWER(username) = LOWER(?) AND password = ? LIMIT 1',
        (username, password)
    ).fetchone()
    conn.close()
    return row_to_dict(row)


def get_student_by_id(student_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


def find_student_by_contact(phone=None, email=None):
    conn = get_db()
    row = None
    if phone and email:
        row = conn.execute(
            'SELECT * FROM students WHERE phone = ? OR LOWER(email) = LOWER(?) ORDER BY id DESC LIMIT 1',
            (phone, email)
        ).fetchone()
    elif phone:
        row = conn.execute('SELECT * FROM students WHERE phone = ? ORDER BY id DESC LIMIT 1', (phone,)).fetchone()
    elif email:
        row = conn.execute('SELECT * FROM students WHERE LOWER(email) = LOWER(?) ORDER BY id DESC LIMIT 1', (email,)).fetchone()
    conn.close()
    return row_to_dict(row)


def _course_query(student_id=None):
    if student_id:
        return """
            SELECT c.*, CASE WHEN uc.id IS NULL THEN 0 ELSE 1 END AS is_unlocked
            FROM courses c
            LEFT JOIN unlocked_courses uc ON uc.course_id = c.id AND uc.student_id = ?
        """, [student_id]
    return """
        SELECT c.*, 0 AS is_unlocked
        FROM courses c
    """, []


def list_courses(student_id=None):
    conn = get_db()
    query, params = _course_query(student_id)
    rows = conn.execute(query + ' ORDER BY c.id ASC', params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_course_by_slug(slug, student_id=None):
    conn = get_db()
    query, params = _course_query(student_id)
    row = conn.execute(query + ' WHERE c.slug = ? LIMIT 1', [*params, slug]).fetchone()
    conn.close()
    return row_to_dict(row)


def get_course_by_id(course_id, student_id=None):
    conn = get_db()
    query, params = _course_query(student_id)
    row = conn.execute(query + ' WHERE c.id = ? LIMIT 1', [*params, course_id]).fetchone()
    conn.close()
    return row_to_dict(row)


def unlock_course(student_id, course_id):
    conn = get_db()
    conn.execute(
        'INSERT OR IGNORE INTO unlocked_courses (student_id, course_id, unlocked_at) VALUES (?, ?, ?)',
        (student_id, course_id, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def list_lessons_for_course(course_id, include_preview=False):
    conn = get_db()
    if include_preview:
        rows = conn.execute(
            'SELECT *, CASE WHEN is_preview = 1 THEN 0 ELSE 1 END AS is_locked FROM course_lessons WHERE course_id = ? ORDER BY order_no ASC, id ASC',
            (course_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            'SELECT *, 0 AS is_locked FROM course_lessons WHERE course_id = ? ORDER BY order_no ASC, id ASC',
            (course_id,)
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_lesson(lesson_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM course_lessons WHERE id = ?', (lesson_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


def create_lesson(course_id, title, summary, video_url, order_no=1, is_preview=0):
    conn = get_db()
    conn.execute(
        'INSERT INTO course_lessons (course_id, title, summary, video_url, order_no, is_preview, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (course_id, title, summary, video_url, order_no, 1 if is_preview else 0, datetime.utcnow().isoformat())
    )
    conn.commit()
    lesson_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    row = conn.execute('SELECT * FROM course_lessons WHERE id = ?', (lesson_id,)).fetchone()
    conn.close()
    return dict(row)


def _slugify(value):
    value = (value or '').strip().lower()
    value = ''.join(ch if ch.isalnum() else '-' for ch in value)
    value = '-'.join(part for part in value.split('-') if part)
    return value or f'course-{int(datetime.utcnow().timestamp())}'


def _unique_slug(conn, base_slug):
    slug = base_slug
    idx = 2
    while conn.execute('SELECT 1 FROM courses WHERE slug = ? LIMIT 1', (slug,)).fetchone():
        slug = f'{base_slug}-{idx}'
        idx += 1
    return slug


def create_course_from_live(base_course_id, title, summary, video_url, room_code=None, price=None, level=None):
    conn = get_db()
    base = conn.execute('SELECT * FROM courses WHERE id = ?', (base_course_id,)).fetchone()
    if not base:
        conn.close()
        return None
    base = dict(base)
    final_room = (room_code or base.get('room_code') or f'LIVE{base_course_id}').upper()
    slug = _unique_slug(conn, _slugify(title))
    clean_level = (level or base.get('level') or 'Live').strip() if isinstance(level or base.get('level') or 'Live', str) else 'Live'
    conn.execute(
        'INSERT INTO courses (slug, title, track, technology, description, duration, level, room_code, is_locked, purchase_password, price, is_live_class, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            slug,
            title,
            'live',
            clean_level or 'Live dars',
            summary or base.get('description') or '',
            base.get('duration') or '1 dars',
            clean_level,
            final_room,
            1,
            base.get('purchase_password') or '123445',
            int(price) if price is not None else (base.get('price') or 199000),
            1,
            datetime.utcnow().isoformat(),
        )
    )
    conn.commit()
    course_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.execute(
        'INSERT INTO course_lessons (course_id, title, summary, video_url, order_no, is_preview, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (course_id, title, summary or 'Live yozuv', video_url, 1, 0, datetime.utcnow().isoformat())
    )
    conn.commit()
    row = conn.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    conn.close()
    return dict(row)


def ensure_class_for_course(course_id):
    conn = get_db()
    course = conn.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    if not course:
        conn.close()
        return None
    course = dict(course)
    room_code = (course.get('room_code') or f'COURSE{course_id}').upper()
    existing = conn.execute('SELECT * FROM classes WHERE room_code = ? LIMIT 1', (room_code,)).fetchone()
    if existing:
        conn.close()
        return dict(existing)
    conn.execute(
        'INSERT INTO classes (title, room_code, description, created_at) VALUES (?, ?, ?, ?)',
        (course.get('title') or 'Practice class', room_code, course.get('description') or '', datetime.utcnow().isoformat())
    )
    conn.commit()
    class_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    row = conn.execute('SELECT * FROM classes WHERE id = ?', (class_id,)).fetchone()
    conn.close()
    return dict(row)


def create_course(title, track, technology, description='', duration='', level='', price=199000, purchase_password='123445'):
    conn = get_db()
    slug = _unique_slug(conn, _slugify(title))
    room_code = f"{(track or 'COURSE')[:5].upper()}{int(datetime.utcnow().timestamp()) % 100000}"
    conn.execute(
        'INSERT INTO courses (slug, title, track, technology, description, duration, level, room_code, is_locked, purchase_password, price, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            slug,
            title,
            (track or 'frontend').strip().lower(),
            technology or 'General',
            description or '',
            duration or '4 hafta',
            level or '1-bosqich',
            room_code,
            1,
            purchase_password or '123445',
            int(price) if str(price).strip() else 199000,
            datetime.utcnow().isoformat(),
        )
    )
    conn.commit()
    course_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    row = conn.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    conn.close()
    return dict(row)


def create_teacher(full_name, username, password):
    conn = get_db()
    conn.execute(
        'INSERT INTO teachers (full_name, username, password, created_at) VALUES (?, ?, ?, ?)',
        (full_name, username.strip().lower(), password, datetime.utcnow().isoformat())
    )
    conn.commit()
    teacher_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    row = conn.execute('SELECT * FROM teachers WHERE id = ?', (teacher_id,)).fetchone()
    conn.close()
    return dict(row)


def list_teachers():
    conn = get_db()
    rows = conn.execute('SELECT * FROM teachers ORDER BY id DESC').fetchall()
    conn.close()
    return [dict(row) for row in rows]


def auth_teacher(username, password):
    conn = get_db()
    row = conn.execute(
        'SELECT * FROM teachers WHERE LOWER(username) = LOWER(?) AND password = ? LIMIT 1',
        (username.strip().lower(), password)
    ).fetchone()
    conn.close()
    return row_to_dict(row)


def get_teacher_by_id(teacher_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM teachers WHERE id = ?', (teacher_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


def delete_teacher(teacher_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM teachers WHERE id = ?', (teacher_id,)).fetchone()
    if not row:
        conn.close()
        return None
    teacher = dict(row)
    conn.execute('DELETE FROM teachers WHERE id = ?', (teacher_id,))
    conn.commit()
    conn.close()
    return teacher


def log_live_join(class_id, room_code, student_name):
    conn = get_db()
    conn.execute(
        'INSERT INTO live_join_events (class_id, room_code, student_name, joined_at) VALUES (?, ?, ?, ?)',
        (class_id, room_code.upper(), student_name or 'Noma’lum', datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def live_stats_summary():
    conn = get_db()
    week_count = conn.execute("SELECT COUNT(*) FROM live_join_events WHERE joined_at >= datetime('now', '-7 day')").fetchone()[0]
    month_count = conn.execute("SELECT COUNT(*) FROM live_join_events WHERE joined_at >= datetime('now', '-30 day')").fetchone()[0]
    total_count = conn.execute('SELECT COUNT(*) FROM live_join_events').fetchone()[0]
    recent = conn.execute('SELECT * FROM live_join_events ORDER BY id DESC LIMIT 12').fetchall()
    by_room = conn.execute('''
        SELECT room_code, COUNT(*) as join_count, MAX(joined_at) as latest_join
        FROM live_join_events
        GROUP BY room_code
        ORDER BY join_count DESC, latest_join DESC
        LIMIT 10
    ''').fetchall()
    conn.close()
    return {
        'week_count': week_count,
        'month_count': month_count,
        'total_count': total_count,
        'recent': [dict(row) for row in recent],
        'by_room': [dict(row) for row in by_room],
    }


def admin_overview_summary():
    conn = get_db()
    students_count = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    teachers_count = conn.execute('SELECT COUNT(*) FROM teachers').fetchone()[0]
    courses_count = conn.execute('SELECT COUNT(*) FROM courses').fetchone()[0]
    unlocked_count = conn.execute('SELECT COUNT(*) FROM unlocked_courses').fetchone()[0]
    live_join_count = conn.execute('SELECT COUNT(*) FROM live_join_events').fetchone()[0]
    tests_count = conn.execute('SELECT COUNT(*) FROM tests').fetchone()[0]
    results_count = conn.execute('SELECT COUNT(*) FROM test_results').fetchone()[0]
    conn.close()
    return {
        'students_count': students_count,
        'teachers_count': teachers_count,
        'courses_count': courses_count,
        'unlocked_count': unlocked_count,
        'live_join_count': live_join_count,
        'tests_count': tests_count,
        'results_count': results_count,
    }
