import logging,json,random,aiohttp
from zoneinfo import ZoneInfo
MOSCOW=ZoneInfo("Europe/Moscow")
from datetime import datetime,timedelta
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup,BotCommand,LinkPreviewOptions
from telegram.ext import Application,CommandHandler,CallbackQueryHandler,MessageHandler,ConversationHandler,ContextTypes,filters

BOT_TOKEN="8601435400:AAHhS3Y-n_l6IgOtqyYaorjeGcxejvkTUb0"
ADMIN_CHAT_ID=1348591267
OUTLY_URL="https://outly-31509.bubbleapps.io/version-test"

CATEGORIES={"culture":"🏛 Культура","creative":"🎨 Творчество","active":"🏃 Активный отдых","walk":"🚶 Прогулки","social":"🥂 Светские мероприятия","gastro":"🍽 Гастрономический досуг"}

# Реальные мероприятия с сайта Outly (картинки и ссылки из БД)
REAL_EVENTS=[
{"id":"r1","title":"Музей русского импрессионизма","category":"culture","link":"https://www.rusimp.su/","description":"Картины Коровина, Серова, Жуковского, Грабаря, Юона и Богданова-Бельского. Постоянная экспозиция + бесплатные лекции.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773956502593x210373659989452350/%D0%BC%D1%80%D0%B8.jpeg"},
{"id":"r2","title":"Шоу-концерт Music and Burlesque в WellWell","category":"social","link":"https://www.instagram.com/wellwell.music?igsh=dTRtemZuejNwcGJn","description":"Камерный шоу-концерт от Ladies of Burlesque — живая музыка джазового бэнда, элегантный бурлеск, ретро-костюмы и блеск страз.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773970782385x342494438440337000/%D1%88%D0%BE%D1%83.jpeg"},
{"id":"r3","title":"Camera Show — живой перформанс","category":"culture","link":"https://camerashow.ru/","description":"Живой перформанс, голос и музыкальная импровизация взаимодействуют с состоянием зрителей. Проекции на стены, панорамный вид на город.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773964682478x190169253168827040/%D0%BA%D0%B0%D0%BC%D0%B5%D1%80%D0%B0.jpeg"},
{"id":"r4","title":"Гольф на Красном Октябре","category":"active","link":"https://golf.ru/where_to_play/g-t-na-karasnom-okt/","description":"Крупнейшая в России всесезонная площадка для игры в гольф. Симуляторы, паттинг-грин, прокат клюшек, гастробар.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774226477956x525450478102811970/photo_2026-03-23_03-41-06.jpg"},
{"id":"r5","title":"Bungee Workout — батутный фитнес","category":"active","link":"https://bungeeworkout.ru/","description":"Ты летаешь над землёй, выполняя кардио-тренировку с эффектом свободного полёта и акробатики. Также пилатес, растяжка и аэростретчинг.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773965724699x681343066649046800/%D1%84%D0%B8%D1%82%D0%BD%D0%B5%D1%81.jpeg"},
{"id":"r6","title":"Deep Fried Friends — бар, ресторан и клуб","category":"gastro","link":"https://deepfriedfriends.ru/","description":"Бар, ресторан и танцы в интерьере Чёрного вигвама из «Твин Пикса». Авторская кухня, сложносочинённые коктейли и шумные вечеринки.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773966397478x655833722551879600/%D0%B4%D1%84%D1%84.jpeg"},
{"id":"r7","title":"Where to Hide — закрытый клуб с караоке","category":"social","link":"https://www.instagram.com/wheretohideinmoscow?igsh=Nzl0bzVwcW9kYTMz","description":"Закрытый клуб по предварительной брони. Лаконичный интерьер, вдохновлённый Armani Hotel Dubai. По пятницам и субботам — ужины с джазом и фламенко.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773966756737x978088210533710600/%D1%85%D0%B4.jpeg"},
{"id":"r8","title":"Ресторан Pino на Патриарших","category":"gastro","link":"https://www.instagram.com/pinorestaurantbar?igsh=MXR6NDBoYndsamh3Mw==","description":"Двухэтажный ресторан на Патриарших. Камерный бар, международное меню от шефа Руслана Полякова. Рекомендация — самый длинный эклер в Москве.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773967969528x509824487419048700/%D0%BF%D0%B8%D0%BD%D0%BE.webp"},
{"id":"r9","title":"Rock the Cycle — велотренировки под музыку","category":"active","link":"https://www.instagram.com/rockthecycle.ru?igsh=OTZnZndjemh2ZTVp","description":"Высокоинтенсивные тренировки-вечеринки под музыку и крики педагога. Тренировки под просмотр фильмов и концертов.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773968498273x261731730033293540/%D1%80%D0%BA%D0%B7%D1%81%D0%BA%D0%BB.jpeg"},
{"id":"r10","title":"WellWell Bistro — музыкальное бистро","category":"social","link":"https://www.instagram.com/wellwell.music?igsh=dTRtemZuejNwcGJn","description":"Бистро Владимира Перельмана с живыми концертами и авторской кухней. По вечерам — акустический джаз, на выходных — виниловые пластинки.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773968731764x552138127126401860/%D0%B2%D0%B2.jpeg"},
{"id":"r11","title":"Chalet Studio — гончарная мастерская","category":"creative","link":"https://www.instagram.com/chaletstudio?igsh=MTNobWU2d2lzd3NrYw==","description":"Сеть гончарных мастерских в центре Москвы. Двух мастер-классов хватит, чтобы слепить авторскую handmade посуду. Отличная идея для свидания.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774180894068x809933762766639400/photo_2026-03-22_15-01-13.jpg"},
{"id":"r12","title":"Музей AZ","category":"culture","link":"https://museum-az.com/","description":"Один из самых ярких частных музеев России. Современный музей нового поколения. В залах — множество выставок, для детей — мастер-классы по рисованию.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774182931831x531458037975383500/photo_2026-03-21_19-44-24.jpg"},
{"id":"r13","title":"Ashram — студия йоги и медитации","category":"active","link":"https://www.instagram.com/ashram?igsh=NjQ3NnlxN3lmZ2x3","description":"Well-being пространство: студия йоги и медитаций, комната аурасомы, кабинет для массажных ритуалов и концепт-стор.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774183161983x478440188968365800/photo_2026-03-22_15-39-06.jpg"},
{"id":"r14","title":"InFeels — студия массажа и йоги","category":"active","link":"https://infeels-bodysoul.ru/?utm_source=yandex","description":"Пространство заботы о здоровой красоте тела. Мастера комбинируют мануальные и аппаратные техники для расслабления и ухода за кожей.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774183356249x852537427461052000/photo_2026-03-22_15-42-13.jpg"},
{"id":"r15","title":"Галерея Triumph","category":"culture","link":"https://www.triumph.gallery/","description":"Галерея в старинном особняке продвигает современное искусство. Сотрудничает с Третьяковкой и МАММ. Выставляются знаменитые и новые художники. Вход бесплатный.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774189969550x332970826575694800/photo_2026-03-22_17-32-00.jpg"},
{"id":"r16","title":"Freestyle Wake Park","category":"active","link":"https://www.instagram.com/freestyle_wake_park","description":"Лучший реверсивный вейк-парк. Вейк-сёрф, вейкборд, бассейн и аренда лодки или каяка.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774183724080x252864508101021250/photo_2026-03-22_15-48-22.jpg"},
{"id":"r17","title":"Дом-музей Бориса Пастернака","category":"culture","link":"https://goslitmuz.ru/museums/dom-muzey-b-l-pasternaka/","description":"Дом-музей, в котором Пастернак жил с 1939 года. Интерьер сохранился практически в том же виде, как при жизни писателя.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774183953499x341692929068118800/photo_2026-03-22_15-52-15.jpg"},
{"id":"r18","title":"Surf Brothers — школа сёрфинга в Сколково","category":"active","link":"https://skolkovo.surfbrothers.ru/","description":"Занятия на волне с тренером в Сколково, возможность поехать в сёрф-трип. Кроме тренировок — фитнес, массаж и спа.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774184258155x868611054037115500/photo_2026-03-22_15-57-19.jpg"},
{"id":"r19","title":"Ресторан Северяне","category":"gastro","link":"https://severyane.moscow/","description":"Современная гастрономия поднимает русские блюда на новый уровень. Авторские напитки и кофе. Дегустации и сезонные меню.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774226221075x348448268959530940/photo_2026-03-23_03-31-16.jpg"},
{"id":"r20","title":"Кинотеатр Coperto — ресторан-кинотеатр","category":"social","link":"https://www.instagram.com/coperto_moscow?igsh=ZHZ0eHN4bm02dDVk","description":"Ресторан-кинотеатр с лакшери-кинозалом на 11 мест и итальянской кухней. Эффект звёздного неба. Классический вариант для свидания.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774190502767x522679910197622500/photo_2026-03-22_17-38-12.jpg"},
{"id":"r21","title":"Театр Crave — кабаре нового формата","category":"culture","link":"https://crave.ru/","description":"Вместо рядов кресел — диваны и столики с шампанским, вместо спектаклей — танцевальный перформанс. Феерические шоу и атмосфера кабаре 21 века.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774190698368x270560911253994180/photo_2026-03-22_17-44-06.jpg"},
{"id":"r22","title":"Стрелковый клуб FireLine","category":"active","link":"https://clubfireline.ru/","description":"Почувствовать себя агентом спецслужб — то, что нужно, чтобы выпустить пар. Обучающие программы для любого уровня подготовки.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774189727370x948995125322799500/photo_2026-03-22_17-27-41.jpg"},
{"id":"r23","title":"Картинг Le Mans","category":"active","link":"https://lemanskarting.ru/","description":"Картинг-клуб с двумя трассами: для взрослых — самая большая среди крытых трасс Москвы; вторая — для детей от пяти лет.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774190123575x312407608383401540/photo_2026-03-22_17-33-54.jpg"},
{"id":"r24","title":"Полёт на вертолёте — Heliport Moscow","category":"active","link":"https://heliport-moscow.ru/","description":"Полёт над городом запомнится надолго. Разные обзорные программы днём или вечером. Можно поуправлять вертолётом самостоятельно под присмотром пилота.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774211031666x161577328859854300/photo_2026-03-22_04-18-01.jpg"},
{"id":"r25","title":"Atlas — ночной клуб","category":"social","link":"https://atlasmoscow.club/","description":"Один из лучших клубов Москвы. Атмосфера вечного праздника. Превосходная музыка, световые инсталляции, разнообразие авторских коктейлей.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774192328844x392480223121425300/photo_2026-03-22_18-10-09.jpg"},
{"id":"r26","title":"Электротеатр Станиславский","category":"culture","link":"https://electrotheatre.ru/","description":"Авангардные спектакли: «Тартюф» в виде футуристического триллера, мультимедийная опера «Curiosity», вдохновлённая твиттером марсохода.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774192636552x269160399784191140/photo_2026-03-22_18-16-28.jpg"},
{"id":"r27","title":"Театр им. Моссовета","category":"culture","link":"https://mossoveta.ru/","description":"Один из старейших театров Москвы. Спектакли по классической литературе и современные постановки от режиссёра Евгения Марчелли.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774192853685x774570487373888400/photo_2026-03-22_18-18-26.jpg"},
{"id":"r28","title":"Люмьер-Холл: выставка Фриды Кало","category":"culture","link":"https://lumierehall.ru/frida","description":"Мультимедийная выставка представляет творчество Фриды Кало в масштабных проекциях. Дополнено музыкой, архивными фото и текстами из дневников.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774215734392x711653466258843100/photo_2026-03-23_00-41-29.jpg"},
{"id":"r29","title":"Третьяковка: выставка «Авангард и икона»","category":"culture","link":"https://www.tretyakovgallery.ru/exhibitions/o/avangard-i-ikona/","description":"Выставка исследует влияние средневекового и народного искусства на формирование русского авангарда. Диалог икон и работ художников начала XX века.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774216114823x199789869336577400/photo_2026-03-23_00-47-17.jpg"},
{"id":"r30","title":"Одеон: шоу-ужин «Закат»","category":"social","link":"https://zakat.odeon.show/","description":"Бродвейский мюзикл встречается с изысканным ужином. Хиты 90-х и 2000-х, интерактивные элементы и авторский ужин от ресторана Pinskiy&Co.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774216280870x281303953483512450/photo_2026-03-23_00-50-15.jpg"},
{"id":"r31","title":"Гончарная мастерская с росписью","category":"creative","link":"https://house-of-arts.ru/goncharnoe-delo-s-rospisyu","description":"Работа на гончарном круге или создание изделия с мастером и росписью ангобами. После двух обжигов с прозрачной глазурью ваше творение станет элементом интерьера.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774215056491x963671686765734700/photo_2026-03-23_00-30-28.jpg"},
{"id":"r32","title":"Аптекарский огород — Ботанический сад МГУ","category":"walk","link":"https://hortus.msu.ru/","description":"Хищные растения, бананы-гиганты, кувшинки с двухметровыми листьями. В оранжереях — лайв-концерты классической, джазовой и рок-музыки.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774217647646x774027049487069200/photo_2026-03-23_01-13-52.jpg"},
{"id":"r33","title":"Студия йоги и танца High Level","category":"active","link":"https://highlevel.moscow/","description":"Более 30 направлений йоги и танцев с профессионалами. Для тех, у кого бессонница, — ночная Гонг медитация от заката до рассвета.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774186642936x397625128562913340/photo_2026-03-22_16-36-15.jpg"},
{"id":"r34","title":"Oldich Art — студия скульптуры и графики","category":"creative","link":"https://oldich.art/","description":"Классы по скульптуре и графике для профи и новичков. Однодневные мастер-классы и курсы с детальным обучением работе с формой, рельефом и цветом.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774186936334x750865728838723200/photo_2026-03-22_16-40-35.jpg"},
{"id":"r35","title":"Студия создания парфюма","category":"creative","link":"https://www.instagram.com/perfume.project?igsh=YXd1eGJzNmhyc2Y5","description":"Тематические мастер-классы по созданию собственных духов. На индивидуальной практике профессиональный парфюмер поможет создать аромат, подчёркивающий ваш характер.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774196342478x677237449267982800/photo_2026-03-22_19-03-51.jpg"},
{"id":"r36","title":"ZU art — студия живописи","category":"creative","link":"https://zuart.ru/","description":"Студия живописи с арт-вечеринками, мастер-классами по спиртовым чернилам, жидкому акрилу и аква-скетчингу. Можно забронировать арт-свидание на двоих.","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774196619632x210048118222644800/photo_2026-03-22_19-21-10.jpg"},
]

