"""Конвертер инфикс → RPN с табличной валидацией."""

# Словарь токенов: имя -> (тип, арность, приоритет, ассоциативность)
dict = {
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

# ТАБЛИЦА ПРАВИЛ: (предыдущий_тип, текущий_тип) -> разрешено/ошибка
# Пустая строка в ошибке означает стандартное сообщение
RULES = {
    # начало выражения (prev=None)
    (None, "OP"): True,
    (None, "PR"): True,
    (None, "LP"): True,
    (None, "BI"): "Нельзя начинать с бинарного оператора",
    (None, "PS"): "Нельзя начинать с постфиксного оператора",
    (None, "RP"): "Нельзя начинать с закрывающей скобки",
    
    # операнд после чего-то
    ("OP", "OP"): "Два операнда подряд",
    ("OP", "PR"): "Нужен оператор между операндом и функцией",
    ("OP", "LP"): "Нужен оператор между операндом и скобкой",
    ("OP", "BI"): True,
    ("OP", "PS"): True,
    ("OP", "RP"): True,
    
    # бинарный оператор после чего-то
    ("BI", "OP"): True,
    ("BI", "PR"): True,
    ("BI", "LP"): True,
    ("BI", "BI"): "Два бинарных оператора подряд",
    ("BI", "PS"): "После бинарного не может быть постфикса",
    ("BI", "RP"): "После бинарного не может быть закрывающей скобки",
    
    # префиксный оператор после чего-то
    ("PR", "OP"): True,
    ("PR", "PR"): True,
    ("PR", "LP"): True,
    ("PR", "BI"): "После префиксного оператора нужно выражение",
    ("PR", "PS"): "После префиксного оператора нужно выражение",
    ("PR", "RP"): "После префиксного оператора нужно выражение",
    
    # постфиксный оператор после чего-то
    ("PS", "OP"): "После постфикса не может быть операнда",
    ("PS", "PR"): "После постфикса не может быть функции",
    ("PS", "LP"): "После постфикса не может быть скобки",
    ("PS", "BI"): True,
    ("PS", "PS"): "Два постфиксных оператора подряд",
    ("PS", "RP"): True,
    
    # левая скобка после чего-то
    ("LP", "OP"): True,
    ("LP", "PR"): True,
    ("LP", "LP"): True,
    ("LP", "BI"): "После скобки не может быть бинарного оператора",
    ("LP", "PS"): "После скобки не может быть постфикса",
    ("LP", "RP"): "Пустые скобки",
    
    # правая скобка после чего-то
    ("RP", "OP"): "Нужен оператор между скобкой и операндом",
    ("RP", "PR"): "Нужен оператор между скобкой и функцией",
    ("RP", "LP"): "Нужен оператор между скобками",
    ("RP", "BI"): True,
    ("RP", "PS"): True,
    ("RP", "RP"): True,
}

def get_type(token):
    """Возвращает тип токена."""
    return dict[token][0] if token in dict else "OP"

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
        
        if i + 1 < n and expr[i:i+2] in dict:
            raw.append(expr[i:i+2])
            i += 2
            continue
        
        if ch in dict:
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
    
    # 2. Проверка через таблицу правил
    if not raw:
        raise ValueError("Пустое выражение")
    
    balance = 0
    prev_type = None
    
    for i, token in enumerate(raw):
        curr_type = get_type(token)
        
        # Баланс скобок
        if token == '(':
            balance += 1
        elif token == ')':
            balance -= 1
            if balance < 0:
                raise ValueError("Лишняя закрывающая скобка")
        
        # Проверка по таблице правил
        rule_key = (prev_type, curr_type)
        if rule_key in RULES:
            result = RULES[rule_key]
            if result is not True:
                if isinstance(result, str):
                    raise ValueError(result)
                else:
                    raise ValueError(f"Некорректная последовательность: '{raw[i-1]}' → '{token}'")
        
        prev_type = curr_type
    
    # Проверка последнего токена
    last_type = get_type(raw[-1])
    if last_type == "BI":
        raise ValueError(f"Нельзя заканчивать бинарным оператором '{raw[-1]}'")
    if last_type == "PR":
        raise ValueError(f"После префиксного оператора '{raw[-1]}' нужно выражение")
    
    # Финальная проверка баланса скобок
    if balance != 0:
        raise ValueError("Несбалансированные скобки")
    
    return raw

def to_rpn(tokens):
    """Алгоритм сортировочной станции."""
    output = []
    stack = []
    
    def get_type(t): return dict[t][0] if t in dict else "OP"
    def get_prec(t): return dict[t][2] if t in dict else 0
    def get_assoc(t): return dict[t][3] if t in dict and len(dict[t]) > 3 else None
    
    for token in tokens:
        token_type = get_type(token)
        
        # Операнд
        if token_type == "OP":
            output.append(token)
            while stack and get_type(stack[-1]) == "PR":
                output.append(stack.pop())
        
        # Постфиксный оператор
        elif token_type == "PS":
            output.append(token)
        
        # Префиксный оператор
        elif token_type == "PR":
            stack.append(token)
        
        # Левая скобка
        elif token == "(":
            stack.append(token)
        
        # Правая скобка
        elif token == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            if not stack:
                raise ValueError("Непарная скобка")
            stack.pop()
            while stack and get_type(stack[-1]) == "PR":
                output.append(stack.pop())
        
        # Бинарный оператор
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
    
    # Выталкиваем оставшиеся операторы
    while stack:
        if stack[-1] == "(":
            raise ValueError("Несбалансированные скобки")
        output.append(stack.pop())
    
    # Проверка результата
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
    return to_rpn(tokenize(expr))

def interactive():
    """Интерактивный режим."""
    print("\n=== Инфикс → RPN ===")
    print("Команды: exit - выход")
    print("Поддержка: + - * / ^ ( ) ! ++ -- sin cos tg ctg")
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
