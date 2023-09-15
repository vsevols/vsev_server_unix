# -*- coding: utf-8 -*-

import os
import shutil
import time
import zipfile

def delete_files_with_invalid_slash(path):
    try:
        # Получаем список файлов и директорий в указанной директории
        entries = os.listdir(path)

        for entry in entries:
            entry_path = os.path.join(path, entry)

            # Проверяем, является ли entry файлом и начинается ли имя с "jh\"
            if os.path.isfile(entry_path) and entry.startswith("jh\\"):
                try:
                    # Удаляем файл
                    os.remove(entry_path)
                    print(f"Файл {entry_path} успешно удален.")
                except Exception as e:
                    print(f"Ошибка при удалении файла {entry_path}: {e}")

            # Если entry является директорией, рекурсивно вызываем эту функцию
            # elif os.path.isdir(entry_path):
            # delete_files_with_invalid_slash(entry_path)

    except Exception as e:
        print(f"Произошла ошибка: {e}")

def archive_files_if_low_disk_space(log_dir, archive_dir, threshold_mb):
    try:
        # Получаем информацию о свободном месте на диске
        free_space = shutil.disk_usage(log_dir).free / (1024 * 1024)  # в мегабайтах

        # Если свободного места меньше указанного порога
        if free_space < threshold_mb:
            print(f"Свободное место на диске меньше {threshold_mb} МБ. Начинаем архивирование файлов.")

            # Создаем поддиректорию "arc", если ее нет
            arc_dir = os.path.join(log_dir, "arc")
            os.makedirs(arc_dir, exist_ok=True)

            # Пересчитываем свободное место на диске
            free_space = shutil.disk_usage(log_dir).free / (1024 * 1024)  # в мегабайтах

            # Получаем список файлов в директории "/var/log/jh" и сортируем их по дате
            files = os.listdir(log_dir)
            files.sort(key=lambda x: os.path.getctime(os.path.join(log_dir, x)))

            for file_name in files:
                file_path = os.path.join(log_dir, file_name)
                if os.path.isfile(file_path):
                    # Проверяем, был ли файл создан менее 10 минут назад
                    if (time.time() - os.path.getctime(file_path)) < 600:
                        try:
                            # Удаляем файл
                            os.remove(file_path)
                            print(f"Файл {file_path} успешно удален, так как он был создан менее 10 минут назад.")
                            continue
                        except Exception as e:
                            print(f"Ошибка при удалении файла {file_path}: {e}")

                # Создаем архивный файл с сжатием

                archive_file = os.path.join(arc_dir, f"archive_{time.strftime('%Y%m%d%H%M%S')}.zip")

                with (zipfile.ZipFile(archive_file, 'w', zipfile.ZIP_DEFLATED) as archive):

                    try:

                        # Пытаемся добавить файл в архив

                        archive.write(file_path, os.path.basename(file_path))
                        print(f"Файл {file_path} добавлен в архив {archive_file}")

                        # Удаляем исходный файл
                        os.remove(file_path)
                        print(f"Файл {file_path} удален.")

                    except Exception as e:
                        print(f"Ошибка при архивировании файла {file_path}: {e}")

                    # Если не хватает места для архивации, удаляем исходный файл

                    os.remove(file_path)

                    print(f"Файл {file_path} удален из-за нехватки места на диске.")


                    # Пересчитываем свободное место на диске
                    free_space = shutil.disk_usage(log_dir).free / (1024 * 1024)  # в мегабайтах

            print(f"Свободное место на диске теперь больше {threshold_mb} МБ. Завершаем архивирование.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

def delete_files_in_arc_if_low_disk_space(log_dir, threshold_mb):
    try:
        # Получаем информацию о свободном месте на диске
        free_space = shutil.disk_usage(log_dir).free / (1024 * 1024)  # в мегабайтах

        # Если свободного места меньше указанного порога и папка "arc" существует
        if free_space < threshold_mb:
            arc_dir = os.path.join(log_dir, "arc")

            # Получаем список файлов в директории "arc" и сортируем их по дате
            arc_files = os.listdir(arc_dir)
            arc_files.sort(key=lambda x: os.path.getctime(os.path.join(arc_dir, x)))

            while free_space < threshold_mb and arc_files:
                arc_file = arc_files.pop(0)
                arc_file_path = os.path.join(arc_dir, arc_file)

                try:
                    # Удаляем файл из "arc"
                    os.remove(arc_file_path)
                    print(f"Файл {arc_file_path} успешно удален из 'arc'.")

                    # Пересчитываем свободное место на диске
                    free_space = shutil.disk_usage(log_dir).free / (1024 * 1024)  # в мегабайтах
                except Exception as e:
                    print(f"Ошибка при удалении файла {arc_file_path} из 'arc': {e}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

while True:
    try:
        # Указываем путь к директории "/var/log/"
        log_dir = "/var/log/"

        # Порог свободного места на диске (в МБ)
        threshold_mb = 100

        # Вызываем функцию для удаления файлов с неправильным слешем
        delete_files_with_invalid_slash(log_dir)

        # Вызываем функцию для архивирования файлов, если свободное место недостаточно
        archive_files_if_low_disk_space(log_dir, threshold_mb)

        # Вызываем функцию для удаления файлов из "arc", если не хватает места на диске
        delete_files_in_arc_if_low_disk_space(log_dir, threshold_mb)

        # Приостанавливаем выполнение программы на 10 минут
        time.sleep(600)

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        # Если произошла ошибка, продолжаем выполнение программы
        continue
