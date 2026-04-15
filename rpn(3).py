def is_operator(c):
    """Проверка, является ли символ оператором"""
    return c in '+-*/^'

def is_function(name):
    """Проверка, является ли токен функцией"""
    return name in ['sin', 'cos', 'tg', 'ctg']

def is_postfix(op):
    """Проверка, является ли оператор постфиксным"""
    return op in ['++', '--', '!']

def precedence(op):
    """Возвращает приоритет оператора"""
    if op in ['+', '-']: return 1
    if op in ['*', '/']: return 2
    if op == '^': return 3
    if op == '~': return 4  # унарный минус
    if op in ['++', '--', '!']: return 5
    return 0

def is_right_associative(op):
    """Проверка на правоассоциативность"""
    return op in ['^', '~', '++', '--']

def tokenize(expr):
    """Разбивает выражение на токены"""
    tokens = []
    i = 0
    n = len(expr)
    
    while i < n:
        if expr[i] == ' ':
            i += 1
            continue
        
        # Идентификаторы (буквы + цифры)
        if expr[i].isalnum():
            j = i
            while j < n and expr[j].isalnum():
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue
        
        # Постфиксные операторы (++, --)
        if i + 1 < n and expr[i:i+2] in ['++', '--']:
            tokens.append(expr[i:i+2])
            i += 2
            continue
        
        # Одиночные символы
        if expr[i] in '+-*/^()!':
            tokens.append(expr[i])
            i += 1
            continue
        
        raise ValueError(f"Неизвестный символ: '{expr[i]}'")
    
    return tokens

def shunting_yard(tokens):
    """
    Алгоритм сортировочной станции (Shunting-yard algorithm)
    Правила:
    1) Если токен - число/переменная → в выход
    2) Если токен - функция → в стек
    3) Если токен - разделитель (,) → выталкиваем из стека до '('
    4) Если токен - оператор o1:
       - Пока в стеке есть оператор o2 с бОльшим приоритетом
         ИЛИ (равный приоритет И левоассоциативный):
         выталкиваем o2 в выход
       - Помещаем o1 в стек
    5) Если токен - '(' → в стек
    6) Если токен - ')' → выталкиваем из стека до '('
       Затем выталкиваем функцию (если есть)
    7) Когда токены кончились → выталкиваем всё из стека в выход
    """
    output = []  # Выходная строка (RPN)
    stack = []   # Стек операторов и функций
    
    for i, token in enumerate(tokens):
        # 1) Операнды (числа и переменные)
        if (token.replace('.', '').isdigit() or  # число
            (token[0] == '-' and len(token) > 1 and token[1:].replace('.', '').isdigit()) or  # отрицательное число
            (token.isalnum() and not is_function(token))):  # переменная
            output.append(token)
        
        # 2) Функции
        elif is_function(token):
            stack.append(token)
        
        # 3) Постфиксные операторы (сразу в выход)
        elif is_postfix(token):
            output.append(token)
        
        # 4) Левая скобка
        elif token == '(':
            stack.append(token)
        
        # 5) Правая скобка
        elif token == ')':
            # Выталкиваем из стека в выход до '('
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            # Удаляем '(' из стека
            if stack and stack[-1] == '(':
                stack.pop()
            # Если на вершине стека функция - выталкиваем её
            if stack and is_function(stack[-1]):
                output.append(stack.pop())
        
        # 6) Операторы
        elif is_operator(token) or token == '-':
            # Определяем, унарный ли минус
            if token == '-':
                is_unary = (i == 0 or 
                           tokens[i-1] in '+-*/^(' or 
                           is_function(tokens[i-1]))
                if is_unary:
                    token = '~'
            
            # Выталкиваем операторы с бОльшим приоритетом
            while (stack and stack[-1] != '(' and 
                   is_operator(stack[-1]) or stack[-1] == '~'):
                o2 = stack[-1]
                # Условие: приоритет o2 > приоритет token
                # ИЛИ (приоритеты равны И o2 левоассоциативный)
                if (precedence(o2) > precedence(token) or
                    (precedence(o2) == precedence(token) and 
                     not is_right_associative(token))):
                    output.append(stack.pop())
                else:
                    break
            
            # Помещаем текущий оператор в стек
            stack.append(token)
    
    # 7) Когда входная строка закончилась: выталкиваем всё из стека
    while stack:
        top = stack.pop()
        if top in '()':
            raise ValueError("Несбалансированные скобки")
        output.append(top)
    
    return ' '.join(output)


def infix_to_rpn(expression):
    """Основная функция: преобразует инфиксную запись в RPN"""
    tokens = tokenize(expression)
    return shunting_yard(tokens)


# Примеры использования
if __name__ == "__main__":
    test_cases = [
        "2 + 4",
        "3+4*2/(1-5)",
        "2+3*4",
        "2^3^2",
        "-5+3",
        "sin(x)+cos(y)",
        "x++ + y",
        "a! + b",
        "11aa",
        "2x + 3y",
        "sin(x)",
        "(2+3)*4",
    ]
    
    print("=" * 50)
    print("Обратная польская запись (RPN)")
    print("=" * 50)
    
    for expr in test_cases:
        try:
            rpn = infix_to_rpn(expr)
            print(f"{expr:20} -> {rpn}")
        except Exception as e:
            print(f"{expr:20} -> Ошибка: {e}")
    
    # Интерактивный режим
    print("\n" + "=" * 50)
    print("Интерактивный режим (пустая строка - выход)")
    print("=" * 50)
    
    while True:
        expr = input("\nВведите выражение: ").strip()
        if not expr:
            break
        try:
            print(f"RPN: {infix_to_rpn(expr)}")
        except Exception as e:
            print(f"Ошибка: {e}")                    break
            stack.append(t)

        elif t == '(':
            stack.append(t)

        elif t == ')':
            while stack and stack[-1] != '(':
                out.append(stack.pop())
            stack.pop()
            if stack and stack[-1] in FUNCS:
                out.append(stack.pop())

        if debug:
            print(f"{t:>6} | STACK: {' '.join(stack)} | OUT: {' '.join(out)}")

    while stack:
        out.append(stack.pop())
        if debug:
            print(f"{'END':>6} | STACK: {' '.join(stack)} | OUT: {' '.join(out)}")

    return out


def parse(expr, debug=False):
    tokens = tokenize(expr)
    tokens = normalize_funcs(tokens)  # 🔹 ключевое место
    validate(tokens)
    return ' '.join(to_rpn(tokens, debug))


# 🔁 ЦИКЛ ВВОДА
if __name__ == "__main__":
    while True:
        expr = input("\nВведите выражение (или exit): ")

        if expr.lower() == "exit":
            print("Выход.")
            break

        try:
            debug = input("Показать шаги? (y/n): ").lower() == 'y'
            result = parse(expr, debug)
            print("ОПЗ:", result)

        except Exception as e:
            print("Ошибка:", e)
def parse(expr, debug=False):
    tokens = tokenize(expr)
    validate(tokens)
    rpn = to_rpn(tokens, debug)
    return ' '.join(rpn)  # 🔹 строка


# 🔹 ВВОД ПОЛЬЗОВАТЕЛЯ
if __name__ == "__main__":
    try:
        expr = input("Введите выражение: ")
        debug = input("Показать шаги? (y/n): ").lower() == 'y'

        result = parse(expr, debug)

        print("\nОПЗ:", result)

    except Exception as e:
        print("Ошибка:", e)
