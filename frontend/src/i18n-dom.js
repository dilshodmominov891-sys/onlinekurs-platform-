// Lightweight DOM translator for EduLive Pro.
// It translates all visible static texts after every route change and after dynamic data is rendered.
const T = {
  'Ochiq': { uz:'Ochiq', ru:'Открыт', en:'Open' },
  'Yopiq': { uz:'Yopiq', ru:'Закрыт', en:'Closed' },
  'Ko‘rish': { uz:'Ko‘rish', ru:'Открыть', en:'Open' },
  // General / navigation
  'Online kurs platforma': { uz:'Online kurs platforma', ru:'Онлайн-платформа курсов', en:'Online course platform' },
  'Home': { uz:'Home', ru:'Главная', en:'Home' },
  'Bosh sahifa': { uz:'Bosh sahifa', ru:'Главная страница', en:'Home page' },
  'Admin qismi': { uz:'Admin qismi', ru:'Админ панель', en:'Admin panel' },
  'Barcha nazorat': { uz:'Barcha nazorat', ru:'Весь контроль', en:'Full control' },
  'Barcha nazorat va ustoz yaratish': { uz:'Barcha nazorat va ustoz yaratish', ru:'Контроль и создание учителей', en:'Control and teacher creation' },
  'Ustoz bo‘limi': { uz:'Ustoz bo‘limi', ru:'Раздел учителя', en:'Teacher section' },
  'Kurs, live va testlar': { uz:'Kurs, live va testlar', ru:'Курсы, live и тесты', en:'Courses, live and tests' },
  'Ustoz yaratish': { uz:'Ustoz yaratish', ru:'Создать учителя', en:'Create teacher' },
  'Yangi ustoz login': { uz:'Yangi ustoz login', ru:'Новый логин учителя', en:'New teacher login' },
  'Ma’lumot': { uz:'Ma’lumot', ru:'Информация', en:'Info' },
  'Sayt statistikasi': { uz:'Sayt statistikasi', ru:'Статистика сайта', en:'Site statistics' },
  'Kurslar': { uz:'Kurslar', ru:'Курсы', en:'Courses' },
  'Barcha pullik kurslar': { uz:'Barcha pullik kurslar', ru:'Все платные курсы', en:'All paid courses' },
  'Kurs yaratish': { uz:'Kurs yaratish', ru:'Создать курс', en:'Create course' },
  'Yangi pullik kurs': { uz:'Yangi pullik kurs', ru:'Новый платный курс', en:'New paid course' },
  'Test qo‘shish': { uz:'Test qo‘shish', ru:'Добавить тест', en:'Add test' },
  'Frontend va backend': { uz:'Frontend va backend', ru:'Frontend и backend', en:'Frontend and backend' },
  'Natijalar': { uz:'Natijalar', ru:'Результаты', en:'Results' },
  'Foiz va yechimlar': { uz:'Foiz va yechimlar', ru:'Проценты и решения', en:'Scores and solutions' },
  'Live dars': { uz:'Live dars', ru:'Live урок', en:'Live class' },
  'Ekran yozish va dars o‘tish': { uz:'Ekran yozish va dars o‘tish', ru:'Запись экрана и урок', en:'Screen record and teach' },
  'Live darslar': { uz:'Live darslar', ru:'Live уроки', en:'Live classes' },
  'Live kurslar': { uz:'Live kurslar', ru:'Live курсы', en:'Live courses' },
  'Video yozuv kurslari': { uz:'Video yozuv kurslari', ru:'Видеозаписи курсов', en:'Recorded video courses' },
  'Video-yozuvlar': { uz:'Video-yozuvlar', ru:'Видеозаписи', en:'Video recordings' },
  'Test yechish': { uz:'Test yechish', ru:'Решать тест', en:'Take test' },
  'O‘quvchi testi': { uz:'O‘quvchi testi', ru:'Тест ученика', en:'Student test' },
  'Test o‘quvchi': { uz:'Test o‘quvchi', ru:'Тест ученика', en:'Student test' },
  'Savollar': { uz:'Savollar', ru:'Вопросы', en:'Questions' },
  'AI yordamchi': { uz:'AI yordamchi', ru:'AI помощник', en:'AI assistant' },
  'Telegram': { uz:'Telegram', ru:'Telegram', en:'Telegram' },
  'Chiqish': { uz:'Chiqish', ru:'Выход', en:'Logout' },
  'Bosh ustoz': { uz:'Bosh ustoz', ru:'Главный учитель', en:'Head teacher' },
  'Menyuni ochish': { uz:'Menyuni ochish', ru:'Открыть меню', en:'Open menu' },

  // Home
  'Ishonchli online ta’lim': { uz:'Ishonchli online ta’lim', ru:'Надёжное онлайн-обучение', en:'Trusted online learning' },
  'EduLive Pro platformasiga xush kelibsiz': { uz:'EduLive Pro platformasiga xush kelibsiz', ru:'Добро пожаловать в EduLive Pro', en:'Welcome to EduLive Pro' },
  'Birinchi bo‘lib home sahifa ochiladi. Shu yerdan kurs yaratish, test qo‘shish, ustoz yaratish va live statistikani boshqarasiz.': { uz:'Birinchi bo‘lib home sahifa ochiladi. Shu yerdan kurs yaratish, test qo‘shish, ustoz yaratish va live statistikani boshqarasiz.', ru:'Сначала открывается главная страница. Здесь можно управлять курсами, тестами, созданием учителей и live-статистикой.', en:'The home page opens first. From here you manage courses, tests, teacher creation and live statistics.' },
  'Bu platformada o‘quvchilar registratsiya qiladi, pullik kurslarga kiradi, live dars yozuvlarini ko‘radi va frontend yoki backend bo‘yicha test yechadi.': { uz:'Bu platformada o‘quvchilar registratsiya qiladi, pullik kurslarga kiradi, live dars yozuvlarini ko‘radi va frontend yoki backend bo‘yicha test yechadi.', ru:'На этой платформе ученики регистрируются, открывают платные курсы, смотрят записи live-уроков и проходят тесты по frontend или backend.', en:'On this platform students register, access paid courses, watch live class recordings and take frontend or backend tests.' },
  'Kurslarni ko‘rish': { uz:'Kurslarni ko‘rish', ru:'Смотреть курсы', en:'View courses' },
  'Yangi frontend yoki backend kurs qo‘shish': { uz:'Yangi frontend yoki backend kurs qo‘shish', ru:'Добавить новый frontend или backend курс', en:'Add a new frontend or backend course' },
  'Test boshqaruvi': { uz:'Test boshqaruvi', ru:'Управление тестами', en:'Test management' },
  'Daraja bo‘yicha Excel testlarni saqlash': { uz:'Daraja bo‘yicha Excel testlarni saqlash', ru:'Сохранение Excel-тестов по уровню', en:'Save Excel tests by level' },
  'Live statistika': { uz:'Live statistika', ru:'Live статистика', en:'Live statistics' },
  '7 kun va 30 kun davomida kirganlar soni': { uz:'7 kun va 30 kun davomida kirganlar soni', ru:'Количество входов за 7 и 30 дней', en:'Entries for 7 and 30 days' },
  'Admin nazorati': { uz:'Admin nazorati', ru:'Контроль админа', en:'Admin control' },
  'Tushum, o‘quvchi, kurs va ustoz faoliyati': { uz:'Tushum, o‘quvchi, kurs va ustoz faoliyati', ru:'Доход, ученики, курсы и активность учителей', en:'Revenue, students, courses and teacher activity' },
  'Frontend va backend bo‘yicha pullik yo‘nalishlar': { uz:'Frontend va backend bo‘yicha pullik yo‘nalishlar', ru:'Платные направления по frontend и backend', en:'Paid frontend and backend tracks' },
  'Daraja va yo‘nalish bo‘yicha testlarni ishlash': { uz:'Daraja va yo‘nalish bo‘yicha testlarni ishlash', ru:'Прохождение тестов по уровню и направлению', en:'Take tests by level and track' },
  'Live yozuv kurslari alohida bo‘limda saqlanadi': { uz:'Live yozuv kurslari alohida bo‘limda saqlanadi', ru:'Записи live-уроков сохраняются в отдельном разделе', en:'Live recordings are saved in a separate section' },
  'Ustoz natijalarni foiz, ball va yo‘nalish bo‘yicha ko‘radi': { uz:'Ustoz natijalarni foiz, ball va yo‘nalish bo‘yicha ko‘radi', ru:'Учитель видит результаты по процентам, баллам и направлению', en:'Teacher sees results by percent, score and track' },
  'Tezkor ko‘rsatkichlar': { uz:'Tezkor ko‘rsatkichlar', ru:'Быстрые показатели', en:'Quick metrics' },
  '7 kun': { uz:'7 kun', ru:'7 дней', en:'7 days' },
  '30 kun': { uz:'30 kun', ru:'30 дней', en:'30 days' },
  'Jami': { uz:'Jami', ru:'Всего', en:'Total' },
  'Jonli darsga kirishlar': { uz:'Jonli darsga kirishlar', ru:'Входы на live-урок', en:'Live class entries' },
  'Barcha kirishlar': { uz:'Barcha kirishlar', ru:'Все входы', en:'All entries' },
  'Aktiv live': { uz:'Aktiv live', ru:'Активный live', en:'Active live' },
  'Hozir ochiq darslar': { uz:'Hozir ochiq darslar', ru:'Сейчас открытые уроки', en:'Currently open classes' },
  'Platforma haqida': { uz:'Platforma haqida', ru:'О платформе', en:'About the platform' },
  'Bu home sahifadan ustoz ham, o‘quvchi ham chiroyli ko‘rinishda ish boshlaydi. Har bir bo‘lim hover animatsiya va yumshoq loading bilan ishlaydi.': { uz:'Bu home sahifadan ustoz ham, o‘quvchi ham chiroyli ko‘rinishda ish boshlaydi. Har bir bo‘lim hover animatsiya va yumshoq loading bilan ishlaydi.', ru:'На главной странице учитель и ученик начинают работу в красивом интерфейсе. Каждый раздел работает с hover-анимацией и плавной загрузкой.', en:'From the home page, teachers and students start in a clean interface. Every section has hover animation and smooth loading.' },
  'EduLive Pro — o‘quv markaz va kurs tizimiga mos zamonaviy platforma. Har bir bo‘lim hover animatsiya, yumshoq o‘tish va chiroyli bloklar bilan tayyorlangan.': { uz:'EduLive Pro — o‘quv markaz va kurs tizimiga mos zamonaviy platforma. Har bir bo‘lim hover animatsiya, yumshoq o‘tish va chiroyli bloklar bilan tayyorlangan.', ru:'EduLive Pro — современная платформа для учебного центра и системы курсов. Каждый раздел оформлен с hover-анимацией, плавными переходами и красивыми блоками.', en:'EduLive Pro is a modern platform for learning centers and course systems. Each section is built with hover animation, smooth transitions and beautiful blocks.' },
  'Kodlash': { uz:'Kodlash', ru:'Кодинг', en:'Coding' },
  'Natija': { uz:'Natija', ru:'Результат', en:'Result' },
  'Qisqacha ishlash tartibi': { uz:'Qisqacha ishlash tartibi', ru:'Краткий порядок работы', en:'Short workflow' },
  'O‘quvchi registratsiya qiladi va tizimga kiradi.': { uz:'O‘quvchi registratsiya qiladi va tizimga kiradi.', ru:'Ученик регистрируется и входит в систему.', en:'The student registers and logs in.' },
  'Ustoz testlarni o‘z bo‘limidan frontend yoki backend yo‘nalishiga qo‘shadi.': { uz:'Ustoz testlarni o‘z bo‘limidan frontend yoki backend yo‘nalishiga qo‘shadi.', ru:'Учитель добавляет тесты в разделе frontend или backend.', en:'The teacher adds tests to frontend or backend tracks.' },
  'O‘quvchi testni yechadi, natijalar ustoz bo‘limiga tushadi.': { uz:'O‘quvchi testni yechadi, natijalar ustoz bo‘limiga tushadi.', ru:'Ученик решает тест, результаты попадают в раздел учителя.', en:'The student takes the test and results go to the teacher section.' },
  'Live yozuvlar alohida pullik bo‘limga saqlanadi.': { uz:'Live yozuvlar alohida pullik bo‘limga saqlanadi.', ru:'Live-записи сохраняются в отдельный платный раздел.', en:'Live recordings are saved to a separate paid section.' },
  'Yangi live yozuv kurslari': { uz:'Yangi live yozuv kurslari', ru:'Новые курсы с live-записями', en:'New live recording courses' },
  'Live olib qo‘yilgan va pullik tarzda ochiladigan kurslar': { uz:'Live olib qo‘yilgan va pullik tarzda ochiladigan kurslar', ru:'Записанные live-курсы, открываемые платно', en:'Recorded live courses unlocked as paid courses' },
  'Hammasini ko‘rish': { uz:'Hammasini ko‘rish', ru:'Смотреть все', en:'View all' },
  'Ustoz boshqaruv markazi': { uz:'Ustoz boshqaruv markazi', ru:'Центр управления учителя', en:'Teacher control center' },
  'Kurs yarating, test qo‘shing, natijalarni ko‘ring va live kirish statistikani tahlil qiling.': { uz:'Kurs yarating, test qo‘shing, natijalarni ko‘ring va live kirish statistikani tahlil qiling.', ru:'Создавайте курсы, добавляйте тесты, смотрите результаты и анализируйте live-статистику.', en:'Create courses, add tests, view results and analyze live statistics.' },
  'Faqat ustozlar': { uz:'Faqat ustozlar', ru:'Только учителя', en:'Teachers only' },
  'Frontend/backend kurslarini qo‘shish': { uz:'Frontend/backend kurslarini qo‘shish', ru:'Добавление frontend/backend курсов', en:'Add frontend/backend courses' },
  'Excel testni yo‘nalish va darajaga biriktirish': { uz:'Excel testni yo‘nalish va darajaga biriktirish', ru:'Привязать Excel-тест к направлению и уровню', en:'Attach Excel test to track and level' },
  'Ism, familiya, to‘g‘ri soni va foizi': { uz:'Ism, familiya, to‘g‘ri soni va foizi', ru:'Имя, фамилия, правильные ответы и процент', en:'Name, correct count and percent' },
  'Bir hafta va bir oy bo‘yicha kirishlar': { uz:'Bir hafta va bir oy bo‘yicha kirishlar', ru:'Входы за неделю и месяц', en:'Entries by week and month' },
  'Ustoz yaratish va barcha nazorat shu yerda': { uz:'Ustoz yaratish va barcha nazorat shu yerda', ru:'Создание учителей и весь контроль здесь', en:'Teacher creation and full control here' },

  // Courses
  'Kurslar bo‘limi': { uz:'Kurslar bo‘limi', ru:'Раздел курсов', en:'Courses section' },
  'Sotuvdagi barcha kurslar quyida joylashgan': { uz:'Sotuvdagi barcha kurslar quyida joylashgan', ru:'Все курсы в продаже расположены ниже', en:'All courses for sale are listed below' },
  'Barcha kurslar': { uz:'Barcha kurslar', ru:'Все курсы', en:'All courses' },
  'Frontend yo‘nalishlari': { uz:'Frontend yo‘nalishlari', ru:'Frontend направления', en:'Frontend tracks' },
  'Backend yo‘nalishlari': { uz:'Backend yo‘nalishlari', ru:'Backend направления', en:'Backend tracks' },
  'Python, Django, PostgreSQL, REST API': { uz:'Python, Django, PostgreSQL, REST API', ru:'Python, Django, PostgreSQL, REST API', en:'Python, Django, PostgreSQL, REST API' },
  'Kurslar vaqtincha backenddan kelmadi. Shu sabab ko‘rinish buzilmasligi uchun tayyor demo kurslar chiqarildi.': { uz:'Kurslar vaqtincha backenddan kelmadi. Shu sabab ko‘rinish buzilmasligi uchun tayyor demo kurslar chiqarildi.', ru:'Курсы временно не пришли с backend. Поэтому для сохранения вида показаны demo-курсы.', en:'Courses temporarily did not load from backend, so demo courses are shown to keep the layout.' },
  'Sotib olish': { uz:'Sotib olish', ru:'Купить', en:'Buy' },
  'Kirish': { uz:'Kirish', ru:'Войти', en:'Enter' },
  'Live yozuvni ko‘rish': { uz:'Live yozuvni ko‘rish', ru:'Смотреть live-запись', en:'Watch live recording' },
  'HTML & CSS Boshlang‘ich': { uz:'HTML & CSS Boshlang‘ich', ru:'HTML & CSS начальный', en:'HTML & CSS beginner' },
  'JavaScript Praktikum': { uz:'JavaScript Praktikum', ru:'JavaScript практикум', en:'JavaScript practicum' },
  'Vue 3 Pro Kurs': { uz:'Vue 3 Pro Kurs', ru:'Vue 3 Pro курс', en:'Vue 3 Pro course' },
  'Python Backend Start': { uz:'Python Backend Start', ru:'Python Backend старт', en:'Python Backend Start' },
  'Django Full Backend': { uz:'Django Full Backend', ru:'Django Full Backend', en:'Django Full Backend' },
  'REST API & Security': { uz:'REST API & Security', ru:'REST API и безопасность', en:'REST API & Security' },
  'Frontend asoslari, layout, responsive dizayn va amaliy mashqlar.': { uz:'Frontend asoslari, layout, responsive dizayn va amaliy mashqlar.', ru:'Основы frontend, layout, responsive-дизайн и практические задания.', en:'Frontend basics, layout, responsive design and practical exercises.' },
  'DOM, event, fetch, mini loyiha va real amaliyot.': { uz:'DOM, event, fetch, mini loyiha va real amaliyot.', ru:'DOM, events, fetch, мини-проект и реальная практика.', en:'DOM, events, fetch, mini project and real practice.' },
  'Composition API, router, component va dashboardlar.': { uz:'Composition API, router, component va dashboardlar.', ru:'Composition API, router, компоненты и dashboard.', en:'Composition API, router, components and dashboards.' },
  'API, auth, CRUD va backend asoslari.': { uz:'API, auth, CRUD va backend asoslari.', ru:'API, auth, CRUD и основы backend.', en:'API, auth, CRUD and backend basics.' },
  'Model, view, auth, postgres va productionga tayyorlash.': { uz:'Model, view, auth, postgres va productionga tayyorlash.', ru:'Model, view, auth, postgres и подготовка к production.', en:'Model, view, auth, postgres and production preparation.' },
  'Token, permission, test va xavfsizlik qoidalari.': { uz:'Token, permission, test va xavfsizlik qoidalari.', ru:'Token, permission, тесты и правила безопасности.', en:'Tokens, permissions, tests and security rules.' },
  '1-bosqich': { uz:'1-bosqich', ru:'1-этап', en:'Stage 1' },
  '2-bosqich': { uz:'2-bosqich', ru:'2-этап', en:'Stage 2' },
  '3-bosqich': { uz:'3-bosqich', ru:'3-этап', en:'Stage 3' },
  '4 hafta': { uz:'4 hafta', ru:'4 недели', en:'4 weeks' },
  '5 hafta': { uz:'5 hafta', ru:'5 недель', en:'5 weeks' },
  '6 hafta': { uz:'6 hafta', ru:'6 недель', en:'6 weeks' },
  '8 hafta': { uz:'8 hafta', ru:'8 недель', en:'8 weeks' },
  '10 hafta': { uz:'10 hafta', ru:'10 недель', en:'10 weeks' },
  'hafta': { uz:'hafta', ru:'недель', en:'weeks' },
  'so‘m': { uz:'so‘m', ru:'сум', en:'UZS' },
  'ta online': { uz:'ta online', ru:'онлайн', en:'online' },

  // Admin
  'Admin panel': { uz:'Admin panel', ru:'Админ панель', en:'Admin panel' },
  'Admin nazorat markazi': { uz:'Admin nazorat markazi', ru:'Центр контроля админа', en:'Admin control center' },
  'Bu bo‘limda faqat umumiy nazorat cardlari turadi. Ustoz yaratish va ma’lumotlar alohida bo‘limlarga ajratildi.': { uz:'Bu bo‘limda faqat umumiy nazorat cardlari turadi. Ustoz yaratish va ma’lumotlar alohida bo‘limlarga ajratildi.', ru:'В этом разделе находятся только общие карточки контроля. Создание учителей и информация вынесены в отдельные разделы.', en:'This section contains only general control cards. Teacher creation and information are separated into their own sections.' },
  'Real vaqt nazorati': { uz:'Real vaqt nazorati', ru:'Контроль в реальном времени', en:'Real-time control' },
  'Platformadagi o‘quvchilar soni avtomatik yangilanadi': { uz:'Platformadagi o‘quvchilar soni avtomatik yangilanadi', ru:'Количество учеников на платформе обновляется автоматически', en:'The number of students on the platform updates automatically' },
  'O‘quvchi saytga kirsa son oshadi, chiqib ketsa shu zahoti kamayadi.': { uz:'O‘quvchi saytga kirsa son oshadi, chiqib ketsa shu zahoti kamayadi.', ru:'Когда ученик заходит на сайт, число увеличивается; когда выходит, сразу уменьшается.', en:'When a student enters, the count increases; when they leave, it decreases immediately.' },
  'hozir online': { uz:'hozir online', ru:'сейчас онлайн', en:'online now' },
  'Hozir saytda': { uz:'Hozir saytda', ru:'Сейчас на сайте', en:'Currently on site' },
  'Real vaqt o‘quvchilar': { uz:'Real vaqt o‘quvchilar', ru:'Ученики в реальном времени', en:'Real-time students' },
  'Jami o‘quvchi': { uz:'Jami o‘quvchi', ru:'Всего учеников', en:'Total students' },
  'Registratsiyadan o‘tganlar': { uz:'Registratsiyadan o‘tganlar', ru:'Зарегистрированные', en:'Registered users' },
  'Ustoz': { uz:'Ustoz', ru:'Учитель', en:'Teacher' },
  'Yaratilgan o‘qituvchilar': { uz:'Yaratilgan o‘qituvchilar', ru:'Созданные учителя', en:'Created teachers' },
  'Kurs': { uz:'Kurs', ru:'Курс', en:'Course' },
  'Jami kurslar': { uz:'Jami kurslar', ru:'Всего курсов', en:'Total courses' },
  'Sotib olingan': { uz:'Sotib olingan', ru:'Куплено', en:'Purchased' },
  'Kurs ochish soni': { uz:'Kurs ochish soni', ru:'Количество открытий курса', en:'Course unlock count' },
  'Test topshirishlar': { uz:'Test topshirishlar', ru:'Сданные тесты', en:'Submitted tests' },
  'Hozir platformadagi o‘quvchilar': { uz:'Hozir platformadagi o‘quvchilar', ru:'Ученики сейчас на платформе', en:'Students currently on the platform' },
  'Ism-familiyalar saytda ko‘rinadi, to‘liq ma’lumot Excelda ochiladi.': { uz:'Ism-familiyalar saytda ko‘rinadi, to‘liq ma’lumot Excelda ochiladi.', ru:'Имена и фамилии видны на сайте, полная информация открывается в Excel.', en:'Names are visible on the site; full information opens in Excel.' },
  'online': { uz:'online', ru:'онлайн', en:'online' },
  'ro‘yxatda': { uz:'ro‘yxatda', ru:'в списке', en:'listed' },
  'Hali o‘quvchi yo‘q.': { uz:'Hali o‘quvchi yo‘q.', ru:'Пока учеников нет.', en:'No students yet.' },
  'Ustoz yaratish bo‘limi': { uz:'Ustoz yaratish bo‘limi', ru:'Раздел создания учителя', en:'Create teacher section' },
  'Ma’lumotlar bo‘limi': { uz:'Ma’lumotlar bo‘limi', ru:'Раздел информации', en:'Information section' },
  'Ma’lumotlar markazi': { uz:'Ma’lumotlar markazi', ru:'Центр информации', en:'Information center' },
  'Saytdagi barcha ma’lumotlar': { uz:'Saytdagi barcha ma’lumotlar', ru:'Все данные сайта', en:'All site data' },
  'Bu bo‘lim faqat admin panelida ko‘rinadi. Har bir card o‘z ma’lumotini Excel qilib yuklaydi.': { uz:'Bu bo‘lim faqat admin panelida ko‘rinadi. Har bir card o‘z ma’lumotini Excel qilib yuklaydi.', ru:'Этот раздел виден только в админ панели. Каждая карточка скачивает свои данные в Excel.', en:'This section is visible only in the admin panel. Each card downloads its own data as Excel.' },
  'Hammasini bitta Excelga yuklash': { uz:'Hammasini bitta Excelga yuklash', ru:'Скачать всё в один Excel', en:'Download all in one Excel' },
  'Foydalanuvchilar': { uz:'Foydalanuvchilar', ru:'Пользователи', en:'Users' },
  'O‘quvchilar': { uz:'O‘quvchilar', ru:'Ученики', en:'Students' },
  'O‘quvchilar Excel': { uz:'O‘quvchilar Excel', ru:'Excel учеников', en:'Students Excel' },
  '1 oy': { uz:'1 oy', ru:'1 месяц', en:'1 month' },
  'Oylik kirishlar': { uz:'Oylik kirishlar', ru:'Месячные входы', en:'Monthly entries' },
  'Oxirgi 30 kunda registratsiya qilgan foydalanuvchilar soni.': { uz:'Oxirgi 30 kunda registratsiya qilgan foydalanuvchilar soni.', ru:'Количество пользователей, зарегистрированных за последние 30 дней.', en:'Number of users registered in the last 30 days.' },
  'Oylik Excel': { uz:'Oylik Excel', ru:'Месячный Excel', en:'Monthly Excel' },
  'Sotuv': { uz:'Sotuv', ru:'Продажи', en:'Sales' },
  'Kurs sotib olish': { uz:'Kurs sotib olish', ru:'Покупка курсов', en:'Course purchases' },
  'Sotuv Excel': { uz:'Sotuv Excel', ru:'Excel продаж', en:'Sales Excel' },
  'Umumiy': { uz:'Umumiy', ru:'Общее', en:'General' },
  'Obshi Excel': { uz:'Obshi Excel', ru:'Общий Excel', en:'All Excel' },
  'O‘quvchilar, oylik kirishlar, kurs sotib olishlar va umumiy statistika bitta Excel faylda.': { uz:'O‘quvchilar, oylik kirishlar, kurs sotib olishlar va umumiy statistika bitta Excel faylda.', ru:'Ученики, месячные входы, покупки курсов и общая статистика в одном Excel файле.', en:'Students, monthly entries, course purchases and overall statistics in one Excel file.' },
  'Hammasini yuklash': { uz:'Hammasini yuklash', ru:'Скачать всё', en:'Download all' },
  'Admin only': { uz:'Admin only', ru:'Только админ', en:'Admin only' },
  'Bu bo‘lim faqat admin panelida ko‘rinadi. Yangi ustoz login va parol shu yerdan ochiladi.': { uz:'Bu bo‘lim faqat admin panelida ko‘rinadi. Yangi ustoz login va parol shu yerdan ochiladi.', ru:'Этот раздел виден только в админ панели. Здесь создаётся логин и пароль нового учителя.', en:'This section is visible only in admin panel. New teacher login and password are created here.' },
  'Admin shu joydan yangi ustoz login ochadi.': { uz:'Admin shu joydan yangi ustoz login ochadi.', ru:'Админ создаёт здесь новый логин учителя.', en:'Admin creates a new teacher login here.' },
  'Ustoz ism familiya': { uz:'Ustoz ism familiya', ru:'Имя и фамилия учителя', en:'Teacher full name' },
  'Ustoz login': { uz:'Ustoz login', ru:'Логин учителя', en:'Teacher login' },
  'Ustoz parol': { uz:'Ustoz parol', ru:'Пароль учителя', en:'Teacher password' },
  'Ustozni saqlash': { uz:'Ustozni saqlash', ru:'Сохранить учителя', en:'Save teacher' },
  'Yaratilgan ustozlar': { uz:'Yaratilgan ustozlar', ru:'Созданные учителя', en:'Created teachers' },
  'Admin yaratgan ustozlarni shu yerdan o‘chiradi.': { uz:'Admin yaratgan ustozlarni shu yerdan o‘chiradi.', ru:'Админ удаляет созданных учителей здесь.', en:'Admin deletes created teachers here.' },
  'O‘chirish': { uz:'O‘chirish', ru:'Удалить', en:'Delete' },
  'Hali ustoz yaratilmagan.': { uz:'Hali ustoz yaratilmagan.', ru:'Учителя пока не созданы.', en:'No teachers created yet.' },
  'Admin paneliga kirish': { uz:'Admin paneliga kirish', ru:'Вход в админ панель', en:'Admin panel login' },
  'Admin login va parol bilan kiriladi.': { uz:'Admin login va parol bilan kiriladi.', ru:'Вход по логину и паролю админа.', en:'Log in with admin username and password.' },

  // Questions / AI
  'Sayt haqida istalgan savolni yozing. Enter yoki yuqoriga qaragan tugma orqali yuboriladi.': { uz:'Sayt haqida istalgan savolni yozing. Enter yoki yuqoriga qaragan tugma orqali yuboriladi.', ru:'Напишите любой вопрос о сайте. Отправьте через Enter или кнопку со стрелкой вверх.', en:'Write any question about the site. Send with Enter or the up-arrow button.' },
  'Salom! EduLive Pro platformasi haqida savolingizni yozing. Kurslar, live dars, testlar yoki foydalanish tartibini tushuntirib beraman.': { uz:'Salom! EduLive Pro platformasi haqida savolingizni yozing. Kurslar, live dars, testlar yoki foydalanish tartibini tushuntirib beraman.', ru:'Здравствуйте! Напишите вопрос о платформе EduLive Pro. Я объясню курсы, live-уроки, тесты или порядок использования.', en:'Hello! Ask a question about EduLive Pro. I can explain courses, live classes, tests, or how to use the platform.' },
  'Savolingizni yozing...': { uz:'Savolingizni yozing...', ru:'Напишите вопрос...', en:'Write your question...' },
  'Javob yozilmoqda...': { uz:'Javob yozilmoqda...', ru:'Ответ пишется...', en:'Writing answer...' },
  'Javob topilmadi.': { uz:'Javob topilmadi.', ru:'Ответ не найден.', en:'No answer found.' },
  'AI javob berishda vaqtinchalik muammo. Backendda OPENAI_API_KEY to‘g‘ri qo‘yilganini tekshiring.': { uz:'AI javob berishda vaqtinchalik muammo. Backendda OPENAI_API_KEY to‘g‘ri qo‘yilganini tekshiring.', ru:'Временная проблема с AI. Проверьте OPENAI_API_KEY в backend/.env.', en:'Temporary AI problem. Check OPENAI_API_KEY in backend/.env.' },

  // Auth / forms / misc
  'Registratsiya': { uz:'Registratsiya', ru:'Регистрация', en:'Registration' },
  'Saytga kirish uchun ro‘yxatdan o‘ting': { uz:'Saytga kirish uchun ro‘yxatdan o‘ting', ru:'Зарегистрируйтесь для входа на сайт', en:'Register to enter the platform' },
  'Ustoz paneliga kirish': { uz:'Ustoz paneliga kirish', ru:'Вход в панель учителя', en:'Teacher panel login' },
  'Ism, familiya, telefon va email to‘liq bo‘lishi kerak. Registratsiyadan keyin siz o‘quvchi sifatida saytga kirasiz.': { uz:'Ism, familiya, telefon va email to‘liq bo‘lishi kerak. Registratsiyadan keyin siz o‘quvchi sifatida saytga kirasiz.', ru:'Введите имя, фамилию, телефон и email. После регистрации вы войдёте как ученик.', en:'Enter first name, last name, phone and email. After registration you enter as a student.' },
  'Ustoz yoki admin login va parol bilan kiradi. Admin yoki ustoz login va parol bilan shu yerdan kiradi.': { uz:'Ustoz yoki admin login va parol bilan kiradi. Admin yoki ustoz login va parol bilan shu yerdan kiradi.', ru:'Учитель или админ входит здесь по логину и паролю.', en:'Teacher or admin logs in here with username and password.' },
  'Ism': { uz:'Ism', ru:'Имя', en:'First name' },
  'Familiya': { uz:'Familiya', ru:'Фамилия', en:'Last name' },
  'Telefon: 881649969 yoki +998881649969': { uz:'Telefon: 881649969 yoki +998881649969', ru:'Телефон: 881649969 или +998881649969', en:'Phone: 881649969 or +998881649969' },
  'Registratsiya qilish': { uz:'Registratsiya qilish', ru:'Зарегистрироваться', en:'Register' },
  'Ustoz yoki admin login': { uz:'Ustoz yoki admin login', ru:'Логин учителя или админа', en:'Teacher or admin login' },
  'Parol': { uz:'Parol', ru:'Пароль', en:'Password' },
  'Login bo‘lmadi.': { uz:'Login bo‘lmadi.', ru:'Вход не выполнен.', en:'Login failed.' },
  'Registratsiya bo‘lmadi.': { uz:'Registratsiya bo‘lmadi.', ru:'Регистрация не выполнена.', en:'Registration failed.' },
  'Registratsiya bo‘ldi.': { uz:'Registratsiya bo‘ldi.', ru:'Регистрация завершена.', en:'Registration completed.' },

  // Live / tests / results / video
  'Ustoz live studiyasi': { uz:'Ustoz live studiyasi', ru:'Live студия учителя', en:'Teacher live studio' },
  'Live dars o‘tish': { uz:'Live dars o‘tish', ru:'Провести live урок', en:'Teach live class' },
  'Live darsni yoqing: o‘quvchi panelida “Live dars yoqildi” xabari va qo‘shilish tugmasi chiqadi. Faqat ustoz gapiradi, o‘quvchilar ekran va ovozni ko‘radi.': { uz:'Live darsni yoqing: o‘quvchi panelida “Live dars yoqildi” xabari va qo‘shilish tugmasi chiqadi. Faqat ustoz gapiradi, o‘quvchilar ekran va ovozni ko‘radi.', ru:'Включите live урок: в панели ученика появится сообщение «Live урок включен» и кнопка подключения. Говорит только учитель, ученики видят экран и слышат звук.', en:'Start the live class: students see a live notification and join button. Only the teacher speaks; students see the screen and hear audio.' },
  'Xona kodi': { uz:'Xona kodi', ru:'Код комнаты', en:'Room code' },
  'Holat': { uz:'Holat', ru:'Статус', en:'Status' },
  '100% ekran yozish va live uzatish': { uz:'100% ekran yozish va live uzatish', ru:'100% запись экрана и live-трансляция', en:'100% screen recording and live streaming' },
  'Chrome oynasida “Entire screen / Весь экран” ni tanlang va “Share audio” ni belgilang.': { uz:'Chrome oynasida “Entire screen / Весь экран” ni tanlang va “Share audio” ni belgilang.', ru:'В окне Chrome выберите “Entire screen / Весь экран” и отметьте “Share audio”.', en:'In Chrome choose “Entire screen” and enable “Share audio”.' },
  'Live to‘xtatish': { uz:'Live to‘xtatish', ru:'Остановить live', en:'Stop live' },
  'Dars darajasi / mavzusi': { uz:'Dars darajasi / mavzusi', ru:'Уровень / тема урока', en:'Class level / topic' },
  'Kursga saqlash sozlamasi': { uz:'Kursga saqlash sozlamasi', ru:'Настройка сохранения в курс', en:'Save to course settings' },
  'Saqlash tugmasi dars to‘xtatilgandan keyin chiqadi. Darajani yozmasdan kursga tushmaydi.': { uz:'Saqlash tugmasi dars to‘xtatilgandan keyin chiqadi. Darajani yozmasdan kursga tushmaydi.', ru:'Кнопка сохранения появляется после остановки урока. Без уровня курс не сохранится.', en:'The save button appears after the class is stopped. Without level, it will not be saved.' },
  'Kursni tanlang': { uz:'Kursni tanlang', ru:'Выберите курс', en:'Select a course' },
  'Livega kirgan o‘quvchilar': { uz:'Livega kirgan o‘quvchilar', ru:'Ученики, вошедшие в live', en:'Students who joined live' },
  'O‘quvchi qo‘shilsa shu yerda ko‘rinadi.': { uz:'O‘quvchi qo‘shilsa shu yerda ko‘rinadi.', ru:'Когда ученик подключится, он появится здесь.', en:'When a student joins, they appear here.' },
  'Chiqarish': { uz:'Chiqarish', ru:'Удалить', en:'Remove' },
  'Hali o‘quvchi qo‘shilmadi.': { uz:'Hali o‘quvchi qo‘shilmadi.', ru:'Пока ученик не подключился.', en:'No student has joined yet.' },
  'Pullik live darslar': { uz:'Pullik live darslar', ru:'Платные live уроки', en:'Paid live classes' },
  'Bu bo‘limda live olib qo‘yilgan kurs videolari turadi. Kurs sotib olingandan keyin video ko‘riladi, saqlab olish va jo‘natish cheklangan.': { uz:'Bu bo‘limda live olib qo‘yilgan kurs videolari turadi. Kurs sotib olingandan keyin video ko‘riladi, saqlab olish va jo‘natish cheklangan.', ru:'В этом разделе находятся видео записанных live-курсов. После покупки курса видео доступно, скачивание и пересылка ограничены.', en:'This section contains recorded live course videos. After purchase the video is available, downloading and forwarding are restricted.' },
  'Live kurslar yuklanmoqda...': { uz:'Live kurslar yuklanmoqda...', ru:'Live курсы загружаются...', en:'Loading live courses...' },
  'Hali live video kurs qo‘shilmagan.': { uz:'Hali live video kurs qo‘shilmagan.', ru:'Live видео-курс пока не добавлен.', en:'No live video course added yet.' },
  'O‘quvchi frontend yoki backend yo‘nalishini tanlab testni yechadi. Natijalar avtomatik ustoz bo‘limidagi natijalar sahifasiga tushadi.': { uz:'O‘quvchi frontend yoki backend yo‘nalishini tanlab testni yechadi. Natijalar avtomatik ustoz bo‘limidagi natijalar sahifasiga tushadi.', ru:'Ученик выбирает frontend или backend и проходит тест. Результаты автоматически попадают на страницу результатов учителя.', en:'The student selects frontend or backend and takes the test. Results automatically go to the teacher results page.' },
  'O‘quvchi bo‘limi': { uz:'O‘quvchi bo‘limi', ru:'Раздел ученика', en:'Student section' },
  'Testlar yuklanmoqda...': { uz:'Testlar yuklanmoqda...', ru:'Тесты загружаются...', en:'Loading tests...' },
  'Testni yechish': { uz:'Testni yechish', ru:'Решить тест', en:'Take the test' },
  'Hozircha bu yo‘nalish va darajada test yo‘q.': { uz:'Hozircha bu yo‘nalish va darajada test yo‘q.', ru:'Пока для этого направления и уровня тестов нет.', en:'No tests for this track and level yet.' },
  'Natijalar bo‘limi': { uz:'Natijalar bo‘limi', ru:'Раздел результатов', en:'Results section' },
  'O‘quvchilarning test natijalari faqat ustozlarga ko‘rinadi.': { uz:'O‘quvchilarning test natijalari faqat ustozlarga ko‘rinadi.', ru:'Результаты тестов учеников видны только учителям.', en:'Student test results are visible only to teachers.' },
  'Frontend natijalari': { uz:'Frontend natijalari', ru:'Frontend результаты', en:'Frontend results' },
  'Backend natijalari': { uz:'Backend natijalari', ru:'Backend результаты', en:'Backend results' },
  'Hali frontend natijasi yo‘q.': { uz:'Hali frontend natijasi yo‘q.', ru:'Пока нет frontend результатов.', en:'No frontend results yet.' },
  'Hali backend natijasi yo‘q.': { uz:'Hali backend natijasi yo‘q.', ru:'Пока нет backend результатов.', en:'No backend results yet.' },
  'Test natijasi': { uz:'Test natijasi', ru:'Результат теста', en:'Test result' },
  'Foiz': { uz:'Foiz', ru:'Процент', en:'Percent' },
  'To‘g‘ri': { uz:'To‘g‘ri', ru:'Правильно', en:'Correct' },
  'Noto‘g‘ri': { uz:'Noto‘g‘ri', ru:'Неправильно', en:'Incorrect' },
  'Yana test yechish': { uz:'Yana test yechish', ru:'Решить ещё тест', en:'Take another test' },
  'Testni saqlash': { uz:'Testni saqlash', ru:'Сохранить тест', en:'Save test' },
  'O‘quvchi:': { uz:'O‘quvchi:', ru:'Ученик:', en:'Student:' },
  'Kursga qaytish': { uz:'Kursga qaytish', ru:'Вернуться к курсу', en:'Back to course' },
  'Oldinga o‘tkazish bloklangan': { uz:'Oldinga o‘tkazish bloklangan', ru:'Перемотка вперёд заблокирована', en:'Forward seeking is blocked' },
  'Ovoz': { uz:'Ovoz', ru:'Звук', en:'Audio' },
  'Video bilan birga eshitiladi': { uz:'Video bilan birga eshitiladi', ru:'Слышно вместе с видео', en:'Played with video' },
  'Nazorat': { uz:'Nazorat', ru:'Контроль', en:'Control' },
  'Faqat ochilgan kurs egalari ko‘radi': { uz:'Faqat ochilgan kurs egalari ko‘radi', ru:'Видят только владельцы открытого курса', en:'Only unlocked course owners can watch' },
  'Xato': { uz:'Xato', ru:'Ошибка', en:'Error' },
  'Bosh sahifa': { uz:'Bosh sahifa', ru:'Главная страница', en:'Home page' }
}


