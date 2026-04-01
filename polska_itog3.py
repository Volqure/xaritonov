import math


def infix_to_rpn(expression):
    """
    Преобразует инфиксное выражение в постфиксную запись (RPN).

    Аргументы:
        expression: строка с инфиксным выражением (например: "3+4*2" или "a+b*c")

    Возвращает:
        строку в постфиксной записи (например: "3 4 2 * +" или "a b c * +")
    """

    # Приоритеты операторов
    precedence = {
        '!': 4,  # факториал (унарный постфиксный)
        '++': 3,  # инкремент (унарный постфиксный)
        '--': 3,  # декремент (унарный постфиксный)
        '^': 3,
        '*': 2,
        '/': 2,
        '+': 1,
        '-': 1
    }

    # Ассоциативность операторов
    associativity = {
        '++': 'R',  # унарный оператор - правоассоциативный
        '--': 'R',  # унарный оператор - правоассоциативный
        '!': 'L',  # факториал - левоассоциативный
        '^': 'R',
        '*': 'L',
        '/': 'L',
        '+': 'L',
        '-': 'L'
    }

    # Список функций
    functions = ['sin', 'cos', 'tg', 'ctg']

    # Разбиваем выражение на токены
    tokens = []
    i = 0
    n = len(expression)
    last_token_type = None  # 'operand', 'operator', 'function', 'lparen', 'rparen'

    while i < n:
        ch = expression[i]

        # Пропускаем пробелы
        if ch == ' ':
            i += 1
            continue

        # Проверяем на операторы ++ и -- (только как постфиксные)
        if i + 1 < n and expression[i:i + 2] == '++':
            # Проверяем, что ++ не в начале выражения
            if last_token_type is None:
                raise ValueError("Оператор ++ не может быть в начале выражения")
            # Проверяем, что перед ++ есть операнд или закрывающая скобка
            if last_token_type not in ['operand', 'rparen']:
                raise ValueError(f"Оператор ++ должен следовать за операндом или скобкой, позиция {i}")
            tokens.append('++')
            i += 2
            last_token_type = 'postfix_operator'
            continue
        elif i + 1 < n and expression[i:i + 2] == '--':
            # Проверяем, что -- не в начале выражения
            if last_token_type is None:
                raise ValueError("Оператор -- не может быть в начале выражения")
            # Проверяем, что перед -- есть операнд или закрывающая скобка
            if last_token_type not in ['operand', 'rparen']:
                raise ValueError(f"Оператор -- должен следовать за операндом или скобкой, позиция {i}")
            tokens.append('--')
            i += 2
            last_token_type = 'postfix_operator'
            continue

        # Проверяем на факториал
        if ch == '!':
            # Проверяем, что факториал не стоит в начале выражения
            if last_token_type is None:
                raise ValueError("Факториал не может быть в начале выражения")
            # Проверяем, что перед факториалом есть операнд или закрывающая скобка
            if last_token_type not in ['operand', 'rparen']:
                raise ValueError(f"Факториал должен следовать за операндом или скобкой, позиция {i}")
            tokens.append('!')
            i += 1
            last_token_type = 'postfix_operator'
            continue

        # Проверяем на функции
        found_function = False
        for func in functions:
            if expression.startswith(func, i):
                # Проверяем, что после имени функции идет '('
                if i + len(func) >= n or expression[i + len(func)] != '(':
                    raise ValueError(f"После функции {func} должна следовать открывающая скобка")
                tokens.append(func)
                i += len(func)
                last_token_type = 'function'
                found_function = True
                break
        if found_function:
            continue

        # Проверяем на числа
        if ch.isdigit() or ch == '.':
            j = i
            has_dot = False
            while j < n and (expression[j].isdigit() or expression[j] == '.'):
                if expression[j] == '.':
                    if has_dot:
                        raise ValueError(f"Некорректное число: {expression[i:j+1]}")
                    has_dot = True
                j += 1
            tokens.append(expression[i:j])
            i = j
            last_token_type = 'operand'
            continue

        # Проверяем на буквы (переменные)
        if ch.isalpha():
            j = i
            while j < n and expression[j].isalpha():
                j += 1
            var_name = expression[i:j]
            tokens.append(var_name)
            last_token_type = 'operand'
            i = j
            continue

        # Проверяем на бинарные операторы и скобки
        if ch in '+-*/^()':
            if ch == '(':
                tokens.append(ch)
                last_token_type = 'lparen'
            elif ch == ')':
                tokens.append(ch)
                last_token_type = 'rparen'
            elif ch in '+-*/^':
                # Бинарные операторы
                tokens.append(ch)
                last_token_type = 'operator'
            i += 1
            continue

        # Если символ не распознан
        raise ValueError(f"Неизвестный символ: {ch}")

    # Проверяем, что выражение не заканчивается бинарным оператором
    if last_token_type in ['operator', 'lparen']:
        raise ValueError("Выражение не может заканчиваться бинарным оператором или открывающей скобкой")


    # Алгоритм сортировочной станции
    output = []
    stack = []

    i = 0
    while i < len(tokens):
        token = tokens[i]

        # Если токен - число или переменная (операнд)
        if (token.replace('.', '').replace('-', '').isdigit() or
            (token[0] == '-' and len(token) > 1 and token[1:].replace('.', '').isdigit()) or
            (token.isalpha() and token not in functions)):
            output.append(token)

        # Если токен - функция
        elif token in functions:
            stack.append(token)

        # Если токен - '('
        elif token == '(':
            stack.append(token)

        # Если токен - ')'
        elif token == ')':
            # Выталкиваем операторы до '('
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            # Удаляем '('
            if stack and stack[-1] == '(':
                stack.pop()
            # Если на вершине стека функция - выталкиваем её
            if stack and stack[-1] in functions:
                output.append(stack.pop())

        # Если токен - постфиксный оператор (++, --, !)
        elif token in ['++', '--', '!']:
            output.append(token)

        # Если токен - бинарный оператор
        elif token in precedence:
            # Выталкиваем операторы с большим или равным приоритетом
            while (stack and stack[-1] != '(' and
                   stack[-1] in precedence and
                   ((associativity[token] == 'L' and precedence[stack[-1]] >= precedence[token]) or
                    (associativity[token] == 'R' and precedence[stack[-1]] > precedence[token]))):
                output.append(stack.pop())
            stack.append(token)

        i += 1

    # Выталкиваем оставшиеся операторы
    while stack:
        output.append(stack.pop())

    # Возвращаем RPN строку
    return ' '.join(output)


def main():
    """
    Главная функция программы
    """
    print("Преобразование инфиксной записи в RPN")
    print("Поддерживаемые операторы: +, -, *, /, ^, !, ++, --")
    print("Поддерживаемые функции: sin, cos, tg, ctg")
    print("=" * 60)

    while True:
        user_input = input("\nВведите выражение: ").strip()

        if user_input.lower() == 'exit':
            break

        if not user_input:
            continue

        try:
            rpn = infix_to_rpn(user_input)
            print(f"RPN: {rpn}")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
