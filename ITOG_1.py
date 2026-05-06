"""Конвертер инфикс → RPN с единственной таблицей правил."""

# Словарь токенов: имя -> (тип, арность, приоритет, ассоциативность)
dict = {
    "(": ("LP", 0, 100, None),
    ")": ("RP", 0, 100, None),
    "!": ("PS", 1, 6, None),
    "++": ("PS", 1, 6, None),
    "--": ("PS", 1, 6, None),
    "sin": ("PR", 1, 8, None),
    "cos": ("PR", 1, 8, None),
    "tg": ("PR", 1, 8, None),
    "ctg": ("PR", 1, 8, None),
    "+": ("BI", 2, 2, "L"),
    "-": ("BI", 2, 2, "L"),
    "*": ("BI", 2, 3, "L"),
    "/": ("BI", 2, 3, "L"),
    "^": ("BI", 2, 4, "R"),
}

# ЕДИНСТВЕННАЯ ТАБЛИЦА ПРАВИЛ: (предыдущий_тип, текущий_тип, баланс_скобок, позиция) -> (разрешено, сообщение)
# Используем специальные маркеры: "START" для начала, "END" для конца, "BALANCE" для проверки скобок
RULES = {
    # Начало выражения
    ("START", "OP"): (True, ""),
    ("START", "PR"): (True, ""),
    ("START", "LP"): (True, ""),
    ("START", "BI"): (False, "Нельзя начинать с бинарного оператора"),
    ("START", "PS"): (False, "Нельзя начинать с постфиксного оператора"),
    ("START", "RP"): (False, "Нельзя начинать с закрывающей скобки"),
    
    # Конец выражения
    ("OP", "END"): (True, ""),
    ("PR", "END"): (False, "После префиксного оператора нужно выражение"),
    ("LP", "END"): (False, "Незакрытая скобка"),
    ("RP", "END"): (True, ""),
    ("BI", "END"): (False, "Нельзя заканчивать бинарным оператором"),
    ("PS", "END"): (True, ""),
    
    # Операнд
    ("OP", "OP"): (False, "Два операнда подряд"),
    ("OP", "PR"): (False, "Нужен оператор между операндом и функцией"),
    ("OP", "LP"): (False, "Нужен оператор между операндом и скобкой"),
    ("OP", "BI"): (True, ""),
    ("OP", "PS"): (True, ""),
    ("OP", "RP"): (True, ""),
    
    # Бинарный оператор
    ("BI", "OP"): (True, ""),
    ("BI", "PR"): (True, ""),
    ("BI", "LP"): (True, ""),
    ("BI", "BI"): (False, "Два бинарных оператора подряд"),
    ("BI", "PS"): (False, "После бинарного не может быть постфикса"),
    ("BI", "RP"): (False, "После бинарного не может быть закрывающей скобки"),
    
    # Префиксный оператор
    ("PR", "OP"): (True, ""),
    ("PR", "PR"): (True, ""),
    ("PR", "LP"): (True, ""),
    ("PR", "BI"): (False, "После префикса нужно выражение"),
    ("PR", "PS"): (False, "После префикса нужно выражение"),
    ("PR", "RP"): (False, "После префикса нужно выражение"),
    
    # Постфиксный оператор
    ("PS", "OP"): (False, "После постфикса не может быть операнда"),
    ("PS", "PR"): (False, "После постфикса не может быть функции"),
    ("PS", "LP"): (False, "После постфикса не может быть скобки"),
    ("PS", "BI"): (True, ""),
    ("PS", "PS"): (False, "Два постфиксных подряд"),
    ("PS", "RP"): (True, ""),
    
    # Левая скобка
    ("LP", "OP"): (True, ""),
    ("LP", "PR"): (True, ""),
    ("LP", "LP"): (True, ""),
    ("LP", "BI"): (False, "После ( не может быть бинарного"),
    ("LP", "PS"): (False, "После ( не может быть постфикса"),
    ("LP", "RP"): (False, "Пустые скобки"),
    
    # Правая скобка
    ("RP", "OP"): (False, "Нужен оператор между ) и операндом"),
    ("RP", "PR"): (False, "Нужен оператор между ) и функцией"),
    ("RP", "LP"): (False, "Нужен оператор между ) и ("),
    ("RP", "BI"): (True, ""),
    ("RP", "PS"): (True, ""),
    ("RP", "RP"): (True, ""),
}

