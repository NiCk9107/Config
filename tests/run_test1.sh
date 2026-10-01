#!/bin/bash
# Тестирование: корректный скрипт + указание VFS и скрипта
echo "Запуск теста 1: корректные команды"
python emulator.py --vfs ./vfs --script test1.sh
echo "Код возврата: $?"