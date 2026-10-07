import base64
import sys
import zipfile

LOGO_B64 = (
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAA'
    'DUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
)

VFS_MIN = {
    'motd': 'Добро пожаловать в минимальную VFS!\n',
}

VFS_FILES = {
    'readme.txt': 'Виртуальная файловая система: файлы в корне.\n',
    'notes.txt': 'Заметка: VFS загружается из ZIP в память.\n',
    'logo.bin': base64.b64decode(LOGO_B64),
}

VFS_DEEP = {
    'motd': 'Привет! Это VFS с тремя уровнями вложенности.\n',
    'docs/readme.txt': 'Документация проекта находится здесь.\n',
    'docs/reports/2026/q1.txt': 'Отчёт за 1 квартал 2026: всё по плану.\n',
    'docs/reports/2026/q2.txt': 'Отчёт за 2 квартал: в процессе.\n',
    'home/user/settings.conf': 'theme=dark\nlang=ru\n',
    'home/user/bin/logo.bin': base64.b64decode(LOGO_B64),
    'empty_dir/': b'',
    'tmp/': b'',
}

VARIANTS = {
    'min': ('vfs_min.zip', VFS_MIN),
    'files': ('vfs_files.zip', VFS_FILES),
    'deep': ('vfs_deep.zip', VFS_DEEP),
}


def build(name, structure):
    
    with zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED) as arc:
        for path, content in structure.items():
            data = content
            if isinstance(data, str):
                data = data.encode('utf-8')
            arc.writestr(path, data)
    msg = f'Создан архив {name} ({len(structure)} элементов)'
    print(msg)


if __name__ == '__main__':
    targets = sys.argv[1:] or list(VARIANTS)
    for key in targets:
        build(*VARIANTS[key])