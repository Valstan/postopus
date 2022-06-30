import yadisk

import config

session = config.session

y = yadisk.YaDisk(token=session['YANDEX_DISK_TOKEN'])
# print(y.check_token())  # Проверим токен

y.mkdir("/test") # Создать папку
y.upload("file1.txt", "/test/file1.txt")  # Загружает первый файл
y.upload("file2.txt", "/test/file2.txt")  # Загружает второй файл