// Extra complete phrases for full page translation
Object.assign(T, {
  'Online kurs platforma': { uz:'Online kurs platforma', ru:'Онлайн-платформа курсов', en:'Online course platform' },
  'Online kurs platformasi': { uz:'Online kurs platformasi', ru:'Онлайн-платформа курсов', en:'Online course platform' },
  'Online-platforma kursov': { uz:'Online kurs platforma', ru:'Онлайн-платформа курсов', en:'Online course platform' },
  'Kurslar bo‘limi': { uz:'Kurslar bo‘limi', ru:'Раздел курсов', en:'Courses section' },
  'Sotuvdagi barcha kurslar quyida joylashgan': { uz:'Sotuvdagi barcha kurslar quyida joylashgan', ru:'Все курсы в продаже расположены ниже', en:'All courses for sale are listed below' },
  'Frontend yo‘nalishlari': { uz:'Frontend yo‘nalishlari', ru:'Frontend направления', en:'Frontend tracks' },
  'Backend yo‘nalishlari': { uz:'Backend yo‘nalishlari', ru:'Backend направления', en:'Backend tracks' },
  'HTML, CSS, JavaScript, Vue, React': { uz:'HTML, CSS, JavaScript, Vue, React', ru:'HTML, CSS, JavaScript, Vue, React', en:'HTML, CSS, JavaScript, Vue, React' },
  'Barcha kurslar': { uz:'Barcha kurslar', ru:'Все курсы', en:'All courses' },
  'Sotib olish': { uz:'Sotib olish', ru:'Купить', en:'Buy' },
  'Kurslar': { uz:'Kurslar', ru:'Курсы', en:'Courses' },
  'Live kurslar': { uz:'Live kurslar', ru:'Live курсы', en:'Live courses' },
  'Live yozuv kurslari': { uz:'Live yozuv kurslari', ru:'Видео-записи live-уроков', en:'Live recording courses' },
  'Live yozuv kurslari alohida bo‘limda saqlanadi': { uz:'Live yozuv kurslari alohida bo‘limda saqlanadi', ru:'Видео-записи live-курсов сохраняются в отдельном разделе', en:'Live recordings are saved in a separate section' },
  'Live yozuv kurslari': { uz:'Live yozuv kurslari', ru:'Видео-записи live-курсов', en:'Live recordings' },
  'Video-yozuvlar': { uz:'Video-yozuvlar', ru:'Видео-записи', en:'Video recordings' },
  'Pullik live darslar': { uz:'Pullik live darslar', ru:'Платные live уроки', en:'Paid live classes' },
  'В этом разделе находятся видео записанных live-курсов. После покупки курса видео доступно, скачивание и пересылка ограничены.': { uz:'Bu bo‘limda yozib olingan live-kurs videolari turadi. Kurs sotib olingandan keyin video ko‘riladi, saqlab olish va jo‘natish cheklangan.', ru:'В этом разделе находятся видео записанных live-курсов. После покупки курса видео доступно, скачивание и пересылка ограничены.', en:'This section contains recorded live-course videos. After purchase, the video is available and download/forwarding are restricted.' },
  'Bu bo‘limda yozib olingan live-kurs videolari turadi. Kurs sotib olingandan keyin video ko‘riladi, saqlab olish va jo‘natish cheklangan.': { uz:'Bu bo‘limda yozib olingan live-kurs videolari turadi. Kurs sotib olingandan keyin video ko‘riladi, saqlab olish va jo‘natish cheklangan.', ru:'В этом разделе находятся видео записанных live-курсов. После покупки курса видео доступно, скачивание и пересылка ограничены.', en:'This section contains recorded live-course videos. After purchase, the video is available and download/forwarding are restricted.' },
  'Live video-kurs пока не добавлен.': { uz:'Hali live video kurs qo‘shilmagan.', ru:'Live видео-курс пока не добавлен.', en:'No live video course added yet.' },
  'Hali live video kurs qo‘shilmagan.': { uz:'Hali live video kurs qo‘shilmagan.', ru:'Live видео-курс пока не добавлен.', en:'No live video course added yet.' },
  'Test tizimi': { uz:'Test tizimi', ru:'Система тестов', en:'Test system' },
  'Daraja va yo‘nalish bo‘yicha testlarni ishlash': { uz:'Daraja va yo‘nalish bo‘yicha testlarni ishlash', ru:'Прохождение тестов по уровню и направлению', en:'Take tests by level and track' },
  'Natijalar': { uz:'Natijalar', ru:'Результаты', en:'Results' },
  'Ustoz natijalarni foiz, ball va yo‘nalish bo‘yicha ko‘radi': { uz:'Ustoz natijalarni foiz, ball va yo‘nalish bo‘yicha ko‘radi', ru:'Учитель видит результаты по процентам, баллам и направлениям', en:'Teacher sees results by percent, score and track' },
  'Platforma haqida': { uz:'Platforma haqida', ru:'О платформе', en:'About platform' },
  'EduLive Pro — o‘quv markaz va kurs tizimiga mos zamonaviy platforma. Har bir bo‘lim hover animatsiya, yumshoq o‘tish va chiroyli bloklar bilan tayyorlangan.': { uz:'EduLive Pro — o‘quv markaz va kurs tizimiga mos zamonaviy platforma. Har bir bo‘lim hover animatsiya, yumshoq o‘tish va chiroyli bloklar bilan tayyorlangan.', ru:'EduLive Pro — современная платформа для учебных центров и курсов. Каждый раздел оформлен с hover-анимациями, плавными переходами и красивыми блоками.', en:'EduLive Pro is a modern platform for training centers and course systems. Every section has hover animations, smooth transitions and beautiful blocks.' },
  'Kodlash': { uz:'Kodlash', ru:'Кодинг', en:'Coding' },
  'Live yoq': { uz:'Live yoq', ru:'Live включён', en:'Live on' },
  'Natija': { uz:'Natija', ru:'Результат', en:'Result' },
  'Qisqacha ishlash tartibi': { uz:'Qisqacha ishlash tartibi', ru:'Краткий порядок работы', en:'How it works' },
  'O‘quvchi registratsiya qiladi va tizimga kiradi.': { uz:'O‘quvchi registratsiya qiladi va tizimga kiradi.', ru:'Ученик регистрируется и входит в систему.', en:'The student registers and logs in.' },
  'Ustoz testlarni o‘z bo‘limidan frontend yoki backend yo‘nalishiga qo‘shadi.': { uz:'Ustoz testlarni o‘z bo‘limidan frontend yoki backend yo‘nalishiga qo‘shadi.', ru:'Учитель добавляет тесты в направления frontend или backend из своего раздела.', en:'The teacher adds tests to frontend or backend from their section.' },
  'O‘quvchi testni yechadi, natijalar ustoz bo‘limiga tushadi.': { uz:'O‘quvchi testni yechadi, natijalar ustoz bo‘limiga tushadi.', ru:'Ученик решает тест, результаты попадают в раздел учителя.', en:'The student takes the test and results go to the teacher section.' },
  'Live yozuvlar alohida pullik bo‘limga saqlanadi.': { uz:'Live yozuvlar alohida pullik bo‘limga saqlanadi.', ru:'Live-записи сохраняются в отдельном платном разделе.', en:'Live recordings are saved in a separate paid section.' },
  'Admin nazorat markazi': { uz:'Admin nazorat markazi', ru:'Центр контроля администратора', en:'Admin control center' },
  'Platformadagi o‘quvchilar soni avtomatik yangilanadi': { uz:'Platformadagi o‘quvchilar soni avtomatik yangilanadi', ru:'Количество учеников на платформе обновляется автоматически', en:'Number of platform students updates automatically' },
  'O‘quvchi saytga kirsa son oshadi, chiqib ketsa shu zahoti kamayadi.': { uz:'O‘quvchi saytga kirsa son oshadi, chiqib ketsa shu zahoti kamayadi.', ru:'Когда ученик входит, число увеличивается; когда выходит — сразу уменьшается.', en:'When a student enters the site, the number increases; when they leave, it decreases immediately.' },
  'Hozir saytda': { uz:'Hozir saytda', ru:'Сейчас на сайте', en:'Currently online' },
  'Real vaqt o‘quvchilar': { uz:'Real vaqt o‘quvchilar', ru:'Ученики в реальном времени', en:'Real-time students' },
  'Jami o‘quvchi': { uz:'Jami o‘quvchi', ru:'Всего учеников', en:'Total students' },
  'Registratsiyadan o‘tganlar': { uz:'Registratsiyadan o‘tganlar', ru:'Зарегистрированные', en:'Registered users' },
  'Yaratilgan o‘qituvchilar': { uz:'Yaratilgan o‘qituvchilar', ru:'Созданные учителя', en:'Created teachers' },
  'Jami kurslar': { uz:'Jami kurslar', ru:'Всего курсов', en:'Total courses' },
  'Kurs ochish soni': { uz:'Kurs ochish soni', ru:'Количество открытий курсов', en:'Course unlocks' },
  'Test topshirishlar': { uz:'Test topshirishlar', ru:'Сданные тесты', en:'Test submissions' },
  'Hozir platformadagi o‘quvchilar': { uz:'Hozir platformadagi o‘quvchilar', ru:'Ученики сейчас на платформе', en:'Students currently on platform' },
  'Ism-familiyalar saytda ko‘rinadi, to‘liq ma’lumot Excelda ochiladi.': { uz:'Ism-familiyalar saytda ko‘rinadi, to‘liq ma’lumot Excelda ochiladi.', ru:'Имена и фамилии видны на сайте, полная информация открывается в Excel.', en:'Names are visible on the site, full information opens in Excel.' },
  'ro‘yxatda': { uz:'ro‘yxatda', ru:'в списке', en:'listed' },
  'online': { uz:'online', ru:'онлайн', en:'online' }
})

