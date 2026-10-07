import os
import socket
import argparse
import sys

def get_prompt(current_dir='~'):
    """Формирует приглашение к вводу на основе данных ОС."""
    username = os.environ.get('USER') or os.getlogin()
    hostname = socket.gethostname()
    return f"{username}@{hostname}:{current_dir}$ "

def run_script(script_path, vfs_path):
    """Выполняет стартовый скрипт, останавливается при первой ошибке."""
    print(f"\n=== Выполнение скрипта: {script_path} ===")
    print(f"VFS путь: {vfs_path}\n")
    
    if not os.path.exists(script_path):
        print(f"Ошибка: скрипт '{script_path}' не найден")
        return False
    
    with open(script_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith('#'):
                continue
            
            # Отображаем ввод (как в реальном терминале)
            prompt = get_prompt()
            print(f"{prompt}{line}")
            
            # Проверяем ошибку в начале строки
            if line.startswith(' ') or line.startswith('\t'):
                print("Ошибка: команда не может начинаться с пробела")
                return False  # Останавливаемся при ошибке
            
            # Парсинг команды
            parts = line.split()
            command = parts[0]
            arguments = parts[1:]
            
            # Выполнение команд
            if command == 'exit':
                print("Выход из эмулятора")
                break
            elif command == 'ls':
                print(f"[Заглушка] Выполняется 'ls' с аргументами: {arguments}")
            elif command == 'cd':
                print(f"[Заглушка] Выполняется 'cd' с аргументами: {arguments}")
            else:
                print(f"Ошибка: неизвестная команда '{command}'")
                return False  # Останавливаемся при ошибке
    
    print("\nСкрипт завершён успешно")
    return True

def interactive_mode(vfs_path):
    """Интерактивный режим REPL."""
    print(f"\n=== Интерактивный режим ===")
    print(f"VFS путь: {vfs_path}\n")
    
    prompt = get_prompt()
    
    while True:
        try:
            user_input = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        
        # Проверка на пробел в начале
        if user_input.startswith(' ') or user_input.startswith('\t'):
            print("Ошибка: команда не может начинаться с пробела")
            continue
        
        if not user_input.strip():
            continue
        
        # Парсер
        parts = user_input.split()
        command = parts[0]
        arguments = parts[1:]
        
        # Обработка команд
        if command == 'exit':
            break
        elif command == 'ls':
            print(f"[Заглушка] Выполняется 'ls' с аргументами: {arguments}")
        elif command == 'cd':
            print(f"[Заглушка] Выполняется 'cd' с аргументами: {arguments}")
        else:
            print(f"Ошибка: неизвестная команда '{command}'")

def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Эмулятор оболочки UNIX')
    parser.add_argument('--vfs', type=str, default='./vfs',
                        help='Путь к физическому расположению VFS')
    parser.add_argument('--script', type=str, default=None,
                        help='Путь к стартовому скрипту')
    
    args = parser.parse_args()
    
    # Отладочный вывод параметров
    
    print("Параметры эмулятора:")
    print(f"  VFS путь: {os.path.abspath(args.vfs)}")
    print(f"  Скрипт: {args.script if args.script else 'не указан (интерактивный режим)'}")
    
    
    
    if args.script:
        success = run_script(args.script, args.vfs)
        sys.exit(0 if success else 1)
    else:
        interactive_mode(args.vfs)

if __name__ == "__main__":
    main()