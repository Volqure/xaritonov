"""Конвертер инфикс → RPN с таблицей правил на основе токенов."""

# Словарь токенов: имя -> (тип, арность, приоритет, ассоциативность)
tokens_dict = {
    # скобки
    "(": ("LP", 0, 100, None),
    ")": ("RP", 0, 100, None),
    # постфиксные операторы
    "!": ("PS", 1, 6, None),
    "++": ("PS", 1, 6, None),
    "--": ("PS", 1, 6, None),
    # префиксные операторы
    "sin": ("PR", 1, 8, None),
    "cos": ("PR", 1, 8, None),
    "tg": ("PR", 1, 8, None),
    "ctg": ("PR", 1, 8, None),
    # бинарные операторы
    "+": ("BI", 2, 2, "L"),
    "-": ("BI", 2, 2, "L"),
    "*": ("BI", 2, 3, "L"),
    "/": ("BI", 2, 3, "L"),
    "^": ("BI", 2, 4, "R"),
}

# ТАБЛИЦА ПРАВИЛ: (предыдущий_токен, текущий_токен) -> (разрешено, сообщение)
# Используем специальные маркеры: None для начала, "END" для конца
RULES = {
    # НАЧАЛО ВЫРАЖЕНИЯ (None → токен)
    (None, "("): (True, ""),
    (None, "sin"): (True, ""),
    (None, "cos"): (True, ""),
    (None, "tg"): (True, ""),
    (None, "ctg"): (True, ""),
    (None, "+"): (False, "Нельзя начинать с бинарного оператора '+'"),
    (None, "-"): (False, "Нельзя начинать с бинарного оператора '-'"),
    (None, "*"): (False, "Нельзя начинать с бинарного оператора '*'"),
    (None, "/"): (False, "Нельзя начинать с бинарного оператора '/'"),
    (None, "^"): (False, "Нельзя начинать с бинарного оператора '^'"),
    (None, "!"): (False, "Нельзя начинать с постфиксного оператора '!'"),
    (None, "++"): (False, "Нельзя начинать с постфиксного оператора '++'"),
    (None, "--"): (False, "Нельзя начинать с постфиксного оператора '--'"),
    (None, ")"): (False, "Нельзя начинать с закрывающей скобки ')'"),
    
    # КОНЕЦ ВЫРАЖЕНИЯ (токен → "END")
    ("+", "END"): (False, "Нельзя заканчивать бинарным оператором '+'"),
    ("-", "END"): (False, "Нельзя заканчивать бинарным оператором '-'"),
    ("*", "END"): (False, "Нельзя заканчивать бинарным оператором '*'"),
    ("/", "END"): (False, "Нельзя заканчивать бинарным оператором '/'"),
    ("^", "END"): (False, "Нельзя заканчивать бинарным оператором '^'"),
    ("sin", "END"): (False, "После 'sin' нужно выражение"),
    ("cos", "END"): (False, "После 'cos' нужно выражение"),
    ("tg", "END"): (False, "После 'tg' нужно выражение"),
    ("ctg", "END"): (False, "После 'ctg' нужно выражение"),
    ("(", "END"): (False, "Незакрытая скобка '('"),
    ("END", "END"): (True, ""),  # для всех остальных токенов
    
    # ОПЕРАНДЫ (числа/переменные)
    # Два операнда подряд
    ("2", "3"): (False, "Два операнда подряд"),
    ("2", "x"): (False, "Два операнда подряд"),
    ("x", "2"): (False, "Два операнда подряд"),
    ("x", "y"): (False, "Два операнда подряд"),
    
    # Операнд и скобка
    ("2", "("): (False, "Нужен оператор между '2' и '('"),
    ("x", "("): (False, "Нужен оператор между 'x' и '('"),
    
    # Операнд и функция
    ("2", "sin"): (False, "Нужен оператор между '2' и 'sin'"),
    ("2", "cos"): (False, "Нужен оператор между '2' и 'cos'"),
    ("x", "sin"): (False, "Нужен оператор между 'x' и 'sin'"),
    
    # Операнд и бинарный оператор
    ("2", "+"): (True, ""),
    ("2", "-"): (True, ""),
    ("2", "*"): (True, ""),
    ("2", "/"): (True, ""),
    ("2", "^"): (True, ""),
    ("x", "+"): (True, ""),
    
    # Операнд и постфикс
    ("2", "!"): (True, ""),
    ("2", "++"): (True, ""),
    ("2", "--"): (True, ""),
    ("x", "!"): (True, ""),
    
    # Операнд и скобка
    ("2", ")"): (True, ""),
    ("x", ")"): (True, ""),
    
    # БИНАРНЫЕ ОПЕРАТОРЫ
    # Бинарный и операнд
    ("+", "2"): (True, ""),
    ("+", "x"): (True, ""),
    ("-", "2"): (True, ""),
    ("*", "2"): (True, ""),
    ("/", "2"): (True, ""),
    ("^", "2"): (True, ""),
    
    # Бинарный и функция
    ("+", "sin"): (True, ""),
    ("+", "cos"): (True, ""),
    ("*", "sin"): (True, ""),
    
    # Бинарный и скобка
    ("+", "("): (True, ""),
    ("*", "("): (True, ""),
    
    # Два бинарных подряд
    ("+", "+"): (False, "Два бинарных оператора подряд '+ +'"),
    ("+", "-"): (False, "Два бинарных оператора подряд '+ -'"),
    ("+", "*"): (False, "Два бинарных оператора подряд '+ *'"),
    ("-", "+"): (False, "Два бинарных оператора подряд '- +'"),
    ("*", "+"): (False, "Два бинарных оператора подряд '* +'"),
    ("/", "*"): (False, "Два бинарных оператора подряд '/ *'"),
    
    # Бинарный и постфикс
    ("+", "!"): (False, "После бинарного оператора '+' не может быть постфикса '!'"),
    ("+", "++"): (False, "После бинарного оператора '+' не может быть постфикса '++'"),
    ("*", "!"): (False, "После бинарного оператора '*' не может быть постфикса '!'"),
    
    # Бинарный и скобка
    ("+", ")"): (False, "После бинарного оператора '+' не может быть ')'"),
    ("*", ")"): (False, "После бинарного оператора '*' не может быть ')'"),
    
    # ПРЕФИКСНЫЕ ОПЕРАТОРЫ
    # Префикс и операнд
    ("sin", "2"): (True, ""),
    ("sin", "x"): (True, ""),
    ("cos", "2"): (True, ""),
    
    # Префикс и префикс
    ("sin", "sin"): (True, ""),
    ("sin", "cos"): (True, ""),
    
    # Префикс и скобка
    ("sin", "("): (True, ""),
    ("cos", "("): (True, ""),
    
    # Префикс и бинарный
    ("sin", "+"): (False, "После 'sin' нужно выражение, а не '+'"),
    ("sin", "-"): (False, "После 'sin' нужно выражение, а не '-'"),
    ("cos", "*"): (False, "После 'cos' нужно выражение, а не '*'"),
    
    # Префикс и постфикс
    ("sin", "!"): (False, "После 'sin' нужно выражение, а не '!'"),
    ("sin", "++"): (False, "После 'sin' нужно выражение, а не '++'"),
    
    # Префикс и скобка
    ("sin", ")"): (False, "После 'sin' нужно выражение, а не ')'"),
    ("cos", ")"): (False, "После 'cos' нужно выражение, а не ')'"),
    
    # ПОСТФИКСНЫЕ ОПЕРАТОРЫ
    # Постфикс и бинарный
    ("!", "+"): (True, ""),
    ("!", "-"): (True, ""),
    ("++", "+"): (True, ""),
    ("--", "*"): (True, ""),
    
    # Постфикс и скобка
    ("!", ")"): (True, ""),
    ("++", ")"): (True, ""),
    
    # Постфикс и операнд
    ("!", "2"): (False, "После '!' не может быть операнда '2'"),
    ("!", "x"): (False, "После '!' не может быть операнда 'x'"),
    ("++", "2"): (False, "После '++' не может быть операнда '2'"),
    
    # Постфикс и функция
    ("!", "sin"): (False, "После '!' не может быть функции 'sin'"),
    ("++", "cos"): (False, "После '++' не может быть функции 'cos'"),
    
    # Постфикс и скобка
    ("!", "("): (False, "После '!' не может быть скобки '('"),
    ("++", "("): (False, "После '++' не может быть скобки '('"),
    
    # Два постфиксных подряд
    ("!", "!"): (False, "Два постфиксных оператора подряд '! !'"),
    ("!", "++"): (False, "Два постфиксных оператора подряд '! ++'"),
    ("++", "!"): (False, "Два постфиксных оператора подряд '++ !'"),
    
    # СКОБКИ
    # Левая скобка и операнд
    ("(", "2"): (True, ""),
    ("(", "x"): (True, ""),
    
    # Левая скобка и префикс
    ("(", "sin"): (True, ""),
    ("(", "cos"): (True, ""),
    
    # Левая скобка и скобка
    ("(", "("): (True, ""),
    
    # Левая скобка и бинарный
    ("(", "+"): (False, "После '(' не может быть бинарного оператора '+'"),
    ("(", "*"): (False, "После '(' не может быть бинарного оператора '*'"),
    
    # Левая скобка и постфикс
    ("(", "!"): (False, "После '(' не может быть постфикса '!'"),
    ("(", "++"): (False, "После '(' не может быть постфикса '++'"),
    
    # Левая скобка и правая скобка
    ("(", ")"): (False, "Пустые скобки '()'"),
    
    # Правая скобка и бинарный
    (")", "+"): (True, ""),
    (")", "*"): (True, ""),
    
    # Правая скобка и постфикс
    (")", "!"): (True, ""),
    (")", "++"): (True, ""),
    
    # Правая скобка и скобка
    (")", ")"): (True, ""),
    
    # Правая скобка и операнд
    (")", "2"): (False, "Нужен оператор между ')' и '2'"),
    (")", "x"): (False, "Нужен оператор между ')' и 'x'"),
    
    # Правая скобка и функция
    (")", "sin"): (False, "Нужен оператор между ')' и 'sin'"),
    (")", "cos"): (False, "Нужен оператор между ')' и 'cos'"),
    
    # Правая скобка и левая скобка
    (")", "("): (False, "Нужен оператор между ')' и '('"),
}

