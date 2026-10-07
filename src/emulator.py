"""Эмулятор оболочки UNIX-подобной ОС. Этап 2: Конфигурация."""
import os
import sys
import socket
import argparse


def get_prompt():
    
    username = os.environ.get('USER', 'user')
    hostname = socket.gethostname()
    return f"{username}@{hostname}:~$ "


def parse_input(line):
    
    parts = line.strip().split()
    if not parts:
        return None, []
    return parts[0], parts[1:]


def handle_command(command, arguments):
    
    if command == 'exit':
        return 'exit'
    
    if command == 'ls':
        print(f"ls: {arguments}")
        return 'ok'
    
    if command == 'cd':
        print(f"cd: {arguments}")
        return 'ok'
    
    print(f"Ошибка: неизвестная команда '{command}'")
    return 'err'


def run_script(script_path):
    
    if not os.path.exists(script_path):
        print(f"Ошибка: скрипт '{script_path}' не найден")
        return False
    
    prompt = get_prompt()
    
    with open(script_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            
            
            if not line.strip() or line.strip().startswith('#'):
                continue
            
           
            print(f"{prompt}{line}")
            
            command, arguments = parse_input(line)
            if command is None:
                continue
            
            status = handle_command(command, arguments)
            
            
            if status == 'err':
                print("Скрипт остановлен на первой ошибке")
                return False
            
            if status == 'exit':
                print("Выход из эмулятора")
                return True
    
    print("Скрипт завершён успешно")
    return True


def interactive_mode():
    """Запускает интерактивный режим REPL."""
    prompt = get_prompt()
    
    while True:
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nВыход из эмулятора")
            break
        
        if not line.strip():
            continue
        
        command, arguments = parse_input(line)
        if command is None:
            continue
        
        status = handle_command(command, arguments)
        if status == 'exit':
            print("Выход из эмулятора")
            break


def print_parameters(args):
    """Выводит отладочную информацию о параметрах запуска."""
    print("=" * 50)
    print("Параметры эмулятора:")
    print(f"  VFS путь: {os.path.abspath(args.vfs)}")
    
    script_info = args.script if args.script else 'не указан'
    print(f"  Скрипт: {script_info}")
    print("=" * 50)


def main():
    """Главная функция. Парсит аргументы и запускает эмулятор."""
    parser = argparse.ArgumentParser(
        description='Эмулятор оболочки UNIX (этап 2)'
    )
    parser.add_argument(
        '--vfs',
        default='./vfs',
        help='Путь к физическому расположению VFS'
    )
    parser.add_argument(
        '--script',
        default=None,
        help='Путь к стартовому скрипту'
    )
    args = parser.parse_args()
    

    print_parameters(args)
    

    if args.script:
        success = run_script(args.script)
        sys.exit(0 if success else 1)
    
    # Иначе интерактивный режим
    interactive_mode()


if __name__ == "__main__":
    main()