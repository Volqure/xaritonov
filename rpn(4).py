def _action_operand(token, output, operators):
    output.append(token)

def _action_unary(token, output, operators):
    while operators and _is_unary(operators[-1]):
        output.append(operators.pop())
    operators.append(token)

def _action_binary(token, output, operators):
    while (operators and
           operators[-1] != '(' and
           (_is_unary(operators[-1]) or
            (_is_binary(operators[-1]) and
             get_priority(operators[-1]) >= get_priority(token)))):
        output.append(operators.pop())
    operators.append(token)

def _action_open(token, output, operators):
    operators.append(token)

def _action_close(token, output, operators):
    while operators and operators[-1] != '(':
        output.append(operators.pop())
    if not operators:
        raise ValueError("Несбалансированные скобки: лишняя ')'")
    operators.pop()
    if operators and _is_type(operators[-1], 'func'):
        output.append(operators.pop())

def _action_func(token, output, operators):
    operators.append(token)

def _action_postfix(token, output, operators):
    output.append(token)


TOKEN_REGISTRY = {
    '+':   {'type': 'binary',  'priority': 1, 'rpn_action': _action_binary,  'drain_ok': True},
    '-':   {'type': 'binary',  'priority': 1, 'rpn_action': _action_binary,  'drain_ok': True},
    '*':   {'type': 'binary',  'priority': 2, 'rpn_action': _action_binary,  'drain_ok': True},
    '/':   {'type': 'binary',  'priority': 2, 'rpn_action': _action_binary,  'drain_ok': True},
    '^':   {'type': 'binary',  'priority': 3, 'rpn_action': _action_binary,  'drain_ok': True},
    'u-':  {'type': 'unary',   'priority': 4, 'symbol': '~', 'reserved': True,
            'rpn_action': _action_unary,  'drain_ok': True},
    '(':   {'type': 'bracket', 'rpn_action': _action_open,   'drain_ok': False},
    ')':   {'type': 'bracket', 'rpn_action': _action_close,  'drain_ok': True},
    '!':   {'type': 'postfix', 'priority': 5, 'rpn_action': _action_postfix, 'drain_ok': True},
    'sin': {'type': 'func',    'priority': 5, 'rpn_action': _action_func,    'drain_ok': True},
    'cos': {'type': 'func',    'priority': 5, 'rpn_action': _action_func,    'drain_ok': True},
    'tg':  {'type': 'func',    'priority': 5, 'rpn_action': _action_func,    'drain_ok': True},
    'ctg': {'type': 'func',    'priority': 5, 'rpn_action': _action_func,    'drain_ok': True},
    '++':  {'type': 'postfix', 'priority': 5, 'rpn_action': _action_postfix, 'drain_ok': True},
    '--':  {'type': 'postfix', 'priority': 5, 'rpn_action': _action_postfix, 'drain_ok': True},
    ' ':   {'type': 'skip'},
}

# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def get_priority(token):  return TOKEN_REGISTRY.get(token, {}).get('priority', 0)
def _is_type(token, t):   return TOKEN_REGISTRY.get(token, {}).get('type') == t
def _is_binary(token):    return _is_type(token, 'binary')
def _is_unary(token):     return _is_type(token, 'unary')
def is_operator(token):   return _is_binary(token) or _is_unary(token)
def is_reserved(word):    return TOKEN_REGISTRY.get(word, {}).get('reserved', False)
def token_symbol(token):  return TOKEN_REGISTRY.get(token, {}).get('symbol', str(token))
def _drain_ok(token):     return TOKEN_REGISTRY.get(token, {}).get('drain_ok', True)

def is_operand(token):
    return isinstance(token, (int, float)) or (
        isinstance(token, str) and token not in TOKEN_REGISTRY
    )

# ---------------------------------------------------------------------------
# Валидаторы
# ---------------------------------------------------------------------------

def _check_operand_sequence(tokens):
    if tokens and is_operand(tokens[-1]):
        raise ValueError("Два операнда подряд без оператора между ними")

