bases = 'bases/'
fbase = 'base.json'
fimage = 'image'
bezfoto = 'bezfoto'
insta_photo_path = bases + 'insta_photo/'
insta_photo_path_manual = bases + 'insta_photo_manual/'
keys = {
    'm': 'mi/',
    'd': 'dran/',
    "standart": ('mi', 'dran', 'test'),
    "reklama": 'reklama',  # Используется для двух разных скриптов
    "novost": "novost",
    "krugozor": 'krugozor',
    "aprel": 'aprel',
    "post_me": 'main',
    "instagram": 'instagram'
}

repost_accounts = ("valstan", "brigadir")

size_base_old_posts = 500  # количество
difference_old_posts = 259200  # в секундах (259200 секунд это 3 дня)

delete_bad_simbol = ' ,\n('

delete_word = (
    'Админ разместите анонимно объявление, спасибо. ', 'Админ пропусти', 'админу добра', 'админ ', 'Админу',
    'Не анонимно', 'анонимно', 'ананимно', 'ананимна', 'аноним',
    'Не анон', 'неанон', 'Анон)', 'анон.', 'анон',
    'пожалуйста', 'пожалуйсто', 'пожалуста',
    '()', '(, )', '( )'
)

delete_msg_blacklist = (
    'Кошечка',
    'ТЦ Добреев',
    'в сети магазинов',
    'Быстрая Оплата Наличными',
    '5638568',
    'Возим мебель из Кирова',
    'реклама в первом',
    'привита от бешенства',
    'солевую жидкость',
    'работадома',
    'удаленнаяработа',
    'администраторнаудаленке',
    'онлайнофис',
    'маманаудаленке',
    'мамавдекрете',
    'работаонлайн',
    'свободныйграфик',
    '586-62-02',
    'Администратор на удаленку',
    'Расписание киносеансов',
    '8020419',
    'Девушка от 25',
    'Оплата от 20 тыс',
    'услуги массажного кабинета',
    '5043506',
    '6705691',
    '707-80-00',
    '503-89-29',
    "легендарный бальзам",
    "первом малмыжском",
    "техно добреев",
    "добреев",
    "добреев малмыж",
    "3870096",
    "комсомольская д.50",
    "доход от 20 000",
    "реализация материнского капитала",
    "8718228",
    "1852040",
    "7246551",
    "7174175",
    "520-7319",
    "щенки",
    "орифлэйм",
    "первый заказ",
    "nestogen",
    "продаю смесь",
    "ул.почтовая 10",
    "кальций в капсулах",
    "витамины для детей",
    "по 850 р",
    "337-31-19",
    "7328566",
    "club46644578",
    "0336666",
    "1300 за все",
    "charon baby",
    "салон мебели",
    "5154341",
    "любой аромат",
    "ремонт цоколя здания администрации города малмыжа",
    "закупаю коров на мясо",
    "мой брат попал в беду",
    "iqos",
    "айкос",
    "вейп",
    "ploom",
    "кальян",
    "джул",
    "новый взгляд",
    "всё по карману",
    "освр",
    "частный клининг",
    "снова в наличии",
    "николай дубравин",
    "узнай своих поклонниц",
    "запустили производство профнастила",
    "большое поступление",
    "закажу второй портрет",
    "метелица",
    "magiccanvas24",
    "оплата при получении",
    "к. маркса 78",
    "карла маркса,92",
    "карла маркса, 92",
    "к. маркса, 20",
    "к-маркса 88",
    "к-маркса, 88",
    "828-33-85",
    "9258077",
    "наши именинники",
    "любой продукт",
    "любое фото",
    "1 фото",
    "любое средство",
    "1фото",
    "каждая по 180",
    "всё по 500",
    "каждое по 150",
    "любая за 350",
    "любая по 350",
    "150р!",
    "любой, 180р!!!",
    "скидка!!!!350р!",
    "все по 100р",
    "300р!",
    "950р",
    "любая 300р!",
    "500р!",
    "ночной крем",
    "в наличии 800р!",
    "любое средство - 150р",
    "пробники",
    "пробник",
    "выезжаем в любой регион россии",
    "банкротство",
    "котят",
    "котята",
    "кошка",
    "кошку",
    "котенок",
    "котенка",
    "кошечка",
    "кошечку",
    "котик",
    "котёнка",
    "мышеловка",
    "кот",
    "кошечек",
    "собака",
    "собаку",
    "собачка",
    "собачку",
    "щенка",
    "щенок",
    "щенков",
    "щенят",
    "щеночка",
    "пёс",
    "пёсики",
    "песики",
    "котики",
    "736-56-00",
    "туалетная вода",
    "передержку",
    "красная весна",
    "кургинян",
    "замалчивается",
    "замалчивает",
    "любая шампунь",
    "бурение скважин",
    "по 145р",
    "любое мыло",
    "красное-белое",
    "брала для мамы массажную подушку",
    "второй этаж флагман",
    "любое средство-150",
    "массажная подушка",
    "распродажа",
    "ждем вас за покупками",
    "видеоуроки на заказ",
    "зимний стиль",
    "кодовые замки",
    "профессиональный спил",
    "приглашаем за покупками",
    "группу совместных покупок",
    "покупать товары",
    "с нами выгодно",
    "интересные закупки",
    "пункт выдачи в г.малмыж",
    "цены снижены",
    "вышел новый айфон",
    "minifit",
    "стройбаза",
    "строймаркет",
    "посудный рай",
    "техно малмыж",
    "строймаркете",
    "3383485",
    "евростиль",
    "20637",
    "336-49-56",
    "асхатзянов",
    "89127190797",
    "89823903850",
    "витамины красоты",
    "сельхоз объявления по малмыжскому району",
    "бруско",
    "продам жижу",
    "любой крем для рук",
    "любой детский сироп",
    "детская смесь",
    "по 80р",
    "продажа обмен за одну",
    "испаритель",
    "чарон беби",
    "ул. к. маркса, 20",
    "в метелице",
    "2-00-13",
    "метелица - тепло отношений",
    "нахуй",
    "маникюр",
    "наращивание ресниц",
    "охуели",
    "чарон бейби",
    "полировка волос",
    "️нанопластика",
    "89872695944",
    "реклама в сообществе",
    "малмыж к маркса 10",
    "посудов",
    "малмыж интерьер",
    "чернышевского 6",
    "2фото",
    "450р",
    "4фото",
    "350р",
    "200р",
    "pasito",
    "медицинский центр \"новый взгляд\"",
    "003237",
    "947-1198",
    "993-6797",
    "опубликуйте",
    "пиздец",
    "2420664",
    "любишь пиво",
    "0389085",
    "выкуп авто",
    "удаленная занятость",
    "наш интернет магазин",
    "без вложений",
    "3250561",
    "доборные элементы",
    "выгодные покупки",
    "сопровождение подписчиков",
    "7181053",
    "касса/бронирование билетов",
    "онлайн консультант"
)

