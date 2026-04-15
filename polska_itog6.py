import math


def infix_to_rpn(expression):

    precedence = {
        '~': 4,
        '!': 4,
        '++': 3,
        '--': 3,
        '^': 3,
        '*': 2,
        '/': 2,
        '+': 1,
        '-': 1
    }

    associativity = {
        '~': 'R',
        '++': 'R',
        '--': 'R',
        '!': 'L',
        '^': 'R',
        '*': 'L',
        '/': 'L',
        '+': 'L',
        '-': 'L'
    }

    functions = ['sin', 'cos', 'tg', 'ctg']

    tokens = []
    i = 0
    n = len(expression)
    last_token_type = None

    while i < n:
        ch = expression[i]

        if ch == ' ':
            i += 1
            continue

        if i + 1 < n and expression[i:i + 2] == '++':
            if last_token_type is None:
                raise ValueError("Оператор ++ не может быть в начале выражения")
            if last_token_type not in ['operand', 'rparen']:
                raise ValueError(f"Оператор ++ должен следовать за операндом или скобкой, позиция {i}")
            tokens.append('++')
            i += 2
            last_token_type = 'postfix_operator'
            continue
        elif i + 1 < n and expression[i:i + 2] == '--':
            if last_token_type is None:
                raise ValueError("Оператор -- не может быть в начале выражения")
            if last_token_type not in ['operand', 'rparen']:
                raise ValueError(f"Оператор -- должен следовать за операндом или скобкой, позиция {i}")
            tokens.append('--')
            i += 2
            last_token_type = 'postfix_operator'
            continue

        if ch == '!':
            if last_token_type is None:
                raise ValueError("Факториал не может быть в начале выражения")
            if last_token_type not in ['operand', 'rparen']:
                raise ValueError(f"Факториал должен следовать за операндом или скобкой, позиция {i}")
            tokens.append('!')
            i += 1
            last_token_type = 'postfix_operator'
            continue

        found_function = False
        for func in functions:
            if expression.startswith(func, i):
                if i + len(func) >= n or expression[i + len(func)] != '(':
                    raise ValueError(f"После функции {func} должна следовать открывающая скобка")
                tokens.append(func)
                i += len(func)
                last_token_type = 'function'
                found_function = True
                break
        if found_function:
            continue

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

        if ch.isalpha():
            j = i
            while j < n and expression[j].isalpha():
                j += 1
            var_name = expression[i:j]
            tokens.append(var_name)
            last_token_type = 'operand'
            i = j
            continue

        if ch in '+-*/^()':
            if ch == '(':
                tokens.append(ch)
                last_token_type = 'lparen'
            elif ch == ')':
                tokens.append(ch)
                last_token_type = 'rparen'
            elif ch in '+-*/^':
                if ch == '-':
                    is_unary = (last_token_type is None or
                               last_token_type in ['operator', 'lparen', 'function'])
                    if is_unary:
                        tokens.append('~')
                        last_token_type = 'operator'
                        i += 1
                        continue
                tokens.append(ch)
                last_token_type = 'operator'
            i += 1
            continue

        raise ValueError(f"Неизвестный символ: {ch}")

    if last_token_type in ['operator', 'lparen']:
        raise ValueError("Выражение не может заканчиваться бинарным оператором или открывающей скобкой")

    output = []
    stack = []

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if (token.replace('.', '').replace('-', '').isdigit() or
            (token[0] == '-' and len(token) > 1 and token[1:].replace('.', '').isdigit()) or
            (token.isalpha() and token not in functions and token != '~')):
            output.append(token)

        elif token in functions:
            stack.append(token)

        elif token == '(':
            stack.append(token)

        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()
            if stack and stack[-1] in functions:
                output.append(stack.pop())

        elif token in ['++', '--', '!']:
            output.append(token)

        elif token == '~':
            stack.append(token)

        elif token in precedence:
            while (stack and stack[-1] != '(' and
                   stack[-1] in precedence and
                   ((associativity[token] == 'L' and precedence[stack[-1]] >= precedence[token]) or
                    (associativity[token] == 'R' and precedence[stack[-1]] > precedence[token]))):
                output.append(stack.pop())
            stack.append(token)

        i += 1

    while stack:
        output.append(stack.pop())

    return ' '.join(output)


def main():

    print("Преобразование инфиксной записи в RPN")
    print("Поддерживаемые операторы: +, -, *, /, ^, !, ++, --")
    print("Унарный минус в RPN обозначается как ~")
    print("Поддерживаемые функции: sin, cos, tg, ctg")
    print("Поддерживаемые переменные: буквы латинского алфавита (a-z, A-Z)")
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