# Мероприятия с фиксированными датами для раздела "Ближайшие"
DATED_EVENTS=[
{"date":"2026-03-28","title":"Музей русского импрессионизма","category":"culture","link":"https://www.rusimp.su/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773956502593x210373659989452350/%D0%BC%D1%80%D0%B8.jpeg"},
{"date":"2026-03-28","title":"Camera Show — живой перформанс","category":"culture","link":"https://camerashow.ru/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773964682478x190169253168827040/%D0%BA%D0%B0%D0%BC%D0%B5%D1%80%D0%B0.jpeg"},
{"date":"2026-03-28","title":"Bungee Workout — батутный фитнес","category":"active","link":"https://bungeeworkout.ru/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773965724699x681343066649046800/%D1%84%D0%B8%D1%82%D0%BD%D0%B5%D1%81.jpeg"},
{"date":"2026-03-28","title":"Одеон: шоу-ужин «Закат»","category":"social","link":"https://zakat.odeon.show/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774216280870x281303953483512450/photo_2026-03-23_00-50-15.jpg"},
{"date":"2026-03-29","title":"Chalet Studio — гончарная мастерская","category":"creative","link":"https://www.instagram.com/chaletstudio?igsh=MTNobWU2d2lzd3NrYw==","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774180894068x809933762766639400/photo_2026-03-22_15-01-13.jpg"},
{"date":"2026-03-29","title":"Rock the Cycle — велотренировки под музыку","category":"active","link":"https://www.instagram.com/rockthecycle.ru?igsh=OTZnZndjemh2ZTVp","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773968498273x261731730033293540/%D1%80%D0%BA%D0%B7%D1%81%D0%BA%D0%BB.jpeg"},
{"date":"2026-03-29","title":"WellWell Bistro — живой джаз","category":"social","link":"https://www.instagram.com/wellwell.music?igsh=dTRtemZuejNwcGJn","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773968731764x552138127126401860/%D0%B2%D0%B2.jpeg"},
{"date":"2026-03-29","title":"Театр Crave — кабаре","category":"culture","link":"https://crave.ru/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774190698368x270560911253994180/photo_2026-03-22_17-44-06.jpg"},
{"date":"2026-03-30","title":"Третьяковка: выставка «Авангард и икона»","category":"culture","link":"https://www.tretyakovgallery.ru/exhibitions/o/avangard-i-ikona/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774216114823x199789869336577400/photo_2026-03-23_00-47-17.jpg"},
{"date":"2026-03-30","title":"Гончарная мастерская с росписью","category":"creative","link":"https://house-of-arts.ru/goncharnoe-delo-s-rospisyu","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774215056491x963671686765734700/photo_2026-03-23_00-30-28.jpg"},
{"date":"2026-03-30","title":"Гольф на Красном Октябре","category":"active","link":"https://golf.ru/where_to_play/g-t-na-karasnom-okt/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774226477956x525450478102811970/photo_2026-03-23_03-41-06.jpg"},
{"date":"2026-03-30","title":"Deep Fried Friends — бар и клуб","category":"gastro","link":"https://deepfriedfriends.ru/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773966397478x655833722551879600/%D0%B4%D1%84%D1%84.jpeg"},
{"date":"2026-03-31","title":"Люмьер-Холл: выставка Фриды Кало","category":"culture","link":"https://lumierehall.ru/frida","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774215734392x711653466258843100/photo_2026-03-23_00-41-29.jpg"},
{"date":"2026-03-31","title":"ZU art — студия живописи","category":"creative","link":"https://zuart.ru/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774196619632x210048118222644800/photo_2026-03-22_19-21-10.jpg"},
{"date":"2026-03-31","title":"Картинг Le Mans","category":"active","link":"https://lemanskarting.ru/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774190123575x312407608383401540/photo_2026-03-22_17-33-54.jpg"},
{"date":"2026-03-31","title":"Одеон: шоу-ужин «Закат»","category":"social","link":"https://zakat.odeon.show/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774216280870x281303953483512450/photo_2026-03-23_00-50-15.jpg"},
{"date":"2026-04-01","title":"Электротеатр Станиславский","category":"culture","link":"https://electrotheatre.ru/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774192636552x269160399784191140/photo_2026-03-22_18-16-28.jpg"},
{"date":"2026-04-01","title":"Студия создания парфюма","category":"creative","link":"https://www.instagram.com/perfume.project?igsh=YXd1eGJzNmhyc2Y5","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774196342478x677237449267982800/photo_2026-03-22_19-03-51.jpg"},
{"date":"2026-04-01","title":"Полёт на вертолёте — Heliport Moscow","category":"active","link":"https://heliport-moscow.ru/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774211031666x161577328859854300/photo_2026-03-22_04-18-01.jpg"},
{"date":"2026-04-01","title":"Where to Hide — закрытый клуб","category":"social","link":"https://www.instagram.com/wheretohideinmoscow?igsh=Nzl0bzVwcW9kYTMz","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773966756737x978088210533710600/%D1%85%D0%B4.jpeg"},
{"date":"2026-04-02","title":"Музей русского импрессионизма","category":"culture","link":"https://www.rusimp.su/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1773956502593x210373659989452350/%D0%BC%D1%80%D0%B8.jpeg"},
{"date":"2026-04-02","title":"Oldich Art — скульптура и графика","category":"creative","link":"https://oldich.art/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774186936334x750865728838723200/photo_2026-03-22_16-40-35.jpg"},
{"date":"2026-04-02","title":"Аптекарский огород МГУ","category":"walk","link":"https://hortus.msu.ru/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774217647646x774027049487069200/photo_2026-03-23_01-13-52.jpg"},
{"date":"2026-04-02","title":"Atlas — ночной клуб","category":"social","link":"https://atlasmoscow.club/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774192328844x392480223121425300/photo_2026-03-22_18-10-09.jpg"},
{"date":"2026-04-02","title":"Ресторан Северяне","category":"gastro","link":"https://severyane.moscow/","image":"https://ae1618aba8e418fbd4029cd98502aa32.cdn.bubble.io/f1774226221075x348448268959530940/photo_2026-03-23_03-31-16.jpg"},
]

