# 0 dan deploy: GitHub → Railway + PostgreSQL → Netlify

## 1. Kerakli akkauntlar

- GitHub
- Railway
- Netlify
- Kompyuterda Git va Node.js 20+

## 2. Eski maxfiy kalitlarni almashtiring

Eski ZIP ichida OpenAI API kaliti va Telegram bot tokeni bo‘lgan. Ularni eski deb hisoblang:

- OpenAI kalitini o‘chirib, yangi kalit yarating.
- BotFather orqali Telegram bot tokenini yangilang.
- Yangi kalitlarni GitHub fayllariga yozmang. Ular faqat Railway Variables ichida turadi.

## 3. GitHub repository yaratish

GitHub saytida:

1. `New repository` ni bosing.
2. Repository nomi: masalan, `edulive-pro`.
3. Public yoki Private tanlang.
4. `Add a README`, `.gitignore`, `license` variantlarini belgilamang.
5. `Create repository` ni bosing.

ZIP’ni oching va loyiha ildizida Git Bash yoki terminal oching:

```bash
git init -b main
git add .
git commit -m "Initial production deploy"
git remote add origin https://github.com/GITHUB_USERNAME/edulive-pro.git
git push -u origin main
```

`GITHUB_USERNAME`ni o‘z GitHub nomingizga almashtiring.

Tekshirish:

```bash
git status
git remote -v
```

GitHub’da quyidagilar chiqmasligi kerak:

- `backend/.env`
- `backend/platform.db`
- `backend/uploads/*.webm`
- `frontend/node_modules`

## 4. Railway’da backend yaratish

1. Railway dashboard → `New Project`.
2. `Deploy from GitHub repo`.
3. GitHub repositoryni tanlang.
4. Backend service yaratilgach, service → `Settings`.
5. `Root Directory` qiymatini `/backend` qiling.
6. Deployni qayta ishga tushiring.

Loyihada Railway uchun tayyor start command bor:

```text
gunicorn -w 1 --threads 100 -b 0.0.0.0:$PORT app:app
```

## 5. Railway PostgreSQL qo‘shish

Railway loyiha canvasida:

1. `+ New`.
2. `Database`.
3. `PostgreSQL`.
4. PostgreSQL service tayyor bo‘lishini kuting.
5. Backend service → `Variables`.
6. `DATABASE_URL` variable qo‘shing.
7. Qiymati PostgreSQL service reference bo‘lsin:

```text
${{Postgres.DATABASE_URL}}
```

PostgreSQL service nomi boshqacha bo‘lsa, `Postgres` o‘rniga aynan o‘sha service nomini yozing. Railway UI’dagi `Add Reference` tugmasi orqali tanlash xavfsizroq.

Backend `DATABASE_URL` topilsa PostgreSQL ishlatadi; lokal kompyuterda bu variable bo‘lmasa SQLite demo baza ishlaydi.

## 6. Railway Variables

Backend service → `Variables` ichiga quyidagilarni kiriting:

```env
SECRET_KEY=JUDA_UZUN_RANDOM_QIYMAT
ADMIN_LOGIN=admin
ADMIN_PASSWORD=KUCHLI_ADMIN_PAROL
TEACHER_LOGIN=teacher
TEACHER_PASSWORD=KUCHLI_USTOZ_PAROL
LIVE_ROOM_PASSWORD=KUCHLI_LIVE_PAROL
COOKIE_SECURE=1
COOKIE_SAMESITE=None
CORS_ORIGINS=http://localhost:5173
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TELEGRAM_LINK=https://t.me/YOUR_USERNAME
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
MAX_UPLOAD_MB=300
```

Random `SECRET_KEY` olish uchun kompyuter terminalida:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Variable o‘zgarishlarini deploy qiling.

## 7. Railway public domain

1. Backend service → `Settings` yoki `Networking`.
2. `Generate Domain` ni bosing.
3. Masalan, shunday URL chiqadi:

```text
https://edulive-production.up.railway.app
```

Tekshirish:

```text
https://SIZNING-RAILWAY-DOMENINGIZ/api/health
```

Javobda `"ok": true` chiqishi kerak.

## 8. Netlify’da frontend yaratish

1. Netlify dashboard → `Add new project`.
2. `Import an existing project`.
3. GitHub’ni tanlang.
4. `edulive-pro` repositoryni tanlang.
5. Loyiha ildizidagi `netlify.toml` sozlamalarni avtomatik beradi.

Tekshiriladigan build qiymatlari:

```text
Base directory: frontend
Build command: npm ci && npm run build
Publish directory: frontend/dist
```

## 9. Netlify environment variables

Netlify → Project configuration → Environment variables:

```env
VITE_API_URL=https://SIZNING-BACKEND-DOMENINGIZ.up.railway.app
VITE_SOCKET_URL=https://SIZNING-BACKEND-DOMENINGIZ.up.railway.app
```

Oxirida `/` qo‘ymang.

Variable qo‘shilgach yangi deploy qiling.

## 10. Railway CORS’ni Netlify domeniga ulash

Netlify sizga masalan quyidagi domenni beradi:

```text
https://edulive-pro.netlify.app
```

Railway backend → Variables → `CORS_ORIGINS`ni o‘zgartiring:

```env
CORS_ORIGINS=https://edulive-pro.netlify.app,http://localhost:5173
```

Bir nechta domen vergul bilan ajratiladi. Oxirida `/` qo‘ymang. Railway backendni qayta deploy qiling.

## 11. Yakuniy tekshiruv

1. Netlify saytini oching.
2. Registratsiya qiling.
3. Admin loginni tekshiring.
4. Kurslar chiqishini tekshiring.
5. Railway PostgreSQL service → Data bo‘limida jadvallar va yozuvlar paydo bo‘lishini tekshiring.
6. Live dars va Socket.IO ulanishini tekshiring.
7. Brauzer DevTools → Network’da API xatolari yo‘qligini tekshiring.

## 12. Keyingi o‘zgarishlarni chiqarish

Kodga o‘zgarish kiritgandan keyin:

```bash
git add .
git commit -m "Update project"
git push
```

GitHub push bo‘lgach Railway va Netlify avtomatik qayta deploy qiladi.

## Muhim cheklovlar

- Railway Free rejasi cheklangan resurs krediti beradi. Backend va PostgreSQL birga limitdan oshishi mumkin.
- Railway service ichidagi oddiy fayllar doimiy storage emas. Live video yozuvlari redeploydan keyin yo‘qolishi mumkin.
- Video uchun Railway Volume yoki Cloudinary/S3 kabi tashqi storage ishlatish kerak.
- Netlify frontend static hosting uchun mos; PostgreSQL faqat Railway backendga ulanadi.
- GitHub’ga hech qachon `.env`, API key, bot token yoki haqiqiy parol yubormang.
