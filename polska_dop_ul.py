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
    elif c == '~':  # унарный минус
        return 4
    elif c in ('!', '++', '--'):  # постфиксные операторы
        return 5
    elif c in ('(', ')'):
        return 0
    else:
        return -1


def is_operator(c):
    """Проверяет, является ли символ оператором"""
    return c in ('+', '-', '*', '/', '^')


def is_function(token):
    """Проверяет, является ли токен функцией"""
    return token in ('sin', 'cos', 'tg', 'ctg')


def is_postfix(token):
    """Проверяет, является ли токен постфиксным оператором"""
    return token in ('!', '++', '--')


def is_unary_minus(infix, i):
    """Определяет, является ли минус унарным"""
    if infix[i] != '-':
        return False
    # В начале выражения
    if i == 0:
        return True
    # После оператора или открывающей скобки
    if i > 0 and infix[i-1] in ('+', '-', '*', '/', '^', '('):
        return True
    return False


def tokenize(expression):
    """Разбивает выражение на токены"""
    tokens = []
    i = 0
    n = len(expression)
    
    while i < n:
        # Пропускаем пробелы
        if expression[i] == ' ':
            i += 1
            continue
        
        # Функции и переменные (буквы)
        if expression[i].isalpha():
            j = i
            while j < n and expression[j].isalpha():
                j += 1
            token = expression[i:j]
            tokens.append(token)
            i = j
            continue
        
        # Числа (цифры и точка)
        if expression[i].isdigit() or expression[i] == '.':
            j = i
            has_dot = False
            while j < n and (expression[j].isdigit() or expression[j] == '.'):
                if expression[j] == '.':
                    if has_dot:
                        raise ValueError(f"Некорректное число: две точки подряд")
                    has_dot = True
                j += 1
            tokens.append(expression[i:j])
            i = j
            continue
        
        # Постфиксные операторы (++, --)
        if i + 1 < n and expression[i:i+2] in ('++', '--'):
            tokens.append(expression[i:i+2])
            i += 2
            continue
        
        # Одиночные символы
        if expression[i] in '+-*/^()!':
            tokens.append(expression[i])
            i += 1
            continue
        
        raise ValueError(f"Неизвестный символ: '{expression[i]}'")
    
    return tokens


def validate_expression(tokens):
    """Проверяет выражение на корректность"""
    if not tokens:
        raise ValueError("Пустое выражение")
    
    balance = 0
    prev_token = None
    
    for i, token in enumerate(tokens):
        # Проверка скобок
        if token == '(':
            balance += 1
        elif token == ')':
            balance -= 1
            if balance < 0:
                raise ValueError("Лишняя закрывающая скобка")
        
        # Проверка двух операторов подряд
        if (prev_token and 
            prev_token in ('+', '-', '*', '/', '^') and 
            token in ('+', '-', '*', '/', '^')):
            raise ValueError(f"Два оператора подряд: '{prev_token}' и '{token}'")
        
        # Проверка оператора в начале
        if i == 0 and token in ('+', '*', '/', '^'):
            raise ValueError(f"Выражение не может начинаться с оператора '{token}'")
        
        # Проверка оператора в конце
        if i == len(tokens) - 1 and token in ('+', '-', '*', '/', '^'):
            raise ValueError(f"Выражение не может заканчиваться оператором '{token}'")
        
        # Проверка постфиксных операторов
        if token in ('!', '++', '--'):
            if i == 0:
                raise ValueError(f"Постфиксный оператор '{token}' не может быть в начале")
            if prev_token not in (None, ')'):
                # Проверяем, что перед постфиксным оператором операнд
                if prev_token not in ('sin', 'cos', 'tg', 'ctg'):
                    # Проверяем, не является ли предыдущий токен функцией
                    pass
        
        prev_token = token
    
    if balance != 0:
        raise ValueError("Несбалансированные скобки")
    
    return True


