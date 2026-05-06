# Словарь операторов с дополнительной информацией
OPERATORS_DICT = {
    "+": {"arity": 2, "prec": 2, "ass": "L", "type": "binary"},
    "-": {"arity": 2, "prec": 2, "ass": "L", "type": "binary"},
    "*": {"arity": 2, "prec": 3, "ass": "L", "type": "binary"},
    "/": {"arity": 2, "prec": 3, "ass": "L", "type": "binary"},
    "^": {"arity": 2, "prec": 4, "ass": "R", "type": "binary"},
    "~": {"arity": 1, "prec": 5, "ass": "R", "type": "prefix"},
    "!": {"arity": 1, "prec": 6, "ass": None, "type": "postfix"},
    "++": {"arity": 1, "prec": 6, "ass": None, "type": "postfix"},
    "--": {"arity": 1, "prec": 6, "ass": None, "type": "postfix"},
    "sin": {"arity": 1, "prec": 8, "ass": None, "type": "prefix"},
    "cos": {"arity": 1, "prec": 8, "ass": None, "type": "prefix"},
    "tg": {"arity": 1, "prec": 8, "ass": None, "type": "prefix"},
    "ctg": {"arity": 1, "prec": 8, "ass": None, "type": "prefix"},
    "(": {"arity": 0, "prec": 10, "ass": None, "type": "paren_left"},
    ")": {"arity": 0, "prec": 10, "ass": None, "type": "paren_right"},
}

class Op:
    reg = {}

    def __init__(self, name, arity, prec, ass=None, op_type=None):
        self.name = name
        self.arity = arity
        self.prec = prec
        self.ass = ass
        self.type = op_type
        Op.reg[name] = self

    @classmethod
    def reg_all(cls):
        cls.reg.clear()
        for name, info in OPERATORS_DICT.items():
            cls(name, info["arity"], info["prec"], info.get("ass"), info["type"])

    @classmethod
    def get(cls, name):
        return cls.reg.get(name)

    @classmethod
    def is_binary(cls, t):
        op = cls.get(t)
        return op is not None and op.type == "binary"

    @classmethod
    def is_prefix(cls, t):
        op = cls.get(t)
        return op is not None and op.type == "prefix"

    @classmethod
    def is_postfix(cls, t):
        op = cls.get(t)
        return op is not None and op.type == "postfix"

    @classmethod
    def is_operand(cls, t):
        return t not in "()" and cls.get(t) is None

def tokenize(expr):
    tokens, i, n = [], 0, len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        
        # Проверяем двухсимвольные операторы
        if i + 1 < n:
            two_chars = expr[i:i+2]
            if Op.is_postfix(two_chars):
                tokens.append(two_chars)
                i += 2
                continue
        
        if c.isalnum():
            j = i + 1
            while j < n and (expr[j].isalnum()):
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue
        
        if c in OPERATORS_DICT:
            tokens.append(c)
            i += 1
            continue
        
        raise ValueError(f"Неизвестный символ: {c!r}")
    return tokens

