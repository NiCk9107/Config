#!/bin/bash
# Демонстрация обработки ошибок: неизвестная команда, пробел в начале,
# несуществующий путь, неверные аргументы
python make_vfs.py deep
printf 'pwd\n ls\ncd /nonexistent\ncat\ncat /missing.txt\nls\nexit\n' | python emulator.py --vfs vfs_deep.zip
echo "Код возврата: $?"