MONTHS_GEN=["","января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"]
MONTHS_SH=["","янв","фев","мар","апр","май","июн","июл","авг","сен","окт","ноя","дек"]

def get_upcoming():
    now=datetime.now(MOSCOW)
    today=now.strftime("%Y-%m-%d")
    tomorrow=(now+timedelta(days=1)).strftime("%Y-%m-%d")
    result=[]
    for e in DATED_EVENTS:
        # Показываем только сегодня и завтра
        if e["date"] not in (today, tomorrow):
            continue
        if e["date"]==today:
            # Сегодняшние — только если время ещё не прошло
            t=e.get("time","23:59")
            try:
                event_dt=datetime.strptime(f"{today} {t}","%Y-%m-%d %H:%M")
                if event_dt<now:
                    continue
            except:
                pass
        result.append(e)
    result=sorted(result,key=lambda x:x["date"])
    if not result:
        return REAL_EVENTS
    return result

SUPPORT_MESSAGE=0
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

WELCOME=("👋 Привет! Я бот *Outly* — твой помощник в планировании досуга в Москве.\n\n"
"Помогу найти мероприятия по интересам или довериться судьбе 🎲\n\n"
"Выбери, с чего начнём 👇")

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗂 Как подобрать досуг по фильтрам",callback_data="filter_help")],
        [InlineKeyboardButton("🎲 Доверься судьбе",callback_data="random_event")],
        [InlineKeyboardButton("📋 Ближайшие мероприятия",callback_data="events_list")],
        [InlineKeyboardButton("🔖 Где найти тематические подборки",callback_data="collections")],
        [InlineKeyboardButton("👤 Профиль",callback_data="profile")],
        [InlineKeyboardButton("💬 Поддержка",callback_data="support")],
        [InlineKeyboardButton("🌐 Открыть Outly",url=OUTLY_URL)],
    ])

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(WELCOME,parse_mode="Markdown",reply_markup=main_menu())
    else:
        chat_id=update.callback_query.message.chat_id
        await update.callback_query.answer()
        try:
            await update.callback_query.edit_message_text(WELCOME,parse_mode="Markdown",reply_markup=main_menu())
        except Exception:
            try: await update.callback_query.message.delete()
            except: pass
            await context.bot.send_message(chat_id=chat_id,text=WELCOME,parse_mode="Markdown",reply_markup=main_menu())

