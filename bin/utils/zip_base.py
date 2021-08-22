import zipfile
import os


def zip_base():
    for folder_name in ('mi', 'dran'):
        z = zipfile.ZipFile('bases/' + folder_name + '.zip', 'w')  # Создание нового архива
        for root, dirs, files in os.walk('bases/' + folder_name):  # Список всех файлов и папок в директории folder
            for file in files:
                z.write(os.path.join(root, file))  # Создание относительных путей и запись файлов в архив
        z.close()