class InfixToRpn:
    def __init__(self, expr):
        Op.reg_all()
        self.source = expr
        raw = tokenize(expr)
        self.tokens = self._process_operators(raw)

    def _process_operators(self, tokens):
        """Обрабатывает последовательности операторов"""
        result = []
        i = 0
        n = len(tokens)
        
        while i < n:
            tok = tokens[i]
            
            # Если это не оператор или не последовательность плюсов
            if tok != '+':
                result.append(tok)
                i += 1
                continue
            
            # Собираем последовательность плюсов
            plus_count = 1
            j = i + 1
            while j < n and tokens[j] == '+':
                plus_count += 1
                j += 1
            
            # Проверяем, что после плюсов нет постфиксных операторов вплотную
            if j < n and (Op.is_postfix(tokens[j])):
                # Проверяем, что перед последовательностью плюсов есть операнд
                if i > 0 and (Op.is_operand(result[-1]) or result[-1] == ')'):
                    # Это бинарный оператор + и постфиксные операторы относятся к операнду слева
                    # Добавляем один бинарный плюс
                    result.append('+')
                    i = j  # Пропускаем все плюсы
                    continue
                else:
                    raise ValueError(f"Некорректная последовательность операторов: {'+' * plus_count}")
            
            # Анализируем последовательность плюсов
            # Определяем контекст
            prev = result[-1] if result else None
            
            if prev is None or prev == '(' or Op.is_binary(prev) or Op.is_prefix(prev):
                # Начало выражения или после оператора - это могут быть унарные плюсы
                # Унарные плюсы игнорируем (просто пропускаем)
                if plus_count == 1:
                    # Одиночный унарный плюс - просто игнорируем
                    pass
                elif plus_count == 2:
                    # Два унарных плюса - тоже игнорируем
                    pass
                else:
                    raise ValueError(f"Некорректная последовательность унарных плюсов: {'+' * plus_count}")
            else:
                # После операнда или скобки - это бинарный оператор
                if plus_count == 1:
                    result.append('+')
                elif plus_count == 2:
                    # Два плюса: первый бинарный, второй унарный? Некорректно
                    raise ValueError(f"Некорректная последовательность: {'+' * plus_count}")
                else:
                    raise ValueError(f"Некорректная последовательность: {'+' * plus_count}")
            
            i = j
        
        return result

    def _fold_unary(self, tokens):
        """Заменяет унарный минус на '~'"""
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

    def _validate(self):
        ts = self.tokens
        if not ts:
            raise ValueError("Пустое выражение")
        
        if Op.is_binary(ts[0]):
            raise ValueError(f"Нельзя начинать с бинарного оператора «{ts[0]}»")
        if Op.is_postfix(ts[0]):
            raise ValueError("Постфиксный оператор не может быть в начале")
        
        if Op.is_binary(ts[-1]):
            raise ValueError(f"Нельзя заканчивать бинарным оператором «{ts[-1]}»")
        
        balance = 0
        for i, curr in enumerate(ts):
            if curr == '(':
                balance += 1
            elif curr == ')':
                balance -= 1
                if balance < 0:
                    raise ValueError("Лишняя закрывающая скобка ')'")
            
            if i == 0:
                continue
            
            prev = ts[i-1]
            
            if Op.is_operand(prev) and (Op.is_operand(curr) or curr == '('):
                raise ValueError(f"Нужен оператор между «{prev}» и «{curr}»")
            
            if prev == ')' and (curr == '(' or Op.is_operand(curr)):
                raise ValueError(f"Нужен оператор между «{prev}» и «{curr}»")
            
            if Op.is_postfix(prev) and Op.is_binary(curr):
                raise ValueError(f"Некорректная запись: постфиксный оператор «{prev}» перед бинарным «{curr}»")
            
            if Op.is_binary(prev) and Op.is_binary(curr):
                raise ValueError(f"Два бинарных оператора подряд: «{prev}» и «{curr}»")
            
            if Op.is_postfix(curr) and not (Op.is_operand(prev) or prev == ')'):
                raise ValueError(f"Некорректная запись: постфиксный оператор «{curr}» применён не к операнду")
        
        if balance != 0:
            raise ValueError("Несбалансированные скобки")

    def to_rpn(self):
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
            
            if Op.is_postfix(tok):
                output.append(tok)
                continue
            
            if tok == '(':
                stack.append(tok)
                continue
            
            if tok == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
                while stack and Op.is_prefix(stack[-1]):
                    output.append(stack.pop())
                continue
            
            inc = Op.get(tok)
            if not inc:
                raise ValueError(f"Неизвестный токен: {tok!r}")
            
            while (stack and stack[-1] != '(' and 
                   not Op.is_prefix(stack[-1]) and 
                   not Op.is_postfix(stack[-1])):
                top = Op.get(stack[-1])
                if top and (top.prec > inc.prec or 
                           (top.prec == inc.prec and (inc.ass or 'L') == 'L')):
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
            elif Op.is_postfix(t) or Op.is_prefix(t):
                if depth < 1:
                    raise ValueError(f"Не хватает операнда для «{t}»")
            elif Op.is_binary(t):
                if depth < 2:
                    raise ValueError(f"Не хватает операндов для бинарного оператора «{t}»")
                depth -= 1
        
        if depth != 1:
            raise ValueError("Выражение не сводится к одному значению")
        
        return ' '.join(output)

def interactive():
    print("\n=== Инфикс → RPN === Введите 'exit' для выхода ===\n")
    print("Примеры правильных выражений:")
    print("  11 ++ ++ + 1  -> 11 ++ ++ 1 +")
    print("  11 ++ + 1     -> 11 ++ 1 +")
    print("\nПримеры неправильных:")
    print("  11 +++ 1      -> Ошибка")
    print("  11 ++ + ++ 1  -> Ошибка")
    print()
    
    while True:
        expr = input("> ").strip()
        if expr.lower() == 'exit':
            break
        if not expr:
            continue
        try:
            rpn = InfixToRpn(expr).to_rpn()
            print(f"RPN: {rpn}")
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    interactive()
