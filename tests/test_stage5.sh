# Тестирование команд cp и rmdir (Этап 5)

echo " Тест cp: копирование файла "
cp /docs/readme.txt /docs/readme_copy.txt
ls /docs

echo " Тест cp: копирование в каталог "
cp /docs/readme.txt /home/user/
ls /home/user

echo " Тест cp: ошибка (несуществующий источник) "
cp /nonexistent /docs/file.txt

echo " Тест cp: ошибка (каталог нельзя копировать) "
cp /docs /home/user/docs_copy

echo " Тест rmdir: удаление пустого каталога "
rmdir /empty_dir
ls /

echo " Тест rmdir: ошибка (каталог не пуст) "
rmdir /docs

echo " Тест rmdir: ошибка (несуществующий каталог) "
rmdir /nonexistent

echo " Тест rmdir: ошибка (нельзя удалить корень) "
rmdir /

echo " Тест rmdir: ошибка (это файл, не каталог) "
rmdir /motd

exit