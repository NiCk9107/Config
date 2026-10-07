"""Эмулятор оболочки UNIX-подобной ОС. Этап 1: REPL."""
import os
import socket
import sys


def get_prompt():
    """Формирует приглашение к вводу на основе данных ОС.
    
    Возвращает строку формата username@hostname:~$
    """
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


def main():
    """Главная функция эмулятора. Запускает интерактивный режим."""
    print("Эмулятор оболочки запущен. Введите 'exit' для выхода.")
    
    while True:
        try:
            prompt = get_prompt()
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


if __name__ == "__main__":
    main()