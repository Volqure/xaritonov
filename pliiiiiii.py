"""Инфикс → RPN. Некорректная запись отсекается до построения постфикса."""
from __future__ import annotations

from typing import List, Optional


# --- реестр операторов (меняете здесь) ----------------------------------------
class tokenSet:
    registry: dict[str, "tokenSet"] = {}

    def __init__(self, name: str, arnost: int, prec: int, ass: Optional[str] = None):
        self.name, self.arnost, self.prec, self.ass = name, arnost, prec, ass
        tokenSet.registry[name] = self

    @classmethod
    def register_builtin(cls) -> None:
        cls.registry.clear()
        for name, prec, ass in [
            ("+", 2, "L"),
            ("-", 2, "L"),
            ("*", 3, "L"),
            ("/", 3, "L"),
            ("^", 4, "R"),
        ]:
            tokenSet(name, 2, prec, ass)
        tokenSet("~", 1, 5, "R")
        for s in ("!", "++", "--"):
            tokenSet(s, 1, 6, None)
        for s in ("sin", "cos", "tg", "ctg"):
            tokenSet(s, 1, 8, None)

    @classmethod
    def get(cls, name: str) -> Optional["tokenSet"]:
        return cls.registry.get(name)


class Lexer:
    POSTFIX = frozenset({"++", "--", "!"})

    @staticmethod
    def scan(text: str) -> List[str]:
        out, i, n = [], 0, len(text)
        while i < n:
            c = text[i]
            if c.isspace():
                i += 1
                continue
            if i + 1 < n and text[i : i + 2] in Lexer.POSTFIX:
                out.append(text[i : i + 2])
                i += 2
                continue
            if c.isalnum() or c == ".":
                j = i + 1
                while j < n and (text[j].isalnum() or text[j] == "."):
                    j += 1
                out.append(text[i:j])
                i = j
                continue
            if c in "+-*/^()!":
                out.append(c)
                i += 1
                continue
            raise ValueError(f"Неизвестный символ: {c!r}")
        return out


class Grammar:
    """Классификация токенов по operator registry и Lexer.POSTFIX."""
    TRIG = frozenset({"sin", "cos", "tg", "ctg"})
    ERR_NEED_BINARY = (
        "Нужен явный бинарный оператор (+ - * / ^) между «{prev}» и «{curr}» "
        "(неявное умножение отключено)."
    )

    @classmethod
    def meta(cls, t: str) -> Optional[tokenSet]:
        return tokenSet.get(t)

    @classmethod
    def is_lit(cls, t: str) -> bool:
        return t not in "()" and cls.meta(t) is None

    @classmethod
    def is_b(cls, t: str) -> bool:
        m = cls.meta(t)
        return m is not None and m.arnost == 2

    @classmethod
    def is_pf(cls, t: str) -> bool:
        return t in Lexer.POSTFIX

    @classmethod
    def is_pr(cls, t: str) -> bool:
        m = cls.meta(t)
        return m is not None and m.arnost == 1 and not cls.is_pf(t)

    @classmethod
    def unary_minus_context(cls, prev: Optional[str]) -> bool:
        if prev is None or prev == "(":
            return True
        if cls.is_pf(prev):
            return False
        return cls.is_b(prev) or cls.is_pr(prev)


class PairRules:
    """Все локальные ограничения на соседние токены; возвращает текст ошибки или None."""

    @staticmethod
    def check(prev: str, curr: str) -> Optional[str]:
        g, E = Grammar, Grammar.ERR_NEED_BINARY.format
        # нельзя «склеивать» факторы без *
        if g.is_lit(prev) and (
            g.is_lit(curr) or curr == "(" or g.is_pr(curr)
        ):
            return E(prev=prev, curr=curr)
        if prev == ")" and (
            curr == "(" or g.is_lit(curr) or g.is_pr(curr)
        ):
            return E(prev=prev, curr=curr)
        if curr in Grammar.TRIG and g.is_lit(prev) and prev not in "()":
            return E(prev=prev, curr=curr)
        if g.is_pr(prev) and (g.is_b(curr) or curr == ")" or g.is_pf(curr)):
            return (
                f"После «{prev}» должно идти выражение (аргумент), "
                f"а не «{curr}» — пустой или незавершённый аргумент недопустим."
            )
        if g.is_pf(prev) and curr == "(":
            return (
                f"После постфиксного «{prev}» нельзя сразу писать «(» — "
                f"укажите бинарный оператор (+ - * / ^) между частями выражения."
            )
        if g.is_b(prev) and g.is_b(curr):
            return f"Два бинарных оператора подряд: «{prev}» и «{curr}»"
        if g.is_pf(prev) and g.is_lit(curr):
            return f"После «{prev}» нужен бинарный оператор, а не операнд «{curr}»"
        if g.is_pf(curr) and not g.is_lit(prev) and prev != ")":
            return f"«{curr}» должно следовать сразу за операндом или «)»"
        return None