def _check_reserved(var, _tokens):
    if is_reserved(var):
        raise ValueError(f"Имя '{var}' зарезервировано, используйте другое имя")

def _check_double_unary(tokens):
    if tokens and tokens[-1] == 'u-':
        raise ValueError("Недопустимый двойной унарный минус '--'")

def _check_binary_position(ch, tokens):
    if _is_binary(ch) and ch != '-' and (
        not tokens or tokens[-1] == '(' or is_operator(tokens[-1])
    ):
        raise ValueError(f"Оператор '{ch}' не может стоять в позиции операнда")

def _check_close_paren(ch, tokens):
    if ch == ')' and tokens and (is_operator(tokens[-1]) or tokens[-1] == '('):
        raise ValueError("Пустые скобки или отсутствует операнд перед ')'")

def _check_postfix_position(token, tokens):
    if not tokens or (not is_operand(tokens[-1]) and tokens[-1] != ')'):
        raise ValueError(f"Оператор '{token}' без операнда слева")
    if token in ('++', '--') and tokens:
        last = tokens[-1]
        if last == ')':
            raise ValueError(f"Оператор '{token}' применим только к переменным, не к выражениям")
        if isinstance(last, (int, float)) or (
                isinstance(last, str) and last.replace('.', '', 1).lstrip('-').isdigit()):
            raise ValueError(f"Оператор '{token}' применим только к переменным, не к числам")

# ---------------------------------------------------------------------------
# Ридеры
# ---------------------------------------------------------------------------

def _read_number(expression, i, tokens):
    _check_operand_sequence(tokens)
    num_start = i
    num, dot_count = '', 0
    while i < len(expression) and (expression[i].isdigit() or expression[i] == '.'):
        dot_count += (expression[i] == '.')
        if dot_count > 1:
            raise ValueError(f"Некорректный формат числа: '{expression[num_start:i+1]}'")
        num += expression[i]
        i += 1
    if num == '.':
        raise ValueError("Некорректный формат числа: '.'")
    if i < len(expression) and expression[i].isalpha():
        raise ValueError(f"Недопустимый символ '{expression[i]}' после числа")
    return (float if '.' in num else int)(num), i

def _read_variable(expression, i, tokens):
    word = ''
    while i < len(expression) and expression[i].isalpha():
        word += expression[i]
        i += 1
    if _is_type(word, 'func'):
        j = i
        while j < len(expression) and expression[j] == ' ':
            j += 1
        if j < len(expression) and expression[j] == '(':
            return word, i
        return '__func_prefix__:' + word, i
    _check_operand_sequence(tokens)
    _check_reserved(word, tokens)
    return word, i

def _read_unary_minus(expression, i, tokens):
    _check_double_unary(tokens)
    return 'u-', i + 1

def _read_registry_token(expression, i, tokens):
    two = expression[i:i+2]
    if len(two) == 2 and two in TOKEN_REGISTRY:
        if _is_type(two, 'postfix'):
            _check_postfix_position(two, tokens)
        return two, i + 2
    ch = expression[i]
    _check_binary_position(ch, tokens)
    _check_close_paren(ch, tokens)
    if _is_type(ch, 'postfix'):
        _check_postfix_position(ch, tokens)
    return ch, i + 1

_CHAR_DISPATCH = [
    (lambda ch, tok: ch.isdigit() or ch == '.',                     _read_number),
    (lambda ch, tok: ch.isalpha(),                                   _read_variable),
    (lambda ch, tok: ch == '-' and (
        not tok or tok[-1] == '(' or is_operator(tok[-1])),          _read_unary_minus),
    (lambda ch, tok: ch in TOKEN_REGISTRY or ch in ('+', '-'),       _read_registry_token),
]

