import os
import io
import sys
import base64
import zipfile
import posixpath
import argparse
import socket
import datetime


class VFS:
    """Виртуальная файловая система, хранящая данные в памяти."""

    def __init__(self, zip_path=None):
        """Инициализирует VFS, загружая ZIP-архив в память."""
        self.dirs = {'/'}
        self.files = {}
        if zip_path and os.path.exists(zip_path):
            with open(zip_path, 'rb') as f:
                raw = f.read()
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                for info in z.infolist():
                    path = self.norm('/' + info.filename)
                    if info.is_dir():
                        self.dirs.add(path)
                    else:
                        content = base64.b64encode(z.read(info)).decode('ascii')
                        self.files[path] = content
                        self._add_parents(path)

    @staticmethod
    def norm(path):
        """Нормализует путь, гарантируя начало с '/'."""
        path = posixpath.normpath(path)
        return path if path.startswith('/') else '/' + path

    def _add_parents(self, path):
        """Добавляет все родительские каталоги для данного пути."""
        cur = ''
        for part in path.strip('/').split('/')[:-1]:
            cur += '/' + part
            self.dirs.add(cur)

    def resolve(self, path, cwd):
        """Преобразует относительный путь в абсолютный."""
        if not path.startswith('/'):
            path = posixpath.join(cwd, path)
        return self.norm(path)

    def is_dir(self, path):
        """Проверяет, является ли путь каталогом."""
        return path in self.dirs

    def is_file(self, path):
        """Проверяет, является ли путь файлом."""
        return path in self.files

    def listdir(self, path):
        """Возвращает отсортированный список содержимого каталога."""
        prefix = path.rstrip('/') + '/'
        items = set()
        for p in list(self.dirs) + list(self.files):
            if p.startswith(prefix):
                items.add(p[len(prefix):].split('/')[0])
        return sorted(items)

    def read_bytes(self, path):
        """Читает содержимое файла как байты."""
        return base64.b64decode(self.files[path])

    def read_text(self, path):
        """Читает содержимое файла как текст UTF-8."""
        return self.read_bytes(path).decode('utf-8', errors='replace')

    def add_file(self, path, content_b64):
        """Добавляет или перезаписывает файл в памяти."""
        self.files[path] = content_b64
        self._add_parents(path)

    def remove_dir(self, path):
        """Удаляет каталог из памяти."""
        if path in self.dirs:
            self.dirs.remove(path)


