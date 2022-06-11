cron_schedule = (
    # mi
    '05 7,8,10,12,14-23 mi_novost',
    '15 9,13 mi_repost_reklama',
    '15 7,12,18,20,22 mi_addons',
    '15 21 mi_repost_krugozor',
    '15 19 mi_repost_aprel',
    '20 6-23 mi_repost_me',
    # dran
    '25 7,9,12,18,20,22 dran_novost',
    '25 6,8,11,15,19,21,23 dran_addons',
    # sbor reklamy
    '40 5-22 dran_reklama',
    '50 6-22 mi_reklama')

tb_url = 'https://api.telegram.org/bot'
tb_params = {'chat_id': -1001746966097}  # канал Тест-тест-тест2000