bases = 'bases/'
fbase = 'base.json'
fimage = 'image'
prefixbase = 'm', 'd'

size_base_old_posts = 500  # количество
difference_old_posts = 259200  # в секундах (259200 секунд это 3 дня)

delete_bad_simbol = ' ,\n('

delete_word = [
    'Админ разместите анонимно объявление, спасибо. ', 'Не анонимно', 'Админ пропусти', 'анонимно',
    'АНОНИМНО', 'ананимно', 'ананимна', 'аноним', 'пожалуйста', 'пожалуйсто', 'пожалуста', 'Не анон',
    'неанон', 'Анон)', 'анон', 'админу добра', 'админ', '()', '(, )', '( )'
]

delete_msg_blacklist = [
    'club46644578', '0336666', '1300 за все', 'Charon Baby', 'Салон Мебели', '5154341'
    'ремонт цоколя здания администрации города малмыжа', 'закупаю коров на мясо', 'мой брат попал в беду',
    'iqos', 'айкос', 'вейп', 'ploom', 'кальян', 'джул', 'новый взгляд', 'всё по карману', 'освр',
    'частный клининг', 'снова в наличии', 'николай дубравин', 'узнай своих поклонниц',
    'запустили производство профнастила', 'большое поступление', 'закажу второй портрет',
    'метелица', 'magiccanvas24', 'оплата при получении',
    'к. маркса 78', 'карла маркса,92', 'карла маркса, 92', 'к. маркса, 20', 'к-маркса 88', 'к-маркса, 88',
    '828-33-85', '9258077', 'наши именинники', 'любой продукт', 'любое фото', '1 фото', 'любое средство',
    '1фото', 'каждая по 180', 'всё по 500', 'каждое по 150', 'любая за 350', 'любая по 350', '150р!',
    'любой, 180р!!!', 'скидка!!!!350р!', 'все по 100р',
    '300р!', '950р', 'любая 300р!', '500р!', 'ночной крем', 'в наличии 800р!', 'любое средство - 150р',
    'пробники', 'пробник', 'выезжаем в любой регион россии', 'банкротство', 'котят', 'котята', 'кошка', 'кошку',
    'котенок', 'котенка', 'кошечка', 'кошечку', 'котик', 'котёнка', 'мышеловка', 'кот', 'кошечек',
    'собака', 'собаку', 'собачка', 'собачку', 'щенка', 'щенок', 'щенков', 'щенки', 'щенят', 'щеночка', 'пёс',
    'пёсики', 'песики', 'котики', '736-56-00',
    'туалетная вода', 'передержку', 'красная весна', 'кургинян', 'замалчивается', 'замалчивает',
    'любая шампунь', 'бурение скважин', 'по 145р', 'любое мыло', 'красное-белое',
    'брала для мамы массажную подушку', 'второй этаж флагман',
    'любое средство-150', 'массажная подушка', 'всё по карману', 'распродажа', 'ждем вас за покупками',
    'видеоуроки на заказ', 'зимний стиль', 'кодовые замки', 'профессиональный спил',
    'приглашаем за покупками', 'группу совместных покупок', 'покупать товары', 'с нами выгодно', 'интересные закупки',
    'пункт выдачи в г.малмыж', 'цены снижены', 'вышел новый айфон', 'добреев', 'minifit',
    'стройбаза', 'строймаркет', 'посудный рай', 'техно малмыж', 'строймаркете', '3383485', 'евростиль',
    '20637', '336-49-56', 'асхатзянов', '89127190797', '89823903850', 'витамины красоты',
    'витамины для детей', 'СЕЛЬХОЗ ОБЪЯВЛЕНИЯ ПО МАЛМЫЖСКОМУ РАЙОНУ', 'бруско', 'Продам жижу', 'Любой крем для рук',
    'Любой продукт', 'Любой детский сироп', 'Детская смесь', 'По 80р', 'Продажа обмен за одну', 'испаритель',
    'чарон беби', 'ул. К. Маркса, 20', 'В Метелице', '2-00-13', 'Метелица - тепло отношений', 'нахуй', 'маникюр',
    'наращивание ресниц', 'охуели', 'чарон бейби', 'Полировка волос', '️Нанопластика', '89872695944',
    'Реклама в сообществе', 'Малмыж К Маркса 10', 'Посудов', 'Малмыж Интерьер', 'Чернышевского 6',
    '2фото', '450р', '4фото', '350р', 'Любое фото', '200р', 'charon baby', 'pasito', 'МЕДИЦИНСКИЙ ЦЕНТР'
    'НОВЫЙ ВЗГЛЯД', '003237', '947-1198', '993-6797', 'Опубликуйте', 'пиздец', '2420664',
    'Любишь пиво', '0389085', 'Выкуп Авто', 'Удаленная занятость', 'наш интернет магазин', 'Без вложений',
    '3250561', 'доборные элементы', 'выгодные покупки', 'сопровождение подписчиков', '7181053',
    'Касса/бронирование билетов', 'онлайн консультант'
]


if __name__ == '__main__':
    pass
