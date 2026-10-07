#!/bin/bash
# Вариант VFS 1: минимальный (только motd)
cd "$(dirname "$0")/.." || exit 1
python src/make_vfs.py min
python src/emulator.py --vfs vfs_min.zip --script tests/test_vfs_min.sh
echo "Код возврата: $?"