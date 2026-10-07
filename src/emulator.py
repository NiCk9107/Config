"""Эмулятор оболочки UNIX-подобной ОС. Этап 3: VFS."""
import os
import io
import sys
import base64
import zipfile
import posixpath
import socket
import argparse


class VFS:
    """Виртуальная ФС: данные хранятся в памяти в формате base64."""

    def __init__(self, zip_path=None):
        """Загружает ZIP-архив VFS целиком в память."""
        self.dirs = {'/'}
        self.files = {}
        if zip_path and os.path.exists(zip_path):
            self._load(zip_path)

    def _load(self, zip_path):
        """Читает архив в память, не распаковывая его на диск."""
        with open(zip_path, 'rb') as fh:
            raw = fh.read()
        with zipfile.ZipFile(io.BytesIO(raw)) as arc:
            for info in arc.infolist():
                self._add_entry(info, arc)

    def _add_entry(self, info, arc):
        """Добавляет один элемент архива в структуру VFS."""
        path = self.norm('/' + info.filename)
        if info.is_dir():
            self.dirs.add(path)
            return
        data = base64.b64encode(arc.read(info))
        self.files[path] = data.decode('ascii')
        self._add_parents(path)

    @staticmethod
    def norm(path):
        """Нормализует путь: всегда начинается с '/'."""
        clean = posixpath.normpath(path)
        return clean if clean.startswith('/') else '/' + clean

    def _add_parents(self, path):
        """Регистрирует все родительские каталоги пути."""
        cur = ''
        parts = path.strip('/').split('/')[:-1]
        for part in parts:
            cur += '/' + part
            self.dirs.add(cur)

    def resolve(self, path, cwd):
        """Преобразует относительный путь в абсолютный."""
        full = path if path.startswith('/') else posixpath.join(cwd, path)
        return self.norm(full)

    def is_dir(self, path):
        """Возвращает True, если путь является каталогом."""
        return path in self.dirs

    def is_file(self, path):
        """Возвращает True, если путь является файлом."""
        return path in self.files

    def listdir(self, path):
        """Возвращает отсортированный список имён в каталоге."""
        prefix = path.rstrip('/') + '/'
        items = set()
        for entry in list(self.dirs) + list(self.files):
            if entry.startswith(prefix):
                tail = entry[len(prefix):]
                items.add(tail.split('/')[0])
        return sorted(items)

    def read_bytes(self, path):
        """Возвращает содержимое файла как байты."""
        return base64.b64decode(self.files[path])

    def read_text(self, path):
        """Возвращает содержимое файла как текст UTF-8."""
        return self.read_bytes(path).decode('utf-8', errors='replace')


