def to_rpn(expr):
    """Преобразует инфиксное выражение в обратную польскую запись"""
    precedence = {'+':1, '-':1, '*':2, '/':2, '^':3, '~':4}
    assoc = {'^': 'R', '~': 'R'}
    functions = {'sin', 'cos', 'tg', 'ctg'}
    postfix = {'++', '--', '!'}
    
    # Токенизация
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i] == ' ':
            i += 1
        elif expr[i].isalnum():
            j = i
            while j < len(expr) and expr[j].isalnum():
                j += 1
            tokens.append(expr[i:j])
            i = j
        elif i+1 < len(expr) and expr[i:i+2] in postfix:
            tokens.append(expr[i:i+2])
            i += 2
        elif expr[i] in '+-*/^()!':
            tokens.append(expr[i])
            i += 1
        else:
            raise ValueError(f"Неверный символ: {expr[i]}")
    
    # Алгоритм сортировочной станции
    output = []
    stack = []
    
    for i, tok in enumerate(tokens):
        # Операнды (всё кроме операторов, функций, скобок)
        if tok not in '+-*/^()' and tok not in postfix and tok not in functions:
            output.append(tok)
        
        # Функции и постфиксные операторы
        elif tok in functions:
            stack.append(tok)
        elif tok in postfix:
            output.append(tok)
        
        # Скобки
        elif tok == '(':
            stack.append(tok)
        elif tok == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
            if stack and stack[-1] in functions:
                output.append(stack.pop())
        
        # Операторы
        elif tok in '+-*/^':
            # Унарный минус
            if tok == '-' and (i == 0 or tokens[i-1] in '+-*/^(' or tokens[i-1] in functions):
                tok = '~'
            
            # Выталкиваем операторы с бОльшим приоритетом
            while (stack and stack[-1] != '(' and stack[-1] in precedence and
                   (precedence[stack[-1]] > precedence[tok] or
                    (precedence[stack[-1]] == precedence[tok] and assoc.get(tok, 'L') == 'L'))):
                output.append(stack.pop())
            stack.append(tok)
    
    # Выгружаем остаток
    while stack:
        output.append(stack.pop())
    
    return ' '.join(output)


# Примеры использования
if __name__ == "__main__":
    tests = [
        "3+4*2/(1-5)",
        "sin(x)+cos(y)",
        "x++ + y",
        "a! + b",
        "2^3^2",
        "-5+3",
        "11aa",
        "2x + 3y",
    ]
    
    print("Обратная польская запись (RPN):\n")
    for test in tests:
        try:
            print(f"{test:15} -> {to_rpn(test)}")
        except Exception as e:
            print(f"{test:15} -> Ошибка: {e}")
    
    # Интерактивный режим
    print("\n" + "="*50)
    while True:
        expr = input("\nВыражение (Enter для выхода): ").strip()
        if not expr:
            break
        try:
            print(f"RPN: {to_rpn(expr)}")
        except Exception as e:
            print(f"Ошибка: {e}")                p2, assoc2, _ = OPS[stack[-1]]
                if (assoc == 'L' and p <= p2) or (assoc == 'R' and p < p2):
                    out.append(stack.pop())
                else:
                    break
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
