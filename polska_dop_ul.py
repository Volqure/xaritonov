def tokenize(expression):

    tokens = []
    i = 0
    n = len(expression)

    while i < n:
        ch = expression[i]

        if ch == ' ':
            i += 1
            continue

        if ch.isalnum():
            j = i
            while j < n and expression[j].isalnum():
                j += 1
            tokens.append(expression[i:j])
            i = j
            continue


        if i + 1 < n and expression[i:i + 2] in ('++', '--'):
            tokens.append(expression[i:i + 2])
            i += 2
            continue


        if ch in '+-*/^()!.':
            tokens.append(ch)
            i += 1
            continue

        raise ValueError(f"Неизвестный символ: '{ch}' в позиции {i}")

    return tokens


def validate_tokens(tokens):
    """
    Валидация последовательности токенов
    """
    if not tokens:
        raise ValueError("Пустое выражение")

    functions = {'sin', 'cos', 'tg', 'ctg'}
    postfix_ops = {'++', '--', '!'}

    operators = {'+', '-', '*', '/', '^'}

    def is_operand(token):
        return (token not in operators and
                token not in postfix_ops and
                token not in '()' and
                token not in functions)


    first = tokens[0]
    if first in operators:
        if first != '-':
            raise ValueError(f"Выражение не может начинаться с бинарного оператора '{first}'")
    if first in postfix_ops:
        raise ValueError(f"Выражение не может начинаться с постфиксного оператора '{first}'")


    last = tokens[-1]
    if last in operators:
        raise ValueError(f"Выражение не может заканчиваться оператором '{last}'")


    balance = 0
    for i in range(len(tokens)):
        token = tokens[i]

        if i > 0:
            prev = tokens[i - 1]

            if is_operand(prev) and is_operand(token):
                pass

            if (prev in operators and token in operators):
                raise ValueError(f"Два оператора подряд: '{prev}' и '{token}'")

            if prev in postfix_ops and is_operand(token):
                raise ValueError(f"После постфиксного оператора '{prev}' должен следовать бинарный оператор")

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
        '~': 5,
        '!': 6, '++': 6, '--': 6
    }
    return precedence.get(op, 0)

def is_right_associative(op):
    right_assoc = {'^', '~', '++', '--'}
    return op in right_assoc


def is_function(token):
    functions = {'sin', 'cos', 'tg', 'ctg'}
    return token in functions


def shunting_yard(tokens):
    output = []
    stack = []
    functions = {'sin', 'cos', 'tg', 'ctg'}
    postfix_ops = {'++', '--', '!'}
    operators = {'+', '-', '*', '/', '^'}

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if (token not in operators and
                token not in postfix_ops and
                token not in '()' and
                token not in functions):
            output.append(token)

        elif token in functions:
            stack.append(token)

        elif token in postfix_ops:
            output.append(token)

        elif token == '(':
            stack.append(token)

        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()
            if stack and stack[-1] in functions:
                output.append(stack.pop())

        elif token in operators:
            if token == '-':
                is_unary = (i == 0 or
                            tokens[i - 1] in operators or
                            tokens[i - 1] == '(' or
                            tokens[i - 1] in functions)
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