class StructureValidator:
    def __init__(self, ts: List[str]):
        self.ts = ts

    def validate(self) -> None:
        ts = self.ts
        if not ts:
            raise ValueError("Пустое выражение")
        g = Grammar
        if g.is_b(ts[0]):
            raise ValueError(f"Выражение не может начинаться с «{ts[0]}»")
        if g.is_pf(ts[0]):
            raise ValueError("Постфиксный оператор не может быть в начале")
        if g.is_b(ts[-1]):
            raise ValueError(f"Выражение не может заканчиваться оператором «{ts[-1]}»")
        if g.is_pr(ts[-1]):
            raise ValueError(
                f"После «{ts[-1]}» должно быть выражение (аргумент), нельзя обрывать на операторе."
            )

        bal = 0
        for i, curr in enumerate(ts):
            if curr == "(":
                bal += 1
            elif curr == ")":
                bal -= 1
                if bal < 0:
                    raise ValueError("Лишняя закрывающая скобка")
            if i == 0:
                continue
            prev = ts[i - 1]
            msg = PairRules.check(prev, curr)
            if msg:
                raise ValueError(msg)
        if bal != 0:
            raise ValueError("Несбалансированные скобки")


class RpnShape:
    """Проверка: постфикс даёт ровно одно значение на стеке."""

    @staticmethod
    def assert_single(rpn: List[str]) -> None:
        d = 0
        for t in rpn:
            m = tokenSet.get(t)
            if m is None:
                d += 1
            elif m.arnost == 2:
                if d < 2:
                    raise ValueError(
                        f"К бинарному оператору «{t}» в постфиксе не хватает операндов."
                    )
                d -= 1
            else:
                if d < 1:
                    raise ValueError(
                        f"К унарному оператору «{t}» в постфиксе не хватает операнда."
                    )
        if d != 1:
            raise ValueError(
                "Выражение не сводится к одному значению: в постфиксе получается несколько "
                "независимых результатов — добавьте недостающие бинарные операторы (+ - * / ^) "
                "или скобки так, чтобы была одна цельная формула."
            )


class ShuntingYard:
    """Сортировочная станция (Дейкстры)."""

    @classmethod
    def _pop_before(cls, top: str, inc: tokenSet) -> bool:
        if top == "(" or Grammar.is_pr(top):
            return False
        st = tokenSet.get(top)
        if st is None:
            return False
        if st.prec > inc.prec:
            return True
        if st.prec == inc.prec:
            return (inc.ass or "L") == "L"
        return False

    @classmethod
    def convert(cls, ts: List[str]) -> List[str]:
        out: List[str] = []
        st: List[str] = []
        for tok in ts:
            if Grammar.is_lit(tok):
                out.append(tok)
                while st and Grammar.is_pr(st[-1]):
                    out.append(st.pop())
                continue
            if Grammar.is_pr(tok):
                st.append(tok)
                continue
            if Grammar.is_pf(tok):
                out.append(tok)
                continue
            if tok == "(":
                st.append(tok)
                continue
            if tok == ")":
                while st and st[-1] != "(":
                    out.append(st.pop())
                if not st:
                    raise ValueError("Непарная скобка")
                st.pop()
                while st and Grammar.is_pr(st[-1]):
                    out.append(st.pop())
                continue

            inc = tokenSet.get(tok)
            if inc is None:
                raise ValueError(f"Неожиданный токен: {tok!r}")
            while st and cls._pop_before(st[-1], inc):
                out.append(st.pop())
            st.append(tok)

        while st:
            t = st.pop()
            if t == "(":
                raise ValueError("Несбалансированные скобки")
            out.append(t)
        return out


class InfixToRpn:
    def __init__(self, expression: str):
        tokenSet.register_builtin()
        self._src = expression
        self.tokens = self._fold_minus(Lexer.scan(expression))

    def debug_snapshot(self) -> str:
        return f"исходник={self._src!r}\nтокены={self.tokens}"

    @staticmethod
    def _fold_minus(ts: List[str]) -> List[str]:
        g, r = Grammar, []
        for t in ts:
            if t != "-":
                r.append(t)
                continue
            p = r[-1] if r else None
            r.append("~" if (p == "(" or g.unary_minus_context(p)) else "-")
        return r

    def _build(self) -> str:
        StructureValidator(self.tokens).validate()
        rpn = ShuntingYard.convert(self.tokens)
        RpnShape.assert_single(rpn)
        return " ".join(rpn)

    def to_rpn(self) -> str:
        return self._build()


def main() -> None:
    while True:
        expr = input("\nВыражение (exit для выхода): ").strip()
        if expr.lower() == "exit":
            break
        if not expr:
            continue
        try:
            print(f"RPN: {InfixToRpn(expr).to_rpn()}")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    from pathlib import Path

    p = Path(__file__).resolve()
    print(f"Запущен скрипт: {p}")
    if " " in p.name and "(" in p.name:
        print(
            "(Удобнее скопировать в файл с простым именем, например infix_rpn.py, и запускать его.)"
        )
    main()
