"""Конвертер инфикс → RPN. Легко настраиваемый через registry."""

from __future__ import annotations
from typing import List, Optional

OPERATORS = [
    ("+", 2, 2, "L"),
    ("-", 2, 2, "L"),
    ("*", 2, 3, "L"),
    ("/", 2, 3, "L"),
    ("^", 2, 4, "R"),
    ("~", 1, 5, "R"),
    ("!", 1, 6, None),
    ("++", 1, 6, None),
    ("--", 1, 6, None),
    ("sin", 1, 8, None),
    ("cos", 1, 8, None),
    ("tg", 1, 8, None),
    ("ctg", 1, 8, None),
]

POSTFIX_OPS = {"++", "--", "!"}
TRIG_NAMES = {"sin", "cos", "tg", "ctg"}


class Op:
    _reg = {}

    def __init__(self, name: str, arity: int, prec: int, ass: Optional[str] = None):
        self.name = name
        self.arity = arity
        self.prec = prec
        self.ass = ass
        Op._reg[name] = self

    @classmethod
    def reg_all(cls):
        cls._reg.clear()
        for name, arity, prec, ass in OPERATORS:
            cls(name, arity, prec, ass)

    @classmethod
    def get(cls, name: str) -> Optional[Op]:
        return cls._reg.get(name)

    @classmethod
    def is_binary(cls, t: str) -> bool:
        op = cls.get(t)
        return op is not None and op.arity == 2

    @classmethod
    def is_prefix(cls, t: str) -> bool:
        op = cls.get(t)
        return op is not None and op.arity == 1 and t not in POSTFIX_OPS

    @classmethod
    def is_operand(cls, t: str) -> bool:
        return t not in "()" and cls.get(t) is None

def tokenize(expr: str) -> List[str]:
    tokens, i, n = [], 0, len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if i + 1 < n and expr[i:i+2] in POSTFIX_OPS:
            tokens.append(expr[i:i+2])
            i += 2
            continue
        if c.isalnum() or c == '.':
            j = i + 1
            while j < n and (expr[j].isalnum() or expr[j] == '.'):
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue
        if c in "+-*/^()!":
            tokens.append(c)
            i += 1
            continue
        raise ValueError(f"Неизвестный символ: {c!r}")
    return tokens

POSTFIX_OPS = {"++", "--", "!"}
TRIG_NAMES = {"sin", "cos", "tg", "ctg"}

class InfixToRpn:
    def __init__(self, expr: str):
        Op.reg_all()
        self.source = expr
        raw = tokenize(expr)
        self.tokens = self._fold_unary(raw)

    def _fold_unary(self, tokens: List[str]) -> List[str]:
        """Заменяет унарный '-' на '~'"""
        res = []
        for i, t in enumerate(tokens):
            if t != '-':
                res.append(t)
                continue
            prev = res[-1] if res else None
            if prev is None or prev == '(' or Op.is_binary(prev) or Op.is_prefix(prev):
                res.append('~')
            else:
                res.append('-')
        return res

    def _validate(self) -> None:
        """Проверка структуры выражения"""
        ts = self.tokens
        if not ts:
            raise ValueError("Пустое выражение")

        if Op.is_binary(ts[0]):
            raise ValueError(f"Нельзя начинать с «{ts[0]}»")
        if ts[0] in POSTFIX_OPS:
            raise ValueError("Постфиксный оператор не может быть в начале")
        if Op.is_binary(ts[-1]):
            raise ValueError(f"Нельзя заканчивать оператором «{ts[-1]}»")
        if Op.is_prefix(ts[-1]):
            raise ValueError(f"После «{ts[-1]}» должно быть выражение")

        balance = 0
        for i, curr in enumerate(ts):
            if curr == '(':
                balance += 1
            elif curr == ')':
                balance -= 1
                if balance < 0:
                    raise ValueError("Лишняя ')'")
            if i == 0:
                continue

            prev = ts[i-1]

            if Op.is_operand(prev) and (Op.is_operand(curr) or curr == '(' or Op.is_prefix(curr)):
                raise ValueError(f"Нужен оператор между «{prev}» и «{curr}»")
            if prev == ')' and (curr == '(' or Op.is_operand(curr) or Op.is_prefix(curr)):
                raise ValueError(f"Нужен оператор между «{prev}» и «{curr}»")

            if prev in POSTFIX_OPS and curr == '(':
                raise ValueError(f"После «{prev}» нужен оператор, а не «(»")

            if curr in TRIG_NAMES and not (prev in '()' or Op.get(prev)):
                raise ValueError(f"Нужен оператор между «{prev}» и «{curr}»")

            if Op.is_prefix(prev) and (Op.is_binary(curr) or curr == ')' or curr in POSTFIX_OPS):
                raise ValueError(f"После «{prev}» нужно выражение, а не «{curr}»")

            if Op.is_binary(prev) and Op.is_binary(curr):
                raise ValueError(f"Два бинарных подряд: «{prev}» и «{curr}»")

            if curr in POSTFIX_OPS and not (Op.is_operand(prev) or prev == ')'):
                raise ValueError(f"«{curr}» должен идти сразу после операнда")

        if balance != 0:
            raise ValueError("Несбалансированные скобки")

    def to_rpn(self) -> str:
        """Преобразование в RPN"""
        self._validate()
        output, stack = [], []

        for tok in self.tokens:
            if Op.is_operand(tok):
                output.append(tok)
                while stack and Op.is_prefix(stack[-1]):
                    output.append(stack.pop())
                continue

            if Op.is_prefix(tok):
                stack.append(tok)
                continue

            if tok in POSTFIX_OPS:
                output.append(tok)
                continue

            if tok == '(':
                stack.append(tok)
                continue

            if tok == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack:
                    raise ValueError("Непарная скобка")
                stack.pop()
                while stack and Op.is_prefix(stack[-1]):
                    output.append(stack.pop())
                continue

            inc = Op.get(tok)
            if not inc:
                raise ValueError(f"Неизвестный токен: {tok!r}")

            while stack and stack[-1] != '(' and not Op.is_prefix(stack[-1]):
                top = Op.get(stack[-1])
                if top and (top.prec > inc.prec or (top.prec == inc.prec and (inc.ass or 'L') == 'L')):
                    output.append(stack.pop())
                else:
                    break
            stack.append(tok)

        while stack:
            if stack[-1] == '(':
                raise ValueError("Несбалансированные скобки")
            output.append(stack.pop())

        depth = 0
        for t in output:
            if Op.is_operand(t):
                depth += 1
            elif t in POSTFIX_OPS or Op.is_prefix(t):
                if depth < 1:
                    raise ValueError(f"Не хватает операнда для «{t}»")
            elif Op.is_binary(t):
                if depth < 2:
                    raise ValueError(f"Не хватает операндов для «{t}»")
                depth -= 1
        if depth != 1:
            raise ValueError("Выражение не сводится к одному значению")

        return ' '.join(output)

def interactive():
    """Интерактивный режим"""
    print("\n=== Инфикс → RPN === Введите 'exit' для выхода ===\n")
    while True:
        expr = input("> ").strip()
        if expr.lower() == 'exit':
            break
        if not expr:
            continue
        try:
            print(f"RPN: {InfixToRpn(expr).to_rpn()}")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":

    interactive()
