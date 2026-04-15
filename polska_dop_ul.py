from typing import List

# Константы
OPERATORS = {'+', '-', '*', '/', '^'}
POSTFIX_OPS = {'++', '--', '!'}
FUNCTIONS = {'sin', 'cos', 'tg', 'ctg'}
ALL_OPS = OPERATORS | POSTFIX_OPS

PRECEDENCE = {'+':2, '-':2, '*':3, '/':3, '^':4, '~':5, '!':6, '++':6, '--':6}
RIGHT_ASSOC = {'^', '~', '++', '--'}


def tokenize(expr: str) -> List[str]:
    """Разбивает выражение на токены"""
    tokens, i, n = [], 0, len(expr)
    
    while i < n:
        c = expr[i]
        if c == ' ': 
            i += 1
            continue
        
        if c.isalnum():
            j = i
            while j < n and expr[j].isalnum():
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue
        
        if i + 1 < n and expr[i:i+2] in POSTFIX_OPS:
            tokens.append(expr[i:i+2])
            i += 2
            continue
        
        if c in '+-*/^()!.':
            tokens.append(c)
            i += 1
            continue
        
        raise ValueError(f"Неизвестный символ: '{c}'")
    
    return tokens


def validate(tokens: List[str]) -> None:
    """Проверяет корректность выражения"""
    if not tokens:
        raise ValueError("Пустое выражение")
    
    def is_operand(t: str) -> bool:
        return t not in ALL_OPS and t not in '()' and t not in FUNCTIONS
    
    # Проверка первого и последнего токена
    if tokens[0] in OPERATORS - {'-'}:
        raise ValueError(f"Выражение не может начинаться с '{tokens[0]}'")
    if tokens[0] in POSTFIX_OPS:
        raise ValueError(f"Постфиксный оператор не может быть в начале")
    if tokens[-1] in OPERATORS:
        raise ValueError(f"Выражение не может заканчиваться оператором '{tokens[-1]}'")
    
    # Проверка последовательности и скобок
    balance = 0
    for i in range(len(tokens)):
        curr = tokens[i]
        prev = tokens[i - 1] if i > 0 else None
        
        if curr == '(':
            balance += 1
            if i + 1 < len(tokens) and tokens[i+1] in POSTFIX_OPS:
                raise ValueError(f"После '(' не может следовать постфиксный оператор")
        
        elif curr == ')':
            balance -= 1
            if balance < 0:
                raise ValueError("Лишняя закрывающая скобка")
        
        if prev is None:
            continue
            
        if is_operand(prev) and is_operand(curr):
            raise ValueError(f"Отсутствует оператор между '{prev}' и '{curr}'")
        
        if prev in OPERATORS and curr in OPERATORS:
            raise ValueError(f"Два бинарных оператора подряд: '{prev}' и '{curr}'")
        
        if prev in POSTFIX_OPS and curr in POSTFIX_OPS:
            raise ValueError(f"Два постфиксных оператора подряд: '{prev}' и '{curr}'")
        
        if prev in POSTFIX_OPS and is_operand(curr):
            raise ValueError(f"После постфиксного оператора '{prev}' должен следовать бинарный оператор")
        
        if curr in POSTFIX_OPS:
            if not (is_operand(prev) or prev == ')'):
                raise ValueError(f"Постфиксный оператор '{curr}' должен следовать за операндом")
    
    if balance != 0:
        raise ValueError("Несбалансированные скобки")


def get_precedence(op: str) -> int:
    return PRECEDENCE.get(op, 0)


def is_right_assoc(op: str) -> bool:
    return op in RIGHT_ASSOC


def shunting_yard(tokens: List[str]) -> str:
    """Алгоритм сортировочной станции"""
    output, stack = [], []
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        # Операнды
        if token not in ALL_OPS and token not in '()' and token not in FUNCTIONS:
            output.append(token)
        
        # Функции
        elif token in FUNCTIONS:
            stack.append(token)
        
        # Постфиксные операторы - НЕ добавляем сразу, а сохраняем для текущего операнда
        elif token in POSTFIX_OPS:
            # Проверяем, есть ли операнд в output
            if output and output[-1] not in POSTFIX_OPS:
                # Временно сохраняем постфиксный оператор, чтобы добавить после следующего операнда?
                # Нет, добавляем его в специальный стек для постфиксных операторов
                stack.append(('postfix', token))
            else:
                raise ValueError(f"Постфиксный оператор '{token}' не может быть применён")
        
        # Левая скобка
        elif token == '(':
            stack.append(('lparen', token))
        
        # Правая скобка
        elif token == ')':
            while stack and stack[-1][0] != 'lparen':
                if stack[-1][0] == 'postfix':
                    output.append(stack[-1][1])
                elif stack[-1][0] == 'operator':
                    output.append(stack[-1][1])
                stack.pop()
            if stack and stack[-1][0] == 'lparen':
                stack.pop()
            if stack and stack[-1][0] == 'function':
                output.append(stack[-1][1])
                stack.pop()
        
        # Операторы
        elif token in OPERATORS:
            # Унарный минус
            if token == '-' and (i == 0 or tokens[i-1] in OPERATORS | {'('} | FUNCTIONS):
                token = '~'
            
            # Выталкиваем операторы с бОльшим или равным приоритетом
            while (stack and stack[-1][0] != 'lparen' and stack[-1][0] != 'function' and
                   (get_precedence(stack[-1][1]) > get_precedence(token) or
                    (get_precedence(stack[-1][1]) == get_precedence(token) and not is_right_assoc(token)))):
                output.append(stack.pop()[1])
            stack.append(('operator', token))
        
        i += 1
    
    # Выгружаем оставшиеся операторы из стека
    while stack:
        if stack[-1][0] == 'postfix':
            output.append(stack[-1][1])
        elif stack[-1][0] == 'operator':
            output.append(stack[-1][1])
        stack.pop()
    
    return ' '.join(output)


def infix_to_rpn(expression: str) -> str:
    """Преобразует инфиксную запись в обратную польскую"""
    tokens = tokenize(expression)
    validate(tokens)
    return shunting_yard(tokens)


def main():
    print("=" * 60)
    print("Преобразование инфиксной записи в RPN")
    print("=" * 60)
    
    # Тесты
    tests = [
        "x +++ x",
        "x+++x",
        "x++ + y",
        "x + y++",
        "a! + b",
    ]
    
    print("\nТЕСТЫ:")
    for expr in tests:
        try:
            result = infix_to_rpn(expr)
            print(f"{expr:15} -> {result}")
        except Exception as e:
            print(f"{expr:15} -> ОШИБКА: {e}")


if __name__ == "__main__":
    main()
