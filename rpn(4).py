def tokenize(expr):
    """Разбивает выражение на токены"""
    tokens = []
    i = 0
    n = len(expr)
    
    while i < n:
        if expr[i] == ' ':
            i += 1
            continue
        
        # Идентификаторы (буквы+цифры)
        if expr[i].isalnum():
            j = i
            while j < n and expr[j].isalnum():
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue
        
        # Постфиксные операторы
        if i + 1 < n and expr[i:i+2] in ('++', '--'):
            tokens.append(expr[i:i+2])
            i += 2
            continue
        
        # Одиночные символы
        if expr[i] in '+-*/^()!':
            tokens.append(expr[i])
            i += 1
            continue
        
        raise ValueError(f"Неизвестный символ: {expr[i]}")
    
    return tokens


def is_operator(tok):
    """Проверка, является ли токен оператором"""
    return tok in '+-*/^~'


def precedence(op):
    """Приоритет операторов"""
    return {'+':1, '-':1, '*':2, '/':2, '^':3, '~':4, '!':5, '++':5, '--':5}.get(op, 0)


def is_right_assoc(op):
    """Правоассоциативные операторы"""
    return op in ('^', '~', '++', '--')


def shunting_yard(tokens):
    """Алгоритм сортировочной станции"""
    output = []
    stack = []
    functions = {'sin', 'cos', 'tg', 'ctg'}
    postfix_ops = {'++', '--', '!'}
    
    for i, tok in enumerate(tokens):
        # Операнды (всё, кроме операторов, функций и скобок)
        if tok not in '+-*/^()' and tok not in postfix_ops and tok not in functions:
            output.append(tok)
        
        # Функции
        elif tok in functions:
            stack.append(tok)
        
        # Постфиксные операторы
        elif tok in postfix_ops:
            output.append(tok)
        
        # Левая скобка
        elif tok == '(':
            stack.append(tok)
        
        # Правая скобка
        elif tok == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # убираем '('
            if stack and stack[-1] in functions:
                output.append(stack.pop())
        
        # Операторы
        elif is_operator(tok) or tok == '-':
            # Унарный минус
            if tok == '-' and (i == 0 or tokens[i-1] in '+-*/^(' or tokens[i-1] in functions):
                tok = '~'
            
            while (stack and stack[-1] != '(' and 
                   precedence(stack[-1]) > precedence(tok) or
                   (precedence(stack[-1]) == precedence(tok) and not is_right_assoc(tok))):
                output.append(stack.pop())
            stack.append(tok)
    
    # Выгружаем остаток
    while stack:
        output.append(stack.pop())
    
    return ' '.join(output)


def infix_to_rpn(expression):
    """Основная функция"""
    tokens = tokenize(expression)
    
    # Минимальная проверка скобок
    if tokens.count('(') != tokens.count(')'):
        raise ValueError("Несбалансированные скобки")
    
    return shunting_yard(tokens)


def main():
    print("Преобразование инфиксной записи в RPN")
    print("Операторы: + - * / ^ ! ++ --")
    print("Функции: sin cos tg ctg")
    print("Переменные: буквы и цифры (например: a, x1, 11aa)")
    print("=" * 50)
    
    test_cases = [
        "3+4*2/(1-5)",
        "sin(x)+cos(y)",
        "x++ + y",
        "a! + b",
        "2^3^2",
        "-5+3",
        "11aa",
        "1133",
        "2x + 3y",
        "x+^2",
        "sin(x++x)",
    ]
    
    for expr in test_cases:
        print(f"\n{expr} -> ", end="")
        try:
            print(infix_to_rpn(expr))
        except Exception as e:
            print(f"Ошибка: {e}")
    
    # Интерактивный режим
    print("\n" + "=" * 50)
    while True:
        expr = input("\nВведите выражение (exit для выхода): ").strip()
        if expr.lower() == 'exit':
            break
        if expr:
            try:
                print(f"RPN: {infix_to_rpn(expr)}")
            except Exception as e:
                print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()            if prev in postfix_ops and is_operand(token):
                raise ValueError(f"После постфиксного оператора '{prev}' должен следовать бинарный оператор")
            
            # Постфиксный оператор должен следовать за операндом
            if token in postfix_ops and not is_operand(prev) and prev != ')':
                raise ValueError(f"Постфиксный оператор '{token}' должен следовать за операндом")
    
    if balance != 0:
        raise ValueError("Несбалансированные скобки")
    
    return True


