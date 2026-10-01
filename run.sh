@'
#!/bin/bash
# Скрипт запуска эмулятора оболочки
cd "$(dirname "$0")" || exit 1
python src/emulator.py "$@"
'@ | Out-File -FilePath run.sh -Encoding utf8