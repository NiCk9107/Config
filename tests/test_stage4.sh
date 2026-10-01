# Стартовый скрипт для тестирования команд Этапа 4
echo "--- Проверка whoami и date ---"
whoami
date

echo "--- Проверка ls и cd (абсолютные и относительные пути) ---"
ls
cd /docs
ls
cd reports/2026
ls
cd /home/user
ls

echo "Проверка du (размер файлов и каталогов)"
du /docs/readme.txt
du /docs
du /home/user/settings.conf

echo "--- Проверка обработки ошибок ---"
cd /nonexistent_dir
ls /missing_file.txt
du /missing_file.txt
exit