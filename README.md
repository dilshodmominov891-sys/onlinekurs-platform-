# EduLive Pro

Vue 3 frontend + Flask/Socket.IO backend + PostgreSQL.

## Papkalar

- `frontend/` — Netlify uchun Vue/Vite frontend
- `backend/` — Railway uchun Flask backend
- `netlify.toml` — Netlify build va SPA redirect
- `backend/railway.toml` — Railway start/healthcheck

## Lokal ishga tushirish

### Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

`DATABASE_URL` berilmasa SQLite lokal demo baza ishlatiladi. Railway’da PostgreSQL `DATABASE_URL` avtomatik ishlatiladi.

### Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Lokal ishlashda `frontend/.env` ichidagi `VITE_API_URL` va `VITE_SOCKET_URL`ni bo‘sh qoldirish yoki `http://127.0.0.1:5000` qilish mumkin.

## Muhim xavfsizlik

- `.env`, `.db`, `node_modules` va yuklangan videolar GitHub’ga yuborilmaydi.
- Eski ZIP ichida bo‘lgan OpenAI/Telegram kalitlarini bekor qilib yangisini yarating.
- Railway Variables ichida kuchli `SECRET_KEY`, `ADMIN_PASSWORD`, `TEACHER_PASSWORD` va `LIVE_ROOM_PASSWORD` kiriting.

## Deploy tartibi

1. Repozitoriyni GitHub’ga push qiling.
2. Railway’da GitHub repo orqali backend service yarating va Root Directory sifatida `/backend` tanlang.
3. Railway loyihasiga PostgreSQL service qo‘shing.
4. Railway backend uchun public domain yarating.
5. Netlify’da GitHub repo import qiling; `netlify.toml` build sozlamalarni oladi.
6. Netlify Variables ichida `VITE_API_URL` va `VITE_SOCKET_URL`ga Railway domainini yozing.
7. Railway `CORS_ORIGINS`ga Netlify domenini yozib backendni qayta deploy qiling.

## Upload eslatmasi

Railway service fayl tizimi doimiy saqlash uchun kafolatlanmaydi. Live video yozuvlarini uzoq muddat saqlash uchun Railway Volume yoki Cloudinary/S3 turidagi tashqi storage kerak.
