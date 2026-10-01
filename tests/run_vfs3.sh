#!/bin/bash
# Вариант VFS 3: не менее 3 уровней файлов и папок
python make_vfs.py deep
python emulator.py --vfs vfs_deep.zip --script test_all.sh
echo "Код возврата: $?"