def is_operand(token):
    """Проверка, является ли токен операндом (числом или переменной)."""
    return token not in tokens_dict

def tokenize(expr):
    """Токенизация с валидацией через таблицу правил."""
    # 1. Разбиение на сырые токены
    raw = []
    i, n = 0, len(expr)
    
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        
        if i + 1 < n and expr[i:i+2] in tokens_dict:
            raw.append(expr[i:i+2])
            i += 2
            continue
        
        if ch in tokens_dict:
            raw.append(ch)
            i += 1
            continue
        
        if ch.isalnum() or ch == '.':
            j = i + 1
            while j < n and (expr[j].isalnum() or expr[j] == '.'):
                j += 1
            raw.append(expr[i:j])
            i = j
            continue
        
        raise ValueError(f"Неизвестный символ: '{ch}'")
    
    # 2. Валидация через таблицу правил
    if not raw:
        raise ValueError("Пустое выражение")
    
    # Заменяем операнды на маркер "OPERAND" для проверки
    normalized = []
    for token in raw:
        if is_operand(token):
            normalized.append("OPERAND")
        else:
            normalized.append(token)
    
    # Добавляем маркеры начала и конца
    sequence = [None] + normalized + ["END"]
    balance = 0
    
    for i in range(len(sequence) - 1):
        prev = sequence[i]
        curr = sequence[i + 1]
        
        # Отслеживаем баланс скобок
        if curr == "(":
            balance += 1
        elif curr == ")":
            balance -= 1
            if balance < 0:
                raise ValueError("Лишняя закрывающая скобка ')'")
        
        # Ищем правило в таблице
        if prev is None:
            key = (None, curr)
        elif curr == "END":
            key = (prev, "END")
        else:
            key = (prev, curr)
        
        # Для операндов используем общее правило
        if prev == "OPERAND" and curr == "OPERAND":
            key = ("OPERAND", "OPERAND")
        elif prev == "OPERAND" and curr != "OPERAND":
            key = ("OPERAND", curr)
        elif prev != "OPERAND" and curr == "OPERAND":
            key = (prev, "OPERAND")
        
        if key in RULES:
            allowed, msg = RULES[key]
            if not allowed:
                # Восстанавливаем оригинальные токены для сообщения
                if prev == "OPERAND" and curr == "OPERAND":
                    prev_token = raw[i-1] if i > 0 else "операнд"
                    curr_token = raw[i] if i < len(raw) else "операнд"
                    raise ValueError(f"Два операнда подряд: '{prev_token}' и '{curr_token}'")
                elif prev == "OPERAND":
                    prev_token = raw[i-1] if i > 0 else "операнд"
                    raise ValueError(msg.replace("операнд", prev_token) if "операнд" in msg else msg)
                elif curr == "OPERAND":
                    curr_token = raw[i] if i < len(raw) else "операнд"
                    raise ValueError(msg.replace("операнд", curr_token) if "операнд" in msg else msg)
                else:
                    raise ValueError(msg)
    
    if balance != 0:
        raise ValueError("Несбалансированные скобки")
    
    return raw

def to_rpn(tokens):
    """Алгоритм сортировочной станции."""
    output = []
    stack = []
    
    def get_type(t): return tokens_dict[t][0] if t in tokens_dict else "OP"
    def get_prec(t): return tokens_dict[t][2] if t in tokens_dict else 0
    def get_assoc(t): return tokens_dict[t][3] if t in tokens_dict and len(tokens_dict[t]) > 3 else None
    
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
    """Основная функция конвертации."""
    tokens = tokenize(expr)
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