def get_precedence(op):
    """Возвращает приоритет оператора"""
    precedence = {
        '(': 0, ')': 0,
        '+': 2, '-': 2,
        '*': 3, '/': 3,
        '^': 4,
        '~': 5,  # унарный минус
        '!': 6, '++': 6, '--': 6
    }
    return precedence.get(op, 0)


def is_right_associative(op):
    """Проверяет, является ли оператор правоассоциативным"""
    right_assoc = {'^', '~', '++', '--'}
    return op in right_assoc


def is_function(token):
    """Проверяет, является ли токен функцией"""
    functions = {'sin', 'cos', 'tg', 'ctg'}
    return token in functions


def shunting_yard(tokens):
    """
    Алгоритм сортировочной станции (Shunting-yard algorithm)
    """
    output = []
    stack = []
    functions = {'sin', 'cos', 'tg', 'ctg'}
    postfix_ops = {'++', '--', '!'}
    operators = {'+', '-', '*', '/', '^'}
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        # Операнды (идентификаторы, числа, переменные)
        if (token not in operators and 
            token not in postfix_ops and 
            token not in '()' and
            token not in functions):
            output.append(token)
        
        # Функции
        elif token in functions:
            stack.append(token)
        
        # Постфиксные операторы
        elif token in postfix_ops:
            output.append(token)
        
        # Левая скобка
        elif token == '(':
            stack.append(token)
        
        # Правая скобка
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()
            if stack and stack[-1] in functions:
                output.append(stack.pop())
        
        # Операторы
        elif token in operators:
            # Обработка унарного минуса
            if token == '-':
                is_unary = (i == 0 or 
                           tokens[i-1] in operators or 
                           tokens[i-1] == '(' or
                           tokens[i-1] in functions)
                if is_unary:
                    token = '~'
            
            while (stack and stack[-1] != '(' and
                   stack[-1] not in functions and
                   (get_precedence(stack[-1]) > get_precedence(token) or
                    (get_precedence(stack[-1]) == get_precedence(token) and 
                     not is_right_associative(token)))):
                output.append(stack.pop())
            stack.append(token)
        
        i += 1
    
    # Выгружаем оставшиеся операторы
    while stack:
        if stack[-1] in '()':
            raise ValueError("Несбалансированные скобки")
        output.append(stack.pop())
    
    return ' '.join(output)


def infix_to_rpn(expression):
    """
    Преобразует инфиксное выражение в обратную польскую запись
    """
    tokens = tokenize(expression)
    validate_tokens(tokens)
    rpn = shunting_yard(tokens)
    return rpn


def main():
    print("=" * 60)
    print("Преобразование инфиксной записи в RPN")
    print("=" * 60)
    print("\nПоддерживаемые операторы: +, -, *, /, ^, !, ++, --")
    print("Поддерживаемые функции: sin, cos, tg, ctg")
    print("Идентификаторы (переменные): буквы и цифры (например: a, x1, var123, 11aa)")
    print("=" * 60)
    
    # Тестовые примеры
    print("\nТестовые примеры:")
    test_cases = [
        "3+4*2/(1-5)",
        "sin(x)+cos(y)",
        "x++ + y",
        "a! + b",
        "2^3^2",
        "-5+3",
        "11aa",          # Теперь это один токен!
        "1133",          # Тоже один токен
        "x1 + y2",       # Переменные с цифрами
        "2x + 3y",       # 2x и 3y - отдельные идентификаторы
        "x+^2",          # Должна быть ошибка
        "sin(x++x)",     # Должна быть ошибка
    ]
    
    for expr in test_cases:
        print(f"\nВход: '{expr}'")
        try:
            rpn = infix_to_rpn(expr)
            print(f"RPN: {rpn}")
        except ValueError as e:
            print(f"Ошибка: {e}")
    
    # Интерактивный режим
    print("\n" + "=" * 60)
    print("Интерактивный режим (введите 'exit' для выхода)")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\nВведите выражение: ").strip()
            
            if user_input.lower() == 'exit':
                print("До свидания!")
                break
            
            if not user_input:
                continue
            
            rpn = infix_to_rpn(user_input)
            print(f"RPN: {rpn}")
            
        except ValueError as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    main()