baraban = ["krugozor", "krugozor", "krugozor", "krugozor",
           "prikol", "prikol",
           "music",
           "art"]

conf = {
    "m": {
        "prefix": "m",
        "bag_report": -168172770,
        "post_group": {
            "key": -158787639
        },
        "reklama": {
            "podslushano_malmig": -149841761,
            "obo_vsem_malmig": -89083141,
            "ivan_malmig": 364752344,
            "Почитай Малмыж https://vk.com/baraholkaml": 624118736,
            "Первый Малмыжский https://vk.com/malmiz": -86517261
        },
        "novost": {
            "Дом-Культуры Малмыжа РЦКиД Районный Центр Культуры и Досуга https://vk.com/id234960216": 234960216,
            "Администрация Малмыжского городского поселения https://vk.com/gormalm": -159098271,
            "Газета Сельская правда https://vk.com/public179280169": -179280169,
            "Малмыжский Краеведческий-Музей https://vk.com/id288616707": 288616707,
            "Сообщество предпринимателей Малмыжского района https://vk.com/public133732168": -133732168,
            "Малмыжская детская школа искусств https://vk.com/club124138214": -124138214,
            "Малмыж и Малмыжский район. Ищу тебя. Разыскивает https://vk.com/club166452860": -166452860,
            "Вятка https://vk.com/vyatkakirovtockaru": -84767981,
            "Добровольцы г. Малмыж Создаём Добрый Малмыж https://vk.com/mvolonter": -72660310,
            "Новости Малмыж https://vk.com/club120893935": -120893935,
            "За мост через Вятку https://vk.com/club111892671": -111892671,
            "Малышок-онлайн Детский сад https://vk.com/malyshok.online": -197351557,
            "Малмыжский завод по ремонту дизельных двигателей https://vk.com/rmz43": -195583920,
            "Культура,молодежная политика и спорт г. Малмыж https://vk.com/public165382241": -165382241,
            "Аджимский Дом-Культуры https://vk.com/id420841463": 420841463,
            "МалмыЖ https://vk.com/club9363816": -9363816,
            "Игорь Степанов https://vk.com/stepanoigo": 225359471
        },
        "prikol": {
            "СМЕШНОЕ ВИДЕО Самый позитивный паблик ВК https://vk.com/smexo": -132265,
            "Стань учёным! А ты возьми и стань! https://vk.com/becomeascientist": -197866857
        },
        "krugozor": {
            "Время - вперёд! Только хорошие новости! https://vk.com/rossiya_segodnya": -65614662,
            "SciTopus Популяризируем популяризаторов https://vk.com/scitopus": -112289703,
            "НауЧпок Разные штуки по науке https://vk.com/nowchpok": -73083424,
            "The Batrachospermum Magazine журнальчик-водоросль https://vk.com/batrachospermum": -85330
        },
        "music": {
            "МУЗЫКА. МОТОР! Русские видеоклипы https://vk.com/russianmusicvideo": -37343149,
            "МУЗЫКА НУЛЕВЫХ СССР (СУПЕРДИСКОТЕКА 90х - 2000х) https://vk.com/public50638629": -50638629,
            "Музыка 70-х 80-х 90-х 2000-х.Саундтреки ! https://vk.com/public187135362": -187135362
        },
        "art": {
            "Культура & Искусство Журнал для умных и творческих https://vk.com/public31786047": -31786047,
            "Удивительный мир https://vk.com/ourmagicalworld": -42320333,
            "Случайный Ренессанс Искусство повсюду https://vk.com/accidental_renaissance": -92583139,
            "wizard https://vk.com/public95775916": -95775916
        },
        "podpisi": {
            "zagolovok": {
                "art": "&#127752;",
                "prikol": "&#9786;&#128515;",
                "novost": "&#128221;",
                "krugozor": "&#128225;ЗНАНИЯ&#128300;",
                "music": "&#127932;&#127932;&#127932;",
                "reklama": "&#128276;",
                "bezfoto": "&#128165;ДЕСЯТКА"
            },
            "heshteg": {
                "art": "\n#КрасотаСпасетМир",
                "prikol": "\n#УраПерерывчик",
                "novost": "\n#НовостиМалмыжа",
                "krugozor": "\n#Кругозор",
                "music": "\n#Музыка",
                "reklama": "\n#ОбъявленияМалмыж"
            },
            "final": "\nНажми лайк &#10084;&#65039; и поделись новостью с друзьями &#128071;",
            "image_desatka": 'photo-158787639_457242342'
        }
    },
    "d": {
        "prefix": "d",
        "bag_report": -168172770,
        "post_group": {
            "key": -187462239
        },
        "reklama": {
            "podslushano_malmig": -149841761,
            "obo_vsem_malmig": -89083141,
            "ivan_malmig": 364752344,
            "Почитай Малмыж https://vk.com/baraholkaml": 624118736,
            "Первый Малмыжский https://vk.com/malmiz": -86517261
        },
        "novost": {
            "Дом-Культуры Малмыжа РЦКиД Районный Центр Культуры и Досуга https://vk.com/id234960216": 234960216,
            "Администрация Малмыжского городского поселения https://vk.com/gormalm": -159098271,
            "Газета Сельская правда https://vk.com/public179280169": -179280169,
            "Малмыжский Краеведческий-Музей https://vk.com/id288616707": 288616707,
            "Сообщество предпринимателей Малмыжского района https://vk.com/public133732168": -133732168,
            "Малмыжская детская школа искусств https://vk.com/club124138214": -124138214,
            "Малмыж и Малмыжский район. Ищу тебя. Разыскивает https://vk.com/club166452860": -166452860,
            "Вятка https://vk.com/vyatkakirovtockaru": -84767981,
            "Добровольцы г. Малмыж Создаём Добрый Малмыж https://vk.com/mvolonter": -72660310,
            "Новости Малмыж https://vk.com/club120893935": -120893935,
            "За мост через Вятку https://vk.com/club111892671": -111892671,
            "Малышок-онлайн Детский сад https://vk.com/malyshok.online": -197351557,
            "Малмыжский завод по ремонту дизельных двигателей https://vk.com/rmz43": -195583920,
            "Культура,молодежная политика и спорт г. Малмыж https://vk.com/public165382241": -165382241,
            "Аджимский Дом-Культуры https://vk.com/id420841463": 420841463,
            "МалмыЖ https://vk.com/club9363816": -9363816,
            "Игорь Степанов https://vk.com/stepanoigo": 225359471
        },
        "prikol": {
            "УДИВИТЕЛЬНЫЙ МИР Be awesome https://vk.com/public94559915": -94559915
        },
        "krugozor": {
            "batrachospermum": -85330,
            "scitopus": -112289703,
            "vremya_vpered": -65614662
        },
        "music": {
            "JPG MUSIC / Годная музыка и сохраненки https://vk.com/detroitmusic": -60902530,
            "novye_klipy": -44497275,
            "muzyka": -34384434,
            "popularnay_muzyka": -35983383
        },
        "art": {
            "Культура & Искусство Журнал для умных и творческих https://vk.com/public31786047": -31786047,
            "Удивительный мир Самое удивительное сообщество во Вселенной! https://vk.com/ourmagicalworld": -42320333,
            "wizard https://vk.com/public95775916": -95775916
        },
        "podpisi": {
            "zagolovok": {
                "art": "&#128396;",
                "prikol": "&#128515;&#129315;",
                "novost": "&#128221;",
                "krugozor": "&#128640;",
                "music": "&#127932;",
                "reklama": "&#128276;",
                "bezfoto": "&#128165;"
            },
            "heshteg": {
                "art": "",
                "prikol": "",
                "novost": "",
                "krugozor": "",
                "music": "",
                "reklama": "",
                "bezfoto": "",
                "sort_novost": "",
                "sort_reklama": ""
            },
            "final": "\nНажми лайк &#10084;&#65039; и поделись с друзьями &#128071;",
            "image_desatka": ''
        }
    }
}

if __name__ == '__main__':
    pass
