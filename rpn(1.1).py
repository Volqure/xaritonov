"""Конвертер инфикс → RPN. Некорректная инфиксная запись отсекает _validate_structure до построения RPN."""
from __future__ import annotations

from typing import List, Optional


# =============================================================================
# Реестр операторов: имя, арность, приоритет, ассоциативность ("L"/"R"/None).
# Меняете только здесь — классификация токенов подстроится под tokenSet.
# =============================================================================


class tokenSet:
    # Имя «registry», не «dict», чтобы не путать со встроенным типом dict.
    registry: dict[str, "tokenSet"] = {}

    def __init__(self, name: str, arnost: int, prec: int, ass: Optional[str] = None):
        self.name = name
        self.arnost = arnost
        self.prec = prec
        self.ass = ass
        tokenSet.registry[name] = self

    @classmethod
    def register_builtin(cls) -> None:
        cls.registry.clear()
        tokenSet("+", 2, 2, "L")
        tokenSet("-", 2, 2, "L")
        tokenSet("*", 2, 3, "L")
        tokenSet("/", 2, 3, "L")
        tokenSet("^", 2, 4, "R")
        tokenSet("~", 1, 5, "R")
        tokenSet("!", 1, 6, None)
        tokenSet("++", 1, 6, None)
        tokenSet("--", 1, 6, None)
        tokenSet("sin", 1, 8, None)
        tokenSet("cos", 1, 8, None)
        tokenSet("tg", 1, 8, None)
        tokenSet("ctg", 1, 8, None)

    @classmethod
    def get(cls, name: str) -> Optional["tokenSet"]:
        return cls.registry.get(name)


class Lexer:
    POSTFIX = frozenset({"++", "--", "!"})

    def __init__(self, text: str):
        self.text = text
        self.n = len(text)

    def tokens(self) -> List[str]:
        out: List[str] = []
        i = 0
        while i < self.n:
            c = self.text[i]
            if c.isspace():
                i += 1
                continue
            if i + 1 < self.n and self.text[i : i + 2] in Lexer.POSTFIX:
                out.append(self.text[i : i + 2])
                i += 2
                continue
            if c.isalnum() or c == ".":
                j = i + 1
                while j < self.n and (self.text[j].isalnum() or self.text[j] == "."):
                    j += 1
                out.append(self.text[i:j])
                i = j
                continue
            if c in "+-*/^()!":
                out.append(c)
                i += 1
                continue
            raise ValueError(f"Неизвестный символ: {c!r}")
        return out


# =============================================================================
# InfixToRpn — вся логика конвертации в одном классе:
#   1) tokenize (Lexer) → 2) нормализация − / ~ → 3) проверка структуры
#   → 4) сортировочная станция.
# Для отладки: вызовите .debug_snapshot() после создания объекта.
# =============================================================================


