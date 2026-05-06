DICT = {
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
    "(": {"arity": 0, "prec": 10, "ass": None, "type": "paren_left"},
    ")": {"arity": 0, "prec": 10, "ass": None, "type": "paren_right"},
}


class Op:
    @classmethod
    def get(cls, name):
        return DICT.get(name)

    @classmethod
    def is_type(cls, name, typ):
        op = cls.get(name)
        return op and op["type"] == typ

    @classmethod
    def is_operand(cls, name):
        return name not in DICT and name not in "()"


def tokenize(expr):
    """Токенизация полностью на основе DICT"""
    tokens, i, n = [], 0, len(expr)
    max_len = max(len(k) for k in DICT if isinstance(k, str))
    
    while i < n:
        if expr[i].isspace():
            i += 1
            continue
        
        # Поиск самого длинного совпадения из DICT
        matched = None
        for length in range(min(max_len, n - i), 0, -1):
            candidate = expr[i:i+length]
            if candidate in DICT:
                matched = candidate
                break
        
        if matched:
            tokens.append(matched)
            i += len(matched)
            continue
        
        # Числа или переменные (всё остальное)
        if expr[i].isalnum():
            j = i
            while j < n and expr[j].isalnum():
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue
        
        raise ValueError(f"Неизвестный символ: {expr[i]!r}")
    
    return tokens


class InfixToRpn:
    def __init__(self, expr):
        self.tokens = tokenize(expr)
        self._process_unary()
    
    def _process_unary(self):
        """Преобразование унарных + и - в ~"""
        result = []
        for i, t in enumerate(self.tokens):
            if t not in ('+', '-'):
                result.append(t)
                continue
            
            prev = result[-1] if result else None
            is_unary = (prev is None or prev == '(' or 
                       DICT.get(prev, {}).get("type") in ("binary", "prefix"))
            
            if is_unary and t == '-':
                result.append('~')
            elif is_unary and t == '+':
                continue  # пропускаем унарный плюс
            else:
                result.append(t)
        
        self.tokens = result
    
    def to_rpn(self):
        output, stack = [], []
        
        for tok in self.tokens:
            if Op.is_operand(tok):
                output.append(tok)
            elif Op.is_type(tok, "prefix"):
                stack.append(tok)
            elif Op.is_type(tok, "postfix"):
                output.append(tok)
            elif tok == '(':
                stack.append(tok)
            elif tok == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack:
                    raise ValueError("Лишняя скобка")
                stack.pop()
            else:  # binary operator
                op = DICT[tok]
                while (stack and stack[-1] != '(' and 
                       not Op.is_type(stack[-1], "prefix")):
                    top = DICT.get(stack[-1])
                    if top and (top["prec"] > op["prec"] or 
                               (top["prec"] == op["prec"] and op["ass"] == "L")):
                        output.append(stack.pop())
                    else:
                        break
                stack.append(tok)
        
        while stack:
            if stack[-1] == '(':
                raise ValueError("Не хватает скобки")
            output.append(stack.pop())
        
        return ' '.join(output)


def interactive():
    print("\n=== Инфикс → RPN ===\n")
    while True:
        expr = input("> ").strip()
        if expr == 'exit':
            break
        if not expr:
            continue
        try:
            print(f"RPN: {InfixToRpn(expr).to_rpn()}")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    interactive()
