import re

# приоритет, ассоциативность (L/R), арность
OPS = {
    '+': (1, 'L', 2), '-': (1, 'L', 2),
    '*': (2, 'L', 2), '/': (2, 'L', 2),
    '^': (3, 'R', 2),
    '~': (4, 'R', 1),  # унарный минус
    '!': (5, 'L', 1),
    '++': (5, 'L', 1), '--': (5, 'L', 1),
}

FUNCS = {'sin', 'cos', 'tg', 'ctg'}

token_re = re.compile(r'\s*(\d+[a-zA-Zа-яА-Я]*|[a-zA-Zа-яА-Я]+|\+\+|--|[()+\-*/^!~,])')

def tokenize(expr):
    tokens = token_re.findall(expr)
    res, prev = [], None
    for t in tokens:
        if t == '-' and (prev is None or prev in OPS or prev == '('):
            t = '~'
        res.append(t)
        prev = t
    return res

def to_rpn(tokens):
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
    while stack:
        out.append(stack.pop())
    return out

def parse(expr):
    return to_rpn(tokenize(expr))


# пример
expr = "sin(2+3)*11aa--"
print(parse(expr))