class InfixToRpn:
    ERR_NEED_BINARY = (
        "Нужен явный бинарный оператор (+ - * / ^) между «{prev}» и «{curr}» "
        "(неявное умножение отключено)."
    )
    # Подстраховка (не только через registry): «число/переменная» + тригонометрия без *
    TRIG_NAMES = frozenset({"sin", "cos", "tg", "ctg"})

    def __init__(self, expression: str):
        tokenSet.register_builtin()
        self._source = expression
        raw = Lexer(expression).tokens()
        self.tokens = self._fold_unary_minus(raw)

    def debug_snapshot(self) -> str:
        return f"исходник={self._source!r}\nтокены={self.tokens}"

    # --- классификация (смотрит только tokenSet и Lexer.POSTFIX) ---

    @staticmethod
    def _is_binary(t: str) -> bool:
        m = tokenSet.get(t)
        return m is not None and m.arnost == 2

    @classmethod
    def _is_postfix_unary(cls, t: str) -> bool:
        return t in Lexer.POSTFIX

    @classmethod
    def _is_prefix_unary(cls, t: str) -> bool:
        m = tokenSet.get(t)
        return m is not None and m.arnost == 1 and not cls._is_postfix_unary(t)

    @classmethod
    def _operand(cls, t: str) -> bool:
        if t in "()":
            return False
        return tokenSet.get(t) is None

    @classmethod
    def _minus_means_unary(cls, prev: Optional[str]) -> bool:
        if prev is None or prev == "(":
            return True
        if cls._is_postfix_unary(prev):
            return False
        return cls._is_binary(prev) or cls._is_prefix_unary(prev)

    # --- нормализация ---

    def _fold_unary_minus(self, tokens: List[str]) -> List[str]:
        folded: List[str] = []
        for tok in tokens:
            if tok != "-":
                folded.append(tok)
                continue
            prev = folded[-1] if folded else None
            if prev == "(" or self._minus_means_unary(prev):
                folded.append("~")
            else:
                folded.append("-")
        return folded

    # --- проверка: все правила «что не может стоять рядом» в одном месте ---

    def _pair_error(self, prev: str, curr: str) -> Optional[str]:
        """Вернуть текст ошибки или None, если пара допустима."""
        if self._operand(prev) and (
            self._operand(curr)
            or curr == "("
            or self._is_prefix_unary(curr)
        ):
            return self.ERR_NEED_BINARY.format(prev=prev, curr=curr)
        if prev == ")" and (
            curr == "("
            or self._operand(curr)
            or self._is_prefix_unary(curr)
        ):
            return self.ERR_NEED_BINARY.format(prev=prev, curr=curr)
        return None

    def _postfix_then_open_paren(self, prev: str, curr: str) -> Optional[str]:
        """x-- ( ... без * между постфиксом и скобкой даёт два «хвоста» на стеке при вычислении."""
        if self._is_postfix_unary(prev) and curr == "(":
            return (
                f"После постфиксного «{prev}» нельзя сразу писать «(» — "
                f"укажите бинарный оператор (+ - * / ^) между частями выражения."
            )
        return None

    def _operand_then_trig_without_operator(self, prev: str, curr: str) -> Optional[str]:
        """
        Жёсткая проверка:  «32132 sin» и аналоги всегда ошибка,
        даже если классификация через tokenSet по какой-то причине не сработала.
        """
        if curr not in self.TRIG_NAMES:
            return None
        if prev in "()":
            return None
        if tokenSet.get(prev) is not None:
            return None
        return self.ERR_NEED_BINARY.format(prev=prev, curr=curr)

    def _prefix_argument_missing(self, prev: str, curr: str) -> Optional[str]:
        """После префиксного унарного (sin, ~, …) должно начинаться выражение-аргумент."""
        if not self._is_prefix_unary(prev):
            return None
        if self._is_binary(curr) or curr == ")" or self._is_postfix_unary(curr):
            return (
                f"После «{prev}» должно идти выражение (аргумент), "
                f"а не «{curr}» — пустой или незавершённый аргумент недопустим."
            )
        return None

    def _validate_structure(self) -> None:
        ts = self.tokens
        if not ts:
            raise ValueError("Пустое выражение")

        if self._is_binary(ts[0]):
            raise ValueError(f"Выражение не может начинаться с «{ts[0]}»")
        if self._is_postfix_unary(ts[0]):
            raise ValueError("Постфиксный оператор не может быть в начале")
        if self._is_binary(ts[-1]):
            raise ValueError(f"Выражение не может заканчиваться оператором «{ts[-1]}»")
        if self._is_prefix_unary(ts[-1]):
            raise ValueError(
                f"После «{ts[-1]}» должно быть выражение (аргумент), нельзя обрывать на операторе."
            )

        balance = 0
        for i, curr in enumerate(ts):
            if curr == "(":
                balance += 1
            elif curr == ")":
                balance -= 1
                if balance < 0:
                    raise ValueError("Лишняя закрывающая скобка")

            if i == 0:
                continue
            prev = ts[i - 1]

            msg = self._pair_error(prev, curr)
            if msg:
                raise ValueError(msg)

            msg0 = self._operand_then_trig_without_operator(prev, curr)
            if msg0:
                raise ValueError(msg0)

            msg2 = self._prefix_argument_missing(prev, curr)
            if msg2:
                raise ValueError(msg2)

            msg3 = self._postfix_then_open_paren(prev, curr)
            if msg3:
                raise ValueError(msg3)

            if self._is_binary(prev) and self._is_binary(curr):
                raise ValueError(f"Два бинарных оператора подряд: «{prev}» и «{curr}»")
            if self._is_postfix_unary(prev) and self._operand(curr):
                raise ValueError(f"После «{prev}» нужен бинарный оператор, а не операнд «{curr}»")
            if self._is_postfix_unary(curr) and not self._operand(prev) and prev != ")":
                raise ValueError(f"«{curr}» должно следовать сразу за операндом или «)»")

        if balance != 0:
            raise ValueError("Несбалансированные скобки")

    def _assert_rpn_single_value(self, rpn_tokens: List[str]) -> None:
        """
        Модель вычисления постфикса: в конце на стеке должно остаться ровно одно значение.
        Иначе (как в 312321--(...)--) при подсчёте остаётся несколько операндов без связи.
        """
        depth = 0
        for t in rpn_tokens:
            meta = tokenSet.get(t)
            if meta is None:
                depth += 1
                continue
            if meta.arnost == 2:
                if depth < 2:
                    raise ValueError(
                        f"К бинарному оператору «{t}» в постфиксе не хватает операндов."
                    )
                depth -= 1
            else:
                if depth < 1:
                    raise ValueError(
                        f"К унарному оператору «{t}» в постфиксе не хватает операнда."
                    )
        if depth != 1:
            raise ValueError(
                "Выражение не сводится к одному значению: в постфиксе получается несколько "
                "независимых результатов — добавьте недостающие бинарные операторы (+ - * / ^) "
                "или скобки так, чтобы была одна цельная формула."
            )

    # --- сортировочная станция: одна цель — собрать постфикс ---

    def _should_pop_for_incoming(self, stack_top: str, incoming_meta: tokenSet) -> bool:
        if stack_top == "(":
            return False
        if self._is_prefix_unary(stack_top):
            return False
        st = tokenSet.get(stack_top)
        if st is None:
            return False
        if st.prec > incoming_meta.prec:
            return True
        if st.prec == incoming_meta.prec:
            # бинарные операторы имеют ass "L" или "R"; None трактуем как левую ассоциативность
            return (incoming_meta.ass or "L") == "L"
        return False

    def _build_rpn_output(self) -> str:
        """Проверка инфикса и сортировочная станция — всегда вместе, одна точка входа в алгоритм."""
        self._validate_structure()
        output: List[str] = []
        stack: List[str] = []

        for token in self.tokens:
            if self._operand(token):
                output.append(token)
                while stack and self._is_prefix_unary(stack[-1]):
                    output.append(stack.pop())
                continue

            if self._is_prefix_unary(token):
                stack.append(token)
                continue

            if self._is_postfix_unary(token):
                output.append(token)
                continue

            if token == "(":
                stack.append(token)
                continue

            if token == ")":
                while stack and stack[-1] != "(":
                    output.append(stack.pop())
                if not stack:
                    raise ValueError("Непарная скобка")
                stack.pop()
                while stack and self._is_prefix_unary(stack[-1]):
                    output.append(stack.pop())
                continue

            inc = tokenSet.get(token)
            if inc is None:
                raise ValueError(f"Неожиданный токен: {token!r}")

            while stack and self._should_pop_for_incoming(stack[-1], inc):
                output.append(stack.pop())
            stack.append(token)

        while stack:
            top = stack.pop()
            if top == "(":
                raise ValueError("Несбалансированные скобки")
            output.append(top)

        self._assert_rpn_single_value(output)
        return " ".join(output)

    def to_rpn(self) -> str:
        """Публичный API (проверка выполняется внутри _build_rpn_output)."""
        return self._build_rpn_output()


def main() -> None:
    while True:
        expr = input("\nВыражение (exit для выхода): ").strip()
        if expr.lower() == "exit":
            break
        if not expr:
            continue
        try:
            conv = InfixToRpn(expr)
            print(f"RPN: {conv.to_rpn()}")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    from pathlib import Path

    _here = Path(__file__).resolve()
    print(f"Запущен скрипт: {_here}")
    if " " in _here.name and "(" in _here.name:
        print(
            "(Подсказка: из-за скобок в имени файла удобнее скопировать программу "
            "в файл с простым именем, например infix_to_rpn.py, и запускать его.)"
        )
    main()
