from typing import List

class tokenSet:
    dict={}
    def __init__(self,name,arnost,prec,ass=None):
        self.name=name
        self.arnost=arnost
        self.prec=prec
        self.ass=ass
        self.dict[name]=self
    @classmethod
    def addSymbols(cls):
        for c in "abcdefghijklmnopq":
            tokenSet(c....)

    def addDigits(cls):
        for c in "abcdefghijklmnopq":
            tokenSet(c....)

OPERATORS = {'+', '-', '*', '/', '^'}
POSTFIX_OPS = {'++', '--', '!'}
FUNCTIONS = {'sin', 'cos', 'tg', 'ctg'}
ALL_OPS = OPERATORS | POSTFIX_OPS

PRECEDENCE = {'+': 2, '-': 2, '*': 3, '/': 3, '^': 4, '~': 5, '!': 6, '++': 6, '--': 6}
RIGHT_ASSOC = {'^', '~', '++', '--'}


def tokenize(expr: str) -> List[str]:
    tokens, i, n = [], 0, len(expr)

    while i < n:
        c = expr[i]
        if c == ' ':
            i += 1
            continue

        if c.isalnum():
            j = i
            while j < n and expr[j].isalnum():
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue

        if i + 1 < n and expr[i:i + 2] in POSTFIX_OPS:
            tokens.append(expr[i:i + 2])
            i += 2
            continue

        if c in '+-*/^()!.':
            tokens.append(c)
            i += 1
            continue

        raise ValueError(f"Неизвестный символ: '{c}'")

    return tokens


def validate(tokens: List[str]) -> None:
    if not tokens:
        raise ValueError("Пустое выражение")

    def is_operand(t: str) -> bool:
        return t not in ALL_OPS and t not in '()' and t not in FUNCTIONS

    if tokens[0] in OPERATORS - {'-'}:
        raise ValueError(f"Выражение не может начинаться с '{tokens[0]}'")
    if tokens[0] in POSTFIX_OPS:
        raise ValueError(f"Постфиксный оператор не может быть в начале")
    if tokens[-1] in OPERATORS:
        raise ValueError(f"Выражение не может заканчиваться оператором '{tokens[-1]}'")

    balance = 0
    for i, (prev, curr) in enumerate(zip([''] + tokens[:-1], tokens)):
        if curr == '(':
            balance += 1
        elif curr == ')':
            balance -= 1
            if balance < 0:
                raise ValueError("Лишняя закрывающая скобка")

        if i == 0:
            continue

        if is_operand(prev) and is_operand(curr):
            raise ValueError(f"Отсутствует оператор между '{prev}' и '{curr}'")
        if prev in OPERATORS and curr in OPERATORS:
            raise ValueError(f"Два оператора подряд: '{prev}' и '{curr}'")
        if prev in POSTFIX_OPS and is_operand(curr):
            raise ValueError(f"После '{prev}' должен следовать бинарный оператор")
        if curr in POSTFIX_OPS and not is_operand(prev) and prev != ')':
            raise ValueError(f"'{curr}' должен следовать за операндом")

    if balance != 0:
        raise ValueError("Несбалансированные скобки")


def get_precedence(op: str) -> int:
    return PRECEDENCE.get(op, 0)


def is_right_assoc(op: str) -> bool:
    return op in RIGHT_ASSOC


def shunting_yard(tokens: List[str]) -> str:
    output, stack = [], []

    for i, token in enumerate(tokens):
        if token not in ALL_OPS and token not in '()' and token not in FUNCTIONS:
            output.append(token)

        elif token in FUNCTIONS:
            stack.append(token)
        elif token in POSTFIX_OPS:
            output.append(token)

        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
            if stack and stack[-1] in FUNCTIONS:
                output.append(stack.pop())

        elif token in OPERATORS:
            if token == '-' and (i == 0 or tokens[i - 1] in OPERATORS | {'('} | FUNCTIONS):
                token = '~'

            while (stack and stack[-1] != '(' and stack[-1] not in FUNCTIONS and
                   (get_precedence(stack[-1]) > get_precedence(token) or
                    (get_precedence(stack[-1]) == get_precedence(token) and not is_right_assoc(token)))):
                output.append(stack.pop())
            stack.append(token)

    while stack:
        output.append(stack.pop())

    return ' '.join(output)


def infix_to_rpn(expression: str) -> str:
    tokens = tokenize(expression)
    validate(tokens)
    return shunting_yard(tokens)


def main():
    print("=" * 60)
    print("Преобразование инфиксной записи в RPN")
    print("=" * 60)
    print("Операторы: + - * / ^ ! ++ --")
    print("Функции: sin cos tg ctg")
    print("=" * 60)

    print("\n" + "=" * 60)
    while True:
        expr = input("\nВыражение (exit для выхода): ").strip()
        if expr.lower() == 'exit':
            break
        if expr:
            try:
                print(f"RPN: {infix_to_rpn(expr)}")
            except Exception as e:
                print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
