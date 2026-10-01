#!/bin/bash
# Вариант VFS 2: несколько файлов в корне (без motd)
# Последняя команда скрипта неизвестна -> остановка на первой ошибке
python make_vfs.py files
python emulator.py --vfs vfs_files.zip --script test_vfs_files.sh
echo "Код возврата: $?"