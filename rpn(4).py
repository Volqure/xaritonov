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
    main()