def infix_to_postfix(infix):
    """Преобразует инфиксное выражение в постфиксную запись"""
    # Токенизируем выражение
    tokens = tokenize(infix)
    
    # Валидируем токены
    validate_expression(tokens)
    
    stk = StackSTR()
    postfix = []
    functions = {'sin', 'cos', 'tg', 'ctg'}
    
    for i, token in enumerate(tokens):
        # Операнды (числа, переменные)
        if (token.replace('.', '').isdigit() or 
            token.isalpha() and not is_function(token)):
            postfix.append(token)
            postfix.append(' ')
        
        # Функции
        elif is_function(token):
            stk.push(token)
        
        # Постфиксные операторы
        elif is_postfix(token):
            postfix.append(token)
            postfix.append(' ')
        
        # Левая скобка
        elif token == '(':
            stk.push(token)
        
        # Правая скобка
        elif token == ')':
            # Выталкиваем операторы до '('
            while not stk.empty() and stk.peek() != '(':
                postfix.append(stk.pop())
                postfix.append(' ')
            # Удаляем '('
            if not stk.empty() and stk.peek() == '(':
                stk.pop()
            # Если на вершине стека функция - выталкиваем её
            if not stk.empty() and is_function(stk.peek()):
                postfix.append(stk.pop())
                postfix.append(' ')
        
        # Операторы
        elif is_operator(token) or token == '-':
            # Определяем, является ли минус унарным
            if token == '-':
                is_unary = (i == 0 or 
                           tokens[i-1] in ('+', '-', '*', '/', '^', '(') or
                           is_function(tokens[i-1]))
                if is_unary:
                    token = '~'
            
            # Добавляем пробел перед оператором
            if postfix and postfix[-1] != ' ':
                postfix.append(' ')
            
            # Для ^ (правоассоциативный)
            if token == '^':
                while (not stk.empty() and stk.peek() != '(' and 
                       priority(stk.peek()) > priority(token)):
                    postfix.append(stk.pop())
                    postfix.append(' ')
            # Для остальных операторов (левоассоциативные)
            else:
                while (not stk.empty() and stk.peek() != '(' and 
                       priority(stk.peek()) >= priority(token)):
                    postfix.append(stk.pop())
                    postfix.append(' ')
            
            stk.push(token)
    
    # Выталкиваем оставшиеся операторы из стека
    while not stk.empty():
        if stk.peek() == '(' or stk.peek() == ')':
            stk.pop()
            continue
        if postfix and postfix[-1] != ' ':
            postfix.append(' ')
        postfix.append(stk.pop())
        postfix.append(' ')
    
    # Удаляем лишние пробелы в конце
    while postfix and postfix[-1] == ' ':
        postfix.pop()
    
    return ''.join(postfix)


def main():
    """Главная функция"""
    print("=" * 60)
    print("Преобразование инфиксной записи в постфиксную (RPN)")
    print("=" * 60)
    print("\nПоддерживаемые операторы и функции:")
    print("  • Бинарные: +, -, *, /, ^")
    print("  • Унарный минус: - (автоматически распознаётся)")
    print("  • Постфиксные: ! (факториал), ++ (инкремент), -- (декремент)")
    print("  • Функции: sin, cos, tg, ctg")
    print("  • Операнды: числа (целые и десятичные), переменные (буквы)")
    print("=" * 60)
    
    # Тестовые примеры
    print("\n" + "=" * 60)
    print("ТЕСТОВЫЕ ПРИМЕРЫ:")
    print("=" * 60)
    
    test_cases = [
        # Базовые операции
        "A+B*C",
        "(A+B)*C",
        "2+3*4",
        "2^3^2",
        "-5+3",
        
        # Постфиксные операторы
        "x++ + y",
        "a! + b",
        "x++",
        "a!",
        
        # Функции
        "sin(x)",
        "cos(x)+sin(y)",
        "sin(x)+cos(y)",
        "sin(30)+cos(45)",
        
        # Смешанные
        "sin(x++)",
        "sin(x)+cos(y)*2",
        "-sin(x)",
        
        # Переменные с цифрами
        "11aa",
        "2x + 3y",
        
        # Ошибочные выражения (должны выдавать ошибку)
        "sin(x++x)",
        "x+^2",
        "a b",
        "a+",
        "+a",
        "()",
        "sin(x",
        "x!+",
    ]
    
    for expr in test_cases:
        try:
            result = infix_to_postfix(expr)
            print(f"{expr:25} -> {result}")
        except Exception as e:
            print(f"{expr:25} -> ОШИБКА: {e}")
    
    # Интерактивный режим
    print("\n" + "=" * 60)
    print("ИНТЕРАКТИВНЫЙ РЕЖИМ")
    print("Введите 'exit' для выхода")
    print("=" * 60)
    
    while True:
        try:
            infix = input("\nВведите выражение: ").strip()
            
            if infix.lower() in ('exit', 'quit', 'q'):
                print("До свидания!")
                break
            
            if not infix:
                continue
            
            postfix = infix_to_postfix(infix)
            print(f"RPN: {postfix}")
            
        except ValueError as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    main()
