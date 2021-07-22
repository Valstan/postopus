bases = 'bases/'
fbase = 'base.json'
fimage = 'image'
prefixbase = 'm', 'd'
pointer = [
    '&#10145;', '&#128077;', '&#128226;', '&#128172;', '&#128161;', '&#9999;', '&#10002;', '&#10004;',
    '&#9193;', '&#9654;', '&#128266;', '&#9997;', '&#128073;', '&#128483;', '*&#8419;'
]
delete_msg_blacklist = [
    'ремонт цоколя здания администрации города малмыжа', 'закупаю коров на мясо', 'мой брат попал в беду',
    'iqos', 'айкос', 'вейп', 'ploom', 'кальян', 'джул', 'новый взгляд', 'всё по карману', 'освр',
    'частный клининг', 'снова в наличии', 'николай дубравин', 'узнай своих поклонниц',
    'запустили производство профнастила', 'большое поступление', 'закажу второй портрет',
    'метелица', 'magiccanvas24', 'оплата при получении', '8 (83347) 2-00-13',
    'к. маркса 78', 'карла маркса,92', 'карла маркса, 92', 'к. маркса, 20', 'к-маркса 88', 'к-маркса, 88',
    '912-828-33-85', '89229258077', 'наши именинники', 'любой продукт', 'любое фото', '1 фото', 'любое средство',
    '1фото', 'каждая по 180', 'всё по 500', 'каждое по 150', 'любая за 350', 'любая по 350', '150р!',
    'любой, 180р!!!', 'скидка!!!!350р!', 'все по 100р',
    '300р!', '950р', 'любая 300р!', '500р!', 'ночной крем', 'в наличии 800р!', 'любое средство - 150р',
    'пробники', 'пробник', 'выезжаем в любой регион россии', 'банкротство', 'котят', 'котята', 'кошка', 'кошку',
    'котенок', 'котенка', 'кошечка', 'кошечку', 'котик', 'котёнка', 'мышеловка', 'кот', 'кошечек',
    'собака', 'собаку', 'собачка', 'собачку', 'щенка', 'щенок', 'щенков', 'щенки', 'щенят', 'щеночка', 'пёс',
    'пёсики', 'песики', 'котики', '8-912-736-56-00',
    'туалетная вода', 'передержку', 'красная весна', 'кургинян', 'замалчивается', 'замалчивает',
    'любая шампунь', 'бурение скважин', 'по 145р', 'любое мыло', 'красное-белое',
    'брала для мамы массажную подушку', 'второй этаж флагман',
    'любое средство-150', 'массажная подушка', 'всё по карману', 'распродажа', 'ждем вас за покупками',
    'видеоуроки на заказ', 'зимний стиль', 'кодовые замки', 'профессиональный спил',
    'приглашаем за покупками', 'группу совместных покупок', 'покупать товары', 'с нами выгодно', 'интересные закупки',
    'пункт выдачи в г.малмыж', 'цены снижены', 'вышел новый айфон', 'добреев', 'minifit',
    'стройбаза', 'строймаркет', 'посудный рай', 'техно малмыж', 'строймаркете', '89123383485', 'евростиль',
    '88334720637', '8-912-336-49-56', 'асхатзянов', '89127190797', '89823903850', 'витамины красоты',
    'витамины для детей', 'СЕЛЬХОЗ ОБЪЯВЛЕНИЯ ПО МАЛМЫЖСКОМУ РАЙОНУ', 'бруско', 'Продам жижу', 'Любой крем для рук',
    'Любой продукт', 'Любой детский сироп', 'Детская смесь', 'По 80р', 'Продажа обмен за одну', 'испаритель',
    'чарон беби', 'ул. К. Маркса, 20', 'В Метелице', '2-00-13', 'Метелица - тепло отношений', 'нахуй', 'маникюр',
    'наращивание ресниц', 'охуели', 'чарон бейби', 'Полировка волос', '️Нанопластика', '89872695944'
]
delete_word = [
    'Не анонимно',
    'анонимно', 'Анонимно', 'АНОНИМНО', 'ананимно', 'аноним', 'Аноним',
    'пожалуйста', 'Пожалуйста', 'ПОЖАЛУЙСТА', 'пожалуйсто',
    'пожалуста', 'Пожалуста', 'ПОЖАЛУСТА',
    'Не анон', 'не анон', 'НЕ АНОН', 'неанон', 'не АНОН',
    'Анон)', 'АНОН', 'анон', 'Анон',
    'Админу добра', 'админу добра', '()'
]
delete_bad_simbol = ' .!,\n('

size_base_old_posts = 500  # количество
difference_old_posts = 259200  # в секундах (259200 секунд это 3 дня)


if __name__ == '__main__':
    pass