// Known mixed strings that can appear after older partial translations. They are normalized directly.

// Extra final translations: prevents half Uzbek / half Russian texts in all panels.
Object.assign(T, {
  'Live yozuv kurslari': { uz:'Live yozuv kurslari', ru:'Курсы с live-записями', en:'Live recording courses' },
  'Bu bo‘limda live olib qo‘yilgan kurs videolari turadi. Kurs sotib olingandan keyin video ko‘riladi, saqlab olish va jo‘natish cheklangan.': { uz:'Bu bo‘limda live olib qo‘yilgan kurs videolari turadi. Kurs sotib olingandan keyin video ko‘riladi, saqlab olish va jo‘natish cheklangan.', ru:'В этом разделе хранятся видео записанных live-уроков. После покупки курса видео открывается, скачивание и пересылка ограничены.', en:'This section stores videos from recorded live classes. After purchase the video opens; download and forwarding are restricted.' },
  'Hali live video kurs qo‘shilmagan.': { uz:'Hali live video kurs qo‘shilmagan.', ru:'Live видео-курс пока не добавлен.', en:'No live video course has been added yet.' },
  'Pullik live darslar': { uz:'Pullik live darslar', ru:'Платные live-уроки', en:'Paid live classes' },
  'Live video-kurs пока не добавлен.': { uz:'Hali live video kurs qo‘shilmagan.', ru:'Live видео-курс пока не добавлен.', en:'No live video course has been added yet.' },
  'Live видео-курс пока не добавлен.': { uz:'Hali live video kurs qo‘shilmagan.', ru:'Live видео-курс пока не добавлен.', en:'No live video course has been added yet.' },
  'В этом разделе находятся видео записанных live-курсов. После покупки курса видео доступно, скачивание и пересылка ограничены.': { uz:'Bu bo‘limda live olib qo‘yilgan kurs videolari turadi. Kurs sotib olingandan keyin video ko‘riladi, saqlab olish va jo‘natish cheklangan.', ru:'В этом разделе хранятся видео записанных live-уроков. После покупки курса видео открывается, скачивание и пересылка ограничены.', en:'This section stores videos from recorded live classes. After purchase the video opens; download and forwarding are restricted.' },
  'Platformadagi o‘quvchilar soni avtomatik yangilanadi': { uz:'Platformadagi o‘quvchilar soni avtomatik yangilanadi', ru:'Количество учеников на платформе обновляется автоматически', en:'The number of students on the platform updates automatically' },
  'O‘quvchi saytga kirsa son oshadi, chiqib ketsa shu zahoti kamayadi.': { uz:'O‘quvchi saytga kirsa son oshadi, chiqib ketsa shu zahoti kamayadi.', ru:'Когда ученик входит на сайт, число увеличивается; когда выходит — сразу уменьшается.', en:'When a student enters the site, the number increases; when they leave, it decreases immediately.' },
  'Hozir saytda': { uz:'Hozir saytda', ru:'Сейчас на сайте', en:'Currently online' },
  'Real vaqt o‘quvchilar': { uz:'Real vaqt o‘quvchilar', ru:'Ученики онлайн', en:'Real-time students' },
  'Jami o‘quvchi': { uz:'Jami o‘quvchi', ru:'Всего учеников', en:'Total students' },
  'Registratsiyadan o‘tganlar': { uz:'Registratsiyadan o‘tganlar', ru:'Зарегистрированные', en:'Registered users' },
  'Ustoz': { uz:'Ustoz', ru:'Учитель', en:'Teacher' },
  'Yaratilgan o‘qituvchilar': { uz:'Yaratilgan o‘qituvchilar', ru:'Созданные учителя', en:'Created teachers' },
  'Kurs': { uz:'Kurs', ru:'Курс', en:'Course' },
  'Jami kurslar': { uz:'Jami kurslar', ru:'Всего курсов', en:'Total courses' },
  'Sotib olingan': { uz:'Sotib olingan', ru:'Куплено', en:'Purchased' },
  'Kurs ochish soni': { uz:'Kurs ochish soni', ru:'Количество открытых курсов', en:'Course unlock count' },
  'Test topshirishlar': { uz:'Test topshirishlar', ru:'Сданные тесты', en:'Test submissions' },
  'Hozir platformadagi o‘quvchilar': { uz:'Hozir platformadagi o‘quvchilar', ru:'Ученики сейчас на платформе', en:'Students currently on the platform' },
  'Ism-familiyalar saytda ko‘rinadi, to‘liq ma’lumot Excelda ochiladi.': { uz:'Ism-familiyalar saytda ko‘rinadi, to‘liq ma’lumot Excelda ochiladi.', ru:'Имена и фамилии видны на сайте, полная информация открывается в Excel.', en:'Names are visible on the site, full information opens in Excel.' },
  'email yo‘q': { uz:'email yo‘q', ru:'нет email', en:'no email' },
  'telefon yo‘q': { uz:'telefon yo‘q', ru:'нет телефона', en:'no phone' },
  'ro‘yxatda': { uz:'ro‘yxatda', ru:'в списке', en:'registered' },
  'Hali o‘quvchi yo‘q.': { uz:'Hali o‘quvchi yo‘q.', ru:'Учеников пока нет.', en:'No students yet.' },
  'Ustoz yaratish bo‘limi': { uz:'Ustoz yaratish bo‘limi', ru:'Раздел создания учителя', en:'Teacher creation section' },
  'Ma’lumotlar bo‘limi': { uz:'Ma’lumotlar bo‘limi', ru:'Раздел информации', en:'Information section' },
  'Admin nazorat markazi': { uz:'Admin nazorat markazi', ru:'Центр админ-контроля', en:'Admin control center' },
  'Bu bo‘limda faqat umumiy nazorat cardlari turadi. Ustoz yaratish va ma’lumotlar alohida bo‘limlarga ajratildi.': { uz:'Bu bo‘limda faqat umumiy nazorat cardlari turadi. Ustoz yaratish va ma’lumotlar alohida bo‘limlarga ajratildi.', ru:'В этом разделе находятся только общие карточки контроля. Создание учителя и информация вынесены в отдельные разделы.', en:'This section contains only general control cards. Teacher creation and information are separated into different sections.' },
  'Real vaqt nazorati': { uz:'Real vaqt nazorati', ru:'Контроль в реальном времени', en:'Real-time control' },
  'hozir online': { uz:'hozir online', ru:'сейчас онлайн', en:'online now' },
  'online': { uz:'online', ru:'онлайн', en:'online' },
})

