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


# 🔹 токенизация + склейка операндов
def tokenize(expr):
    raw = token_re.findall(expr.replace(' ', ''))
    
    tokens = []
    prev = None

    for t in raw:
        # если подряд идут операнды → склеиваем
        if tokens and t.isalnum() and tokens[-1].isalnum():
            tokens[-1] += t
            continue

        # унарный минус
        if t == '-' and (prev is None or prev in OPS or prev == '('):
            t = '~'

        tokens.append(t)
        prev = t

    return tokens


# 🔹 красивый вывод
def fmt(stack, out):
    return f"STACK: [{' '.join(stack)}] | OUT: [{' '.join(out)}]"


# 🔹 алгоритм сортировочной станции
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
            if not stack:
                raise ValueError("Ошибка: лишняя закрывающая скобка")
            stack.pop()
            if stack and stack[-1] in FUNCS:
                out.append(stack.pop())

        else:
            raise ValueError(f"Неизвестный токен: {t}")

        if debug:
            print(f"{t:>6} -> {fmt(stack, out)}")

    while stack:
        if stack[-1] == '(':
            raise ValueError("Ошибка: незакрытая скобка")
        out.append(stack.pop())
        if debug:
            print(f"{'END':>6} -> {fmt(stack, out)}")

    return out


# 🔹 основная функция
def parse(expr, debug=False):
    tokens = tokenize(expr)
    if debug:
        print("TOKENS:", tokens)
    return to_rpn(tokens, debug)


# 🔹 пример
if __name__ == "__main__":
    expr = "aaa 333 + sin(2+3)*11aa--"
    rpn = parse(expr, debug=True)
    print("RPN:", rpn)