def validate(tokens):
    """Единый метод проверки через таблицу правил."""
    if not tokens:
        raise ValueError("Пустое выражение")
    
    def get_type(t):
        return dict[t][0] if t in dict else "OP"
    
    # Добавляем маркеры начала и конца
    types = ["START"] + [get_type(t) for t in tokens] + ["END"]
    balance = 0
    
    for i in range(len(types) - 1):
        prev_type = types[i]
        curr_type = types[i + 1]
        
        # Обработка скобок
        if i < len(tokens):
            token = tokens[i]
            if token == '(':
                balance += 1
            elif token == ')':
                balance -= 1
                if balance < 0:
                    raise ValueError("Лишняя закрывающая скобка")
        
        # Проверка по таблице
        key = (prev_type, curr_type)
        if key in RULES:
            allowed, msg = RULES[key]
            if not allowed:
                raise ValueError(msg)
    
    # Проверка баланса скобок через таблицу
    if balance != 0:
        raise ValueError("Несбалансированные скобки")

def tokenize(expr):
    """Разбиение на токены."""
    tokens = []
    i, n = 0, len(expr)
    
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        
        if i + 1 < n and expr[i:i+2] in dict:
            tokens.append(expr[i:i+2])
            i += 2
            continue
        
        if ch in dict:
            tokens.append(ch)
            i += 1
            continue
        
        if ch.isalnum() or ch == '.':
            j = i + 1
            while j < n and (expr[j].isalnum() or expr[j] == '.'):
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue
        
        raise ValueError(f"Неизвестный символ: '{ch}'")
    
    return tokens

def to_rpn(tokens):
    """Алгоритм сортировочной станции."""
    output = []
    stack = []
    
    def get_type(t): return dict[t][0] if t in dict else "OP"
    def get_prec(t): return dict[t][2] if t in dict else 0
    def get_assoc(t): return dict[t][3] if t in dict and len(dict[t]) > 3 else None
    
    for token in tokens:
        token_type = get_type(token)
        
        if token_type == "OP":
            output.append(token)
            while stack and get_type(stack[-1]) == "PR":
                output.append(stack.pop())
        
        elif token_type == "PS":
            output.append(token)
        
        elif token_type == "PR":
            stack.append(token)
        
        elif token == "(":
            stack.append(token)
        
        elif token == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            if not stack:
                raise ValueError("Непарная скобка")
            stack.pop()
            while stack and get_type(stack[-1]) == "PR":
                output.append(stack.pop())
        
        elif token_type == "BI":
            curr_prec = get_prec(token)
            curr_assoc = get_assoc(token)
            while (stack and stack[-1] != "(" and get_type(stack[-1]) != "PR"):
                top_prec = get_prec(stack[-1])
                if top_prec > curr_prec or (top_prec == curr_prec and curr_assoc == "L"):
                    output.append(stack.pop())
                else:
                    break
            stack.append(token)
    
    while stack:
        if stack[-1] == "(":
            raise ValueError("Несбалансированные скобки")
        output.append(stack.pop())
    
    # Финальная проверка результата
    depth = 0
    for token in output:
        token_type = get_type(token)
        if token_type == "OP":
            depth += 1
        elif token_type in ("PR", "PS"):
            if depth < 1:
                raise ValueError(f"Не хватает операнда для '{token}'")
        elif token_type == "BI":
            if depth < 2:
                raise ValueError(f"Не хватает операндов для '{token}'")
            depth -= 1
    
    if depth != 1:
        raise ValueError("Выражение не сводится к одному значению")
    
    return ' '.join(output)

def convert(expr):
    """Основная функция."""
    tokens = tokenize(expr)
    validate(tokens)
    return to_rpn(tokens)

def interactive():
    """Интерактивный режим."""
    print("\n=== Инфикс → RPN ===")
    print("Команды: exit - выход")
    print("=" * 50)
    
    while True:
        expr = input("\n> ").strip()
        if expr.lower() == 'exit':
            break
        if not expr:
            continue
        try:
            print(f"RPN: {convert(expr)}")
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    interactive()