class Shell:
    """Оболочка: хранит текущий каталог и выполняет команды."""

    def __init__(self, vfs):
        """Создаёт оболочку с заданной VFS."""
        self.vfs = vfs
        self.cwd = '/'

    def prompt(self):
        """Формирует приглашение ввода на основе данных ОС."""
        user = os.environ.get('USER', 'user')
        host = socket.gethostname()
        return f"{user}@{host}:{self.cwd}$ "

    def execute(self, line):
        """Выполняет команду. Возвращает 'ok', 'err' или 'exit'."""
        if line.startswith(' ') or line.startswith('\t'):
            print('Ошибка: команда не может начинаться с пробела')
            return 'err'
        parts = line.split()
        cmd, args = parts[0], parts[1:]
        commands = {
            'exit': self.cmd_exit,
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'cat': self.cmd_cat,
        }
        handler = commands.get(cmd)
        if handler is None:
            print(f"Ошибка: неизвестная команда '{cmd}'")
            return 'err'
        return handler(args)

    def cmd_exit(self, args):
        """Завершает работу эмулятора."""
        return 'exit'

    def cmd_ls(self, args):
        """Выводит содержимое каталога VFS или имя файла."""
        max_args = 1
        if len(args) > max_args:
            print('Ошибка: ls: слишком много аргументов')
            return 'err'
        path = self.vfs.resolve(args[0], self.cwd) if args else self.cwd
        if self.vfs.is_file(path):
            print(path.rsplit('/', 1)[-1])
            return 'ok'
        if self.vfs.is_dir(path):
            items = self.vfs.listdir(path)
            if items:
                print('  '.join(items))
            return 'ok'
        target = args[0] if args else path
        print(f"Ошибка: ls: '{target}': нет такого файла")
        return 'err'

    def cmd_cd(self, args):
        """Меняет текущий каталог оболочки."""
        max_args = 1
        if len(args) > max_args:
            print('Ошибка: cd: слишком много аргументов')
            return 'err'
        path = self.vfs.resolve(args[0], self.cwd) if args else '/'
        if self.vfs.is_dir(path):
            self.cwd = path
            return 'ok'
        target = args[0] if args else path
        print(f"Ошибка: cd: '{target}': нет такого каталога")
        return 'err'

    def cmd_cat(self, args):
        """Выводит содержимое файла VFS."""
        exact_args = 1
        if len(args) != exact_args:
            print('Ошибка: cat: нужен ровно один аргумент')
            return 'err'
        path = self.vfs.resolve(args[0], self.cwd)
        if not self.vfs.is_file(path):
            print(f"Ошибка: cat: '{args[0]}': нет такого файла")
            return 'err'
        data = self.vfs.read_bytes(path)
        try:
            print(data.decode('utf-8'), end='')
        except UnicodeDecodeError:
            b64 = base64.b64encode(data).decode('ascii')
            print(f'[двоичные данные, base64]: {b64}')
        print()
        return 'ok'


def run_script(shell, script_path):
    """Выполняет стартовый скрипт, останавливаясь на ошибке."""
    if not os.path.exists(script_path):
        print(f"Ошибка: скрипт '{script_path}' не найден")
        return False
    print(f' Выполнение скрипта: {script_path} ===')
    with open(script_path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.rstrip('\n')
            if not line.strip() or line.strip().startswith('#'):
                continue
            print(f'{shell.prompt()}{line}')
            status = shell.execute(line)
            if status == 'err':
                print('Скрипт остановлен на первой ошибке')
                return False
            if status == 'exit':
                print('Выход из эмулятора')
                return True
    print('Скрипт завершён успешно')
    return True


def interactive(shell):
    """Запускает интерактивный режим REPL."""
    while True:
        try:
            line = input(shell.prompt())
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line.strip():
            continue
        if shell.execute(line) == 'exit':
            break


def print_parameters(args, vfs):
    """Выводит отладочную информацию о параметрах запуска."""
    print('Параметры эмулятора:')
    print(f'  VFS (ZIP): {os.path.abspath(args.vfs)}')
    print(f'  Файлов в VFS: {len(vfs.files)}')
    print(f'  Каталогов в VFS: {len(vfs.dirs)}')
    script = args.script if args.script else 'не указан'
    print(f'  Скрипт: {script}')
    


def show_motd(vfs):
    """Выводит сообщение из /motd, если он есть в корне VFS."""
    if vfs.is_file('/motd'):
        print(vfs.read_text('/motd'))


def main():
    """Точка входа: парсит аргументы и запускает эмулятор."""
    parser = argparse.ArgumentParser(
        description='Эмулятор оболочки UNIX (этап 3: VFS)'
    )
    parser.add_argument('--vfs', default='vfs.zip',
                        help='Путь к ZIP-архиву VFS')
    parser.add_argument('--script', default=None,
                        help='Путь к стартовому скрипту')
    args = parser.parse_args()

    vfs = VFS(args.vfs)
    print_parameters(args, vfs)
    if not os.path.exists(args.vfs):
        print('Предупреждение: архив VFS не найден, VFS пуста')

    show_motd(vfs)
    shell = Shell(vfs)
    if args.script:
        sys.exit(0 if run_script(shell, args.script) else 1)
    interactive(shell)


if __name__ == '__main__':
    main()