# ---------------------------------------------------------------------------
# Токенизатор
# ---------------------------------------------------------------------------
# Функция без скобок (sin x) захватывает аргумент до конца выражения:
#   sin x+1   = sin(x+1)
#   sin sin x = sin(sin(x))
# Реализация: при встрече функции без '(' вставляем func+'(' в tokens,
# а ')' добавляем в конец (по одной на каждую такую функцию).

def tokenize(expression):
    tokens, i = [], 0
    pending_funcs = []  # функции без скобок, ждущие закрытия

    while i < len(expression):
        ch = expression[i]
        if TOKEN_REGISTRY.get(ch, {}).get('type') == 'skip':
            i += 1
            continue
        for predicate, reader in _CHAR_DISPATCH:
            if predicate(ch, tokens):
                token, i = reader(expression, i, tokens)
                if isinstance(token, str) and token.startswith('__func_prefix__:'):
                    func_name = token[len('__func_prefix__:'):]
                    # Неявное * если перед функцией стоит операнд или ')'
                    if not pending_funcs and tokens and (
                            is_operand(tokens[-1]) or tokens[-1] == ')'):
                        tokens.append('*')
                    tokens.append(func_name)
                    tokens.append('(')
                    pending_funcs.append(func_name)
                else:
                    # Неявное * если перед func(...) стоит операнд или ')'
                    if (_is_type(token, 'func') and tokens and (
                            is_operand(tokens[-1]) or tokens[-1] == ')')):
                        tokens.append('*')
                    tokens.append(token)
                break
        else:
            raise ValueError(f"Недопустимый символ: '{ch}'")

    if pending_funcs:
        if not tokens or is_operator(tokens[-1]) or tokens[-1] == '(':
            raise ValueError(f"После функции '{pending_funcs[-1]}' ожидается аргумент")
        for _ in pending_funcs:
            tokens.append(')')

    return tokens

# ---------------------------------------------------------------------------
# Алгоритм сортировочной станции
# ---------------------------------------------------------------------------

def _drain_operators(operators, output):
    while operators:
        op = operators.pop()
        if not _drain_ok(op):
            raise ValueError("Несбалансированные скобки: лишняя '('")
        output.append(op)

def infix_to_rpn(expression):
    tokens = tokenize(expression)
    output, operators = [], []

    for token in tokens:
        action = TOKEN_REGISTRY.get(token, {}).get('rpn_action', _action_operand)
        action(token, output, operators)

    _drain_operators(operators, output)

    if tokens and is_operator(tokens[-1]):
        raise ValueError(
            f"Выражение заканчивается на оператор '{tokens[-1]}'"
            f" — отсутствует правый операнд"
        )

    return output

# ---------------------------------------------------------------------------
# Вывод
# ---------------------------------------------------------------------------

def rpn_to_string(rpn_tokens):
    return ' '.join(token_symbol(t) for t in rpn_tokens)

# ---------------------------------------------------------------------------
# Точка входа
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("КОНВЕРТЕР В ОБРАТНУЮ ПОЛЬСКУЮ ЗАПИСЬ (ОПЗ)")
    print("=" * 60)
    print("Поддерживаемые операции: +, -, *, /, ^ (степень), ! (факториал), ++, --")
    print("Функции: sin, cos, tg, ctg  [скобки необязательны]")
    print("  sin x+1 = sin(x+1),  sin(x)+1 = sin(x)+1")
    print("Операнды: числа и переменные (x, y, ab, ...)")
    print("Унарный минус: -(x), -y")
    print("Для выхода введите: exit или q")
    print("=" * 60)

    while True:
        try:
            expr = input("\nВведите выражение: ").strip()
            if expr.lower() in ('exit', 'q', 'quit', 'выход'):
                print("До свидания!")
                break
            if not expr:
                continue
            rpn = infix_to_rpn(expr)
            print(f"Постфиксная (ОПЗ): {rpn_to_string(rpn)}")
        except ValueError as e:
            print(f"Ошибка: {e}")
        except KeyboardInterrupt:
            print("\nДо свидания!")
            break