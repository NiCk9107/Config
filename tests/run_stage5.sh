#!/bin/bash
# Запуск тестов Этапа 5 (cp, rmdir)
cd "$(dirname "$0")/.." || exit 1

# Генерируем VFS с 3 уровнями вложенности и пустым каталогом
python src/make_vfs.py deep

# Запускаем эмулятор с тестовым скриптом
python src/emulator.py --vfs vfs_deep.zip --script tests/test_stage5.sh
echo "Код возврата: $?"