class Shell:
    """Оболочка эмулятора, управляющая текущим каталогом и командами."""

    def __init__(self, vfs):
        """Инициализирует оболочку с заданной VFS."""
        self.vfs = vfs
        self.cwd = '/'

    def prompt(self):
        """Генерирует строку приглашения ввода."""
        username = os.environ.get('USER') or os.getlogin()
        hostname = socket.gethostname()
        return f"{username}@{hostname}:{self.cwd}$ "

    def execute(self, line):
        """
        Выполняет команду.
        Возвращает: 'ok', 'err' или 'exit'.
        """
        if line.startswith(' ') or line.startswith('\t'):
            print("Ошибка: команда не может начинаться с пробела")
            return 'err'

        parts = line.split()
        cmd, args = parts[0], parts[1:]

        # Словарь обработчиков снижает цикломатическую сложность
        handlers = {
            'exit': self.cmd_exit,
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'cat': self.cmd_cat,
            'date': self.cmd_date,
            'whoami': self.cmd_whoami,
            'du': self.cmd_du,
            'cp': self.cmd_cp,
            'rmdir': self.cmd_rmdir,
        }

        if cmd in handlers:
            return handlers[cmd](args)

        print(f"Ошибка: неизвестная команда '{cmd}'")
        return 'err'

    def cmd_exit(self, args):
        """Завершает работу эмулятора."""
        required_args = 0
        if len(args) > required_args:
            print("Ошибка: exit: лишние аргументы")
            return 'err'
        return 'exit'

    def cmd_ls(self, args):
        """Выводит содержимое каталога или имя файла."""
        max_args = 1
        if len(args) > max_args:
            print("Ошибка: ls: слишком много аргументов")
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
        print(f"Ошибка: ls: '{target}': нет такого файла или каталога")
        return 'err'

    def cmd_cd(self, args):
        """Меняет текущий рабочий каталог."""
        max_args = 1
        if len(args) > max_args:
            print("Ошибка: cd: слишком много аргументов")
            return 'err'
        
        path = self.vfs.resolve(args[0], self.cwd) if args else '/'
        
        if self.vfs.is_dir(path):
            self.cwd = path
            return 'ok'
            
        target = args[0] if args else path
        print(f"Ошибка: cd: '{target}': нет такого каталога")
        return 'err'

    def cmd_cat(self, args):
        """Выводит содержимое файла."""
        required_args = 1
        if not args:
            print("Ошибка: cat: отсутствует операнд")
            return 'err'
        if len(args) > required_args:
            print("Ошибка: cat: слишком много аргументов")
            return 'err'
            
        path = self.vfs.resolve(args[0], self.cwd)
        if self.vfs.is_file(path):
            data = self.vfs.read_bytes(path)
            try:
                print(data.decode('utf-8'), end='')
            except UnicodeDecodeError:
                b64_data = base64.b64encode(data).decode()
                print(f"[двоичные данные, base64]: {b64_data}")
            print()
            return 'ok'
            
        print(f"Ошибка: cat: '{args[0]}': нет такого файла")
        return 'err'

    def cmd_date(self, args):
        """Выводит текущую дату и время."""
        required_args = 0
        if len(args) > required_args:
            print("Ошибка: date: лишние аргументы")
            return 'err'
        fmt = "%a %b %d %H:%M:%S %Y"
        print(datetime.datetime.now().strftime(fmt))
        return 'ok'

    def cmd_whoami(self, args):
        """Выводит имя текущего пользователя ОС."""
        required_args = 0
        if len(args) > required_args:
            print("Ошибка: whoami: лишние аргументы")
            return 'err'
        print(os.environ.get('USER') or os.getlogin())
        return 'ok'

    def cmd_du(self, args):
        """Выводит размер файла или сумму размеров файлов в каталоге."""
        max_args = 1
        if len(args) > max_args:
            print("Ошибка: du: слишком много аргументов")
            return 'err'
            
        path = self.vfs.resolve(args[0], self.cwd) if args else self.cwd
        
        if self.vfs.is_file(path):
            size = len(self.vfs.read_bytes(path))
            print(f"{size}\t{path}")
            return 'ok'
        elif self.vfs.is_dir(path):
            total_size = 0
            for item in self.vfs.listdir(path):
                item_path = self.vfs.resolve(item, path)
                if self.vfs.is_file(item_path):
                    total_size += len(self.vfs.read_bytes(item_path))
            print(f"{total_size}\t{path}")
            return 'ok'
            
        target = args[0] if args else path
        print(f"Ошибка: du: '{target}': нет такого файла или каталога")
        return 'err'

    def cmd_cp(self, args):
        """Копирует файл внутри VFS (только в памяти)."""
        required_args = 2
        if len(args) != required_args:
            print("Ошибка: cp: требуется ровно 2 аргумента")
            return 'err'
        
        src_path = self.vfs.resolve(args[0], self.cwd)
        dst_path = self.vfs.resolve(args[1], self.cwd)
        
        if not self.vfs.is_file(src_path):
            print(f"Ошибка: cp: '{args[0]}': нет такого файла")
            return 'err'
        
        if self.vfs.is_dir(dst_path):
            filename = src_path.rsplit('/', 1)[-1]
            dst_path = posixpath.join(dst_path, filename)
        
        content_b64 = self.vfs.files[src_path]
        self.vfs.add_file(dst_path, content_b64)
        print(f"Скопировано: {src_path} -> {dst_path}")
        return 'ok'

    def cmd_rmdir(self, args):
        """Удаляет пустой каталог из VFS (только в памяти)."""
        required_args = 1
        if len(args) != required_args:
            print("Ошибка: rmdir: требуется ровно 1 аргумент")
            return 'err'
        
        path = self.vfs.resolve(args[0], self.cwd)
        
        if not self.vfs.is_dir(path):
            print(f"Ошибка: rmdir: '{args[0]}': нет такого каталога")
            return 'err'
        
        if path == '/':
            print("Ошибка: rmdir: нельзя удалить корневой каталог '/'")
            return 'err'
        
        items = self.vfs.listdir(path)
        if items:
            print(f"Ошибка: rmdir: '{args[0]}': каталог не пуст")
            return 'err'
        
        self.vfs.remove_dir(path)
        print(f"Удалён каталог: {path}")
        return 'ok'


def run_script(shell, script_path):
    """Выполняет стартовый скрипт, останавливаясь при первой ошибке."""
    if not os.path.exists(script_path):
        print(f"Ошибка: скрипт '{script_path}' не найден")
        return False
        
    print(f"\n=== Выполнение скрипта: {script_path} ===\n")
    with open(script_path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line.strip() or line.strip().startswith('#'):
                continue
            print(f"{shell.prompt()}{line}")
            status = shell.execute(line)
            if status == 'err':
                print("Скрипт остановлен на первой ошибке")
                return False
            if status == 'exit':
                print("Выход из эмулятора")
                return True
    print("\n=== Скрипт завершён успешно ===")
    return True


def interactive(shell):
    """Запускает интерактивный цикл чтения-вычисления-вывода (REPL)."""
    print("\n=== Интерактивный режим ===\n")
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


def main():
    """Точка входа в приложение. Парсит аргументы и запускает эмулятор."""
    parser = argparse.ArgumentParser(
        description='Эмулятор оболочки UNIX (этап 5: cp, rmdir)'
    )
    parser.add_argument(
        '--vfs', default='vfs.zip', help='Путь к ZIP-архиву VFS'
    )
    parser.add_argument(
        '--script', default=None, help='Путь к стартовому скрипту'
    )
    args = parser.parse_args()

    vfs = VFS(args.vfs)

    
    print("Параметры эмулятора:")
    print(f"  VFS (ZIP): {os.path.abspath(args.vfs)}")
    print(f"  Файлов в VFS: {len(vfs.files)}, каталогов: {len(vfs.dirs)}")
    
    script_info = args.script if args.script else 'не указан (REPL)'
    print(f"  Скрипт: {script_info}")
    
    
    if not os.path.exists(args.vfs):
        print("Предупреждение: архив VFS не найден, создана пустая VFS")

    if vfs.is_file('/motd'):
        print(vfs.read_text('/motd'))

    shell = Shell(vfs)
    if args.script:
        sys.exit(0 if run_script(shell, args.script) else 1)
    interactive(shell)


if __name__ == "__main__":
    main()