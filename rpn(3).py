import re

OPS = {
    '+': (1, 'L', 2), '-': (1, 'L', 2),
    '*': (2, 'L', 2), '/': (2, 'L', 2),
    '^': (3, 'R', 2),
    '~': (4, 'R', 1),
    '!': (5, 'L', 1),
    '++': (5, 'L', 1), '--': (5, 'L', 1),
}

FUNCS = {'sin', 'cos', 'tg', 'ctg'}

token_re = re.compile(r'(\+\+|--|[()+\-*/^!~,]|[a-zA-Zа-яА-Я0-9]+)')


def tokenize(expr):
    raw = token_re.findall(expr.replace(' ', ''))
    tokens, prev = [], None

    for t in raw:
        if tokens and t.isalnum() and tokens[-1].isalnum():
            tokens[-1] += t
            continue

        if t == '-' and (prev is None or prev in OPS or prev == '('):
            t = '~'

        tokens.append(t)
        prev = t

    return tokens


def validate(tokens):
    if not tokens:
        raise ValueError("Пустое выражение")

    prev = None
    balance = 0

    for i, t in enumerate(tokens):

        if t == '(':
            balance += 1
        elif t == ')':
            balance -= 1
            if balance < 0:
                raise ValueError("Лишняя ')'")

        if prev in OPS and t in OPS:
            if OPS[prev][2] == 2 and OPS[t][2] == 2:
                raise ValueError(f"Ошибка: '{prev}{t}'")

        if i == 0 and t in OPS and OPS[t][2] == 2:
            raise ValueError(f"Начало с '{t}' недопустимо")

        if i == len(tokens) - 1 and t in OPS and OPS[t][2] == 2:
            raise ValueError(f"Конец на '{t}' недопустим")

        prev = t

    if balance != 0:
        raise ValueError("Несбалансированные скобки")


def to_rpn(tokens, debug=False):
    out, stack = [], []

    for t in tokens:
        if t.isalnum():
            out.append(t)

        elif t in FUNCS:
            stack.append(t)

        elif t in OPS:
            p, assoc, _ = OPS[t]
            while stack and stack[-1] in OPS:
                p2, assoc2, _ = OPS[stack[-1]]
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
