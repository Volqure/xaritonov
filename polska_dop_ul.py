class StackSTR:
    """Реализация стека на списке (аналог C++ класса)"""
    def __init__(self, size=100):
        self.top = -1
        self.array = [''] * size
    
    def push(self, var):
        """Добавляет элемент в стек"""
        self.top += 1
        self.array[self.top] = var
    
    def pop(self):
        """Удаляет и возвращает верхний элемент"""
        if self.top >= 0:
            self.top -= 1
            return self.array[self.top + 1]
        return '\0'
    
    def peek(self):
        """Возвращает верхний элемент без удаления"""
        if self.top >= 0:
            return self.array[self.top]
        return '\0'
    
    def empty(self):
        """Проверяет, пуст ли стек"""
        return self.top == -1


def priority(c):
    """Возвращает приоритет оператора"""
    if c in ('+', '-'):
        return 1
    elif c in ('*', '/'):
        return 2
    elif c == '^':
        return 3
    elif c in ('(', ')'):
        return 0
    else:
        return -1


def is_operator(c):
    """Проверяет, является ли символ оператором"""
    return c in ('+', '-', '*', '/', '^')


def infix_to_postfix(infix):
    """Преобразует инфиксное выражение в постфиксную запись"""
    stk = StackSTR()
    postfix = []
    
    for i, current in enumerate(infix):
        # Пропускаем пробелы
        if current == ' ':
            continue
        
        # Операнды (цифры, буквы, точка)
        if current.isdigit() or current.isalpha() or current == '.':
            postfix.append(current)
            # Добавляем пробел, если следующий символ не часть операнда
            if (i + 1 < len(infix) and 
                not infix[i + 1].isdigit() and 
                infix[i + 1] != '.' and 
                not infix[i + 1].isalpha()):
                postfix.append(' ')
        
        # Левая скобка
        elif current == '(':
            stk.push(current)
        
        # Правая скобка
        elif current == ')':
            # Добавляем пробел перед операторами
            if postfix and postfix[-1] != ' ':
                postfix.append(' ')
            # Выталкиваем операторы до '('
            while not stk.empty() and stk.peek() != '(':
                postfix.append(stk.pop())
                postfix.append(' ')
            # Удаляем '('
            stk.pop()
        
        # Операторы
        elif is_operator(current):
            # Добавляем пробел перед оператором
            if postfix and postfix[-1] != ' ':
                postfix.append(' ')
            
            # Для ^ (правоассоциативный)
            if current == '^':
                while (not stk.empty() and stk.peek() != '(' and 
                       priority(stk.peek()) > priority(current)):
                    postfix.append(stk.pop())
                    postfix.append(' ')
            # Для остальных операторов (левоассоциативные)
            else:
                while (not stk.empty() and stk.peek() != '(' and 
                       priority(stk.peek()) >= priority(current)):
                    postfix.append(stk.pop())
                    postfix.append(' ')
            
            stk.push(current)
    
    # Добавляем пробел перед выталкиванием остатка
    if postfix and postfix[-1] != ' ':
        postfix.append(' ')
    
    # Выталкиваем оставшиеся операторы из стека
    while not stk.empty():
        postfix.append(stk.pop())
        postfix.append(' ')
    
    # Удаляем лишний пробел в конце
    if postfix and postfix[-1] == ' ':
        postfix.pop()
    
    return ''.join(postfix)


def main():
    """Главная функция"""
    print("=" * 50)
    print("Преобразование инфиксной записи в постфиксную")
    print("=" * 50)
    print("Поддерживаемые операторы: +, -, *, /, ^")
    print("Поддерживаемые операнды: буквы, цифры, десятичные точки")
    print("=" * 50)
    
    while True:
        try:
            # Получаем выражение от пользователя
            infix = input("\nN: ").strip()
            
            # Проверка на выход
            if infix.lower() in ('exit', 'quit', 'q'):
                print("До свидания!")
                break
            
            # Пустая строка - пропускаем
            if not infix:
                continue
            
            # Преобразуем и выводим результат
            postfix = infix_to_postfix(infix)
            print(f"P: {postfix}")
            
        except Exception as e:
            print(f"Ошибка: {e}")
            # В случае ошибки продолжаем работу


if __name__ == "__main__":
    main()