const MIXED = {
  'Frontend и backend bo‘yicha pullik yo‘nalishlar': 'Frontend va backend bo‘yicha pullik yo‘nalishlar',
  'Frontend и backend bo‘yicha pullik yo‘nalishlar': 'Frontend va backend bo‘yicha pullik yo‘nalishlar',
  'Live урокlar': 'Live darslar',
  'Live урок kurslari alohida bo‘limda saqlanadi': 'Live yozuv kurslari alohida bo‘limda saqlanadi',
  'Учитель natijalarni foiz, ball va yo‘nalish bo‘yicha ko‘radi': 'Ustoz natijalarni foiz, ball va yo‘nalish bo‘yicha ko‘radi',
  'Video-записи': 'Video-yozuvlar',
  'КурсЫ': 'Kurslar',
  'Kursы': 'Kurslar',
  'Решать test': 'Test yechish',
  'Test ученика': 'O‘quvchi testi'
}

const phraseAliases = new Map()
const originalTextNodes = new WeakMap()
const originalPlaceholders = new WeakMap()
const originalTitles = new WeakMap()
function normalize(value) {
  return String(value || '')
    .replace(/[’ʻ`]/g, '‘')
    .replace(/\s+/g, ' ')
    .trim()
}
function rebuildIndex() {
  phraseAliases.clear()
  for (const [key, data] of Object.entries(T)) {
    const values = [key, data.uz, data.ru, data.en].filter(Boolean)
    for (const value of values) phraseAliases.set(normalize(value), key)
  }
  for (const [mixed, key] of Object.entries(MIXED)) phraseAliases.set(normalize(mixed), key)
}
rebuildIndex()

function currentLang() {
  const bodyRole = document.body?.dataset?.eduliveRole || 'auth'
  let saved = 'uz'
  if (bodyRole === 'admin') saved = localStorage.getItem('edulive_lang_admin') || 'uz'
  else if (bodyRole === 'teacher') saved = localStorage.getItem('edulive_lang_teacher') || 'uz'
  else if (bodyRole === 'student') saved = localStorage.getItem('edulive_lang_student') || 'uz'
  else saved = localStorage.getItem('edulive_lang_auth') || 'uz'
  return ['uz', 'ru'].includes(saved) ? saved : 'uz'
}

function translateString(rawText, lang = currentLang()) {
  const raw = String(rawText ?? '')
  if (!raw.trim()) return raw
  const normalized = normalize(raw)
  const key = phraseAliases.get(normalized)
  if (key && T[key]?.[lang]) return T[key][lang]

  let result = raw
  const entries = Object.entries(T)
    .filter(([source, data]) => {
      const variants = [source, data.uz, data.ru, data.en].filter(Boolean).map(String)
      return variants.some(v => normalize(v).length >= 14 && /\s/.test(v))
    })
    .sort((a, b) => Math.max(...Object.values(b[1]).map(v => String(v).length), String(b[0]).length) - Math.max(...Object.values(a[1]).map(v => String(v).length), String(a[0]).length))

  for (const [source, data] of entries) {
    const target = data?.[lang]
    if (!target) continue
    const variants = new Set([source, data.uz, data.ru, data.en].filter(Boolean).map(String))
    for (const variant of variants) {
      if (!variant || variant === target) continue
      if (normalize(variant).length < 14) continue
      result = result.split(variant).join(target)
      result = result.split(variant.replace(/[’ʻ`]/g, '‘')).join(target)
    }
  }
  for (const [mixed, key2] of Object.entries(MIXED)) {
    const target = T[key2]?.[lang]
    if (target) result = result.split(mixed).join(target)
  }
  // Safe compact fixes for counting phrases without ever duplicating 'ta'.
  result = result.replace(/(\d+)\s+(ta\s+){2,}/g, '$1 ta ')
  if (lang === 'ru') result = result.replace(/(\d+)\s+ta\s+online/g, '$1 онлайн').replace(/(\d+)\s+ta\s+dars/g, '$1 уроков').replace(/(\d+)\s+ta\s+kirish/g, '$1 входов').replace(/(\d+)\s+ta\s+urinish/g, '$1 попыток').replace(/\bta\b/g, '')
  if (lang === 'en') result = result.replace(/(\d+)\s+ta\s+online/g, '$1 online').replace(/(\d+)\s+ta\s+dars/g, '$1 lessons').replace(/(\d+)\s+ta\s+kirish/g, '$1 visits').replace(/(\d+)\s+ta\s+urinish/g, '$1 attempts')
  return result
}

function translateTextNode(node, lang) {
  const current = node.nodeValue
  if (!current || !current.trim()) return
  if (!originalTextNodes.has(node)) originalTextNodes.set(node, current)
  const original = originalTextNodes.get(node)
  const leading = original.match(/^\s*/)?.[0] || ''
  const trailing = original.match(/\s*$/)?.[0] || ''
  const middle = original.trim()
  const translated = translateString(middle, lang)
  const nextValue = leading + translated + trailing
  if (node.nodeValue !== nextValue) node.nodeValue = nextValue
}

export function translateVisibleTexts(lang = currentLang()) {
  const root = document.getElementById('app')
  if (!root) return
  document.documentElement.lang = lang

  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      const parent = node.parentElement
      if (!parent) return NodeFilter.FILTER_REJECT
      if (['SCRIPT', 'STYLE', 'TEXTAREA'].includes(parent.tagName)) return NodeFilter.FILTER_REJECT
      // Do not translate user-typed input values or code blocks.
      if (parent.closest('[data-no-translate]')) return NodeFilter.FILTER_REJECT
      return NodeFilter.FILTER_ACCEPT
    }
  })
  const nodes = []
  while (walker.nextNode()) nodes.push(walker.currentNode)
  nodes.forEach((node) => translateTextNode(node, lang))

  root.querySelectorAll('input[placeholder], textarea[placeholder]').forEach((el) => {
    if (!originalPlaceholders.has(el)) originalPlaceholders.set(el, el.placeholder)
    const nextPlaceholder = translateString(originalPlaceholders.get(el), lang)
    if (el.placeholder !== nextPlaceholder) el.placeholder = nextPlaceholder
  })
  root.querySelectorAll('[title]').forEach((el) => {
    if (!originalTitles.has(el)) originalTitles.set(el, el.title)
    const nextTitle = translateString(originalTitles.get(el), lang)
    if (el.title !== nextTitle) el.title = nextTitle
  })
}

export function installDomTranslator(router) {
  let timer = null
  const run = (lang = currentLang()) => {
    clearTimeout(timer)
    timer = setTimeout(() => translateVisibleTexts(lang), 0)
  }
  const runMany = (lang = currentLang()) => {
    translateVisibleTexts(lang)
    setTimeout(() => translateVisibleTexts(lang), 80)
  }

  window.addEventListener('edulive-lang-change', (event) => runMany(event.detail || currentLang()))
  router?.afterEach(() => runMany())

  const waitRoot = () => {
    const root = document.getElementById('app')
    if (!root) { setTimeout(waitRoot, 50); return }
    const observer = new MutationObserver(() => run())
    observer.observe(root, { childList: true, subtree: true, characterData: false, attributes: true, attributeFilter: ['placeholder', 'title'] })
    runMany()
  }
  waitRoot()
}
