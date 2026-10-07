"""Служебная утилита для создания тестовых ZIP-архивов VFS."""
import base64
import zipfile
import sys

LOGO_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAA"
    "DUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)

VFS_MIN = {
    'motd': "Добро пожаловать в минимальную VFS!\n",
}

VFS_FILES = {
    'readme.txt': "Виртуальная файловая система.\n",
    'notes.txt': "Заметка: VFS загружается в память.\n",
    'logo.bin': base64.b64decode(LOGO_B64),
}

VFS_DEEP = {
    'motd': "Привет! Это VFS с тремя уровнями вложенности.\n",
    'docs/readme.txt': "Документация проекта.\n",
    'docs/reports/2026/q1.txt': "Отчёт за 1 квартал 2026.\n",
    'docs/reports/2026/q2.txt': "Отчёт за 2 квартал.\n",
    'home/user/settings.conf': "theme=dark\nlang=ru\n",
    'home/user/bin/logo.bin': base64.b64decode(LOGO_B64),
    'empty_dir/': b'',
}

VARIANTS = {
    'min': ('vfs_min.zip', VFS_MIN),
    'files': ('vfs_files.zip', VFS_FILES),
    'deep': ('vfs_deep.zip', VFS_DEEP),
}


def build(name, structure):
    """Создает ZIP-архив из переданной структуры данных."""
    with zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED) as z:
        for path, content in structure.items():
            if path.endswith('/'):
                z.writestr(path, b'')
            else:
                if isinstance(content, str):
                    content = content.encode('utf-8')
                z.writestr(path, content)
    print(f"Создан архив {name} ({len(structure)} файлов)")


if __name__ == '__main__':
    targets = sys.argv[1:] or ['min', 'files', 'deep']
    for key in targets:
        if key in VARIANTS:
            build(*VARIANTS[key])