async def back_main(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    chat_id=update.callback_query.message.chat_id
    try:
        await update.callback_query.edit_message_text(WELCOME,parse_mode="Markdown",reply_markup=main_menu())
    except Exception:
        try: await update.callback_query.message.delete()
        except: pass
        await context.bot.send_message(chat_id=chat_id,text=WELCOME,parse_mode="Markdown",reply_markup=main_menu())

async def filter_help(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    text=("🗂 *Как подобрать досуг по фильтрам на Outly*\n\n"
          "Всё просто — следуй этим шагам:\n\n"
          "1️⃣ Перейди на сайт Outly по кнопке ниже\n\n"
          "2️⃣ На главной странице выбери *формат досуга*: культурный досуг, творчество, активный отдых, прогулки, светские мероприятия или гастрономический досуг\n\n"
          "3️⃣ Укажи *город* и *дату* — выбери день, когда хочешь провести время\n\n"
          "4️⃣ Нажми *«Показать варианты»* — сайт покажет все подходящие мероприятия\n\n"
          "5️⃣ Нажми на любое мероприятие, чтобы увидеть подробное описание, место и время\n\n"
          "🎯 Фильтры помогают найти именно то, что подойдёт тебе сегодня!")
    await update.callback_query.edit_message_text(text,parse_mode="Markdown",reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Перейти на Outly и подобрать досуг",url=OUTLY_URL)],
        [InlineKeyboardButton("🔙 В главное меню",callback_data="back_main")],
    ]))

# ── ДОВЕРЬСЯ СУДЬБЕ — только реальные мероприятия с картинками и ссылками
async def random_event(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    chat_id=update.callback_query.message.chat_id
    await update.callback_query.delete_message()
    e=random.choice(REAL_EVENTS)
    cat_lbl=CATEGORIES.get(e.get("category",""),"🎯")
    text=(f"🎲 *Судьба выбрала для тебя:*\n\n*{e['title']}*\n{cat_lbl}\n\n_{e['description']}_\n\n"
          "_Иногда лучшие вечера — незапланированные_ ✨")
    buttons=[[InlineKeyboardButton("🌐 Подробнее и запись",url=e["link"])],
             [InlineKeyboardButton("🎲 Ещё раз!",callback_data="random_event")],
             [InlineKeyboardButton("🔙 В главное меню",callback_data="back_main")]]
    kb=InlineKeyboardMarkup(buttons)
    try:
        await context.bot.send_photo(chat_id=chat_id,photo=e["image"],caption=text,parse_mode="Markdown",reply_markup=kb)
    except:
        await context.bot.send_message(chat_id=chat_id,text=text,parse_mode="Markdown",reply_markup=kb)

# ── БЛИЖАЙШИЕ МЕРОПРИЯТИЯ — список одним сообщением
async def events_list(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    events=get_upcoming()
    if not events:
        await update.callback_query.edit_message_text("📋 Пока нет мероприятий.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад",callback_data="back_main")]]))
        return
    text="📋 *Ближайшие мероприятия в Москве:*\n\n"
    prev_date=""
    for e in events:
        cat_lbl=CATEGORIES.get(e.get("category",""),"🎯")
        if e.get("date") and e.get("date")!=prev_date:
            try:
                dd=datetime.strptime(e["date"],"%Y-%m-%d")
                text+=f"\n📅 *{dd.day} {MONTHS_GEN[dd.month]}*\n"
            except: pass
            prev_date=e.get("date","")
        link=e.get("link","")
        if link:
            text+=f"• [{e['title']}]({link}) — {cat_lbl}\n"
        else:
            text+=f"• *{e['title']}* — {cat_lbl}\n"
    await update.callback_query.edit_message_text(text,parse_mode="Markdown",
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Все мероприятия на сайте",url=OUTLY_URL)],
        [InlineKeyboardButton("🔙 В главное меню",callback_data="back_main")],
    ]))

# ── ТЕМАТИЧЕСКИЕ ПОДБОРКИ
async def collections(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    text=("🔖 *Где найти тематические подборки на Outly*\n\n"
          "На сайте Outly есть раздел *«Готовые идеи»* — тематические подборки мероприятий и мест для вашего отдыха.\n\n"
          "📌 *Как найти:*\n"
          "1️⃣ Перейди на сайт Outly по кнопке ниже\n"
          "2️⃣ На главной странице найди кнопку *«Готовые идеи»*\n"
          "3️⃣ Нажми на неё — откроется список тематических подборок\n\n"
          "🎨 *Что внутри:*\n"
          "На данный момент доступны три подборки:\n"
          "• *Куда пойти на свидание* — идеи для романтического вечера вдвоём\n"
          "• *Небанальные музеи* — нестандартные музейные площадки Москвы\n"
          "• *День с собой* — идеи для качественного времени наедине с собой")
    await update.callback_query.edit_message_text(text,parse_mode="Markdown",reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Открыть Outly и найти подборки",url=OUTLY_URL)],
        [InlineKeyboardButton("🔙 В главное меню",callback_data="back_main")],
    ]))

# ── ПРОФИЛЬ
async def profile_show(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    text=("👤 *Профиль*\n\n"
          "Твой профиль находится в разделе *«Профиль»* на сайте Outly.\n\n"
          "Там ты можешь:\n"
          "• Посмотреть избранные мероприятия\n"
          "• Дополнить и отредактировать информацию о себе\n"
          "• Управлять своими предпочтениями\n\n"
          "👇 *Перейти в профиль:*")
    await update.callback_query.edit_message_text(text,parse_mode="Markdown",reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Нажми сюда — открыть профиль",url=OUTLY_URL)],
        [InlineKeyboardButton("🔙 В главное меню",callback_data="back_main")],
    ]))

# ── ПОДДЕРЖКА
async def support_start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "💬 *Поддержка*\n\nНапиши свой вопрос или проблему — менеджер команды Outly ответит в ближайшее время:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена",callback_data="back_main")]]))
    return SUPPORT_MESSAGE

async def support_receive(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user=update.effective_user
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID,
        text=f"📩 *Обращение в поддержку*\n\nОт: {user.full_name} (@{user.username or '—'}, ID: {user.id})\n\n{update.message.text}",
        parse_mode="Markdown")
    await update.message.reply_text(
        "✅ *Спасибо за обращение!*\n\nВаш запрос доставлен и будет рассмотрен менеджером команды Outly в ближайшее время.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 В главное меню",callback_data="back_main")]]))
    return ConversationHandler.END

async def post_init(app):
    await app.bot.set_my_commands([BotCommand("start","Главное меню")])

def main():
    app=Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(support_start,pattern="^support$")],
        states={SUPPORT_MESSAGE:[MessageHandler(filters.TEXT&~filters.COMMAND,support_receive)]},
        fallbacks=[CallbackQueryHandler(back_main,pattern="^back_main$")],per_message=False))
    app.add_handler(CallbackQueryHandler(filter_help,pattern="^filter_help$"))
    app.add_handler(CallbackQueryHandler(random_event,pattern="^random_event$"))
    app.add_handler(CallbackQueryHandler(events_list,pattern="^events_list$"))
    app.add_handler(CallbackQueryHandler(collections,pattern="^collections$"))
    app.add_handler(CallbackQueryHandler(profile_show,pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(back_main,pattern="^back_main$"))
    logger.info("Outly бот запущен 🚀")
    app.run_polling()

if __name__=="__main__":
    main()
