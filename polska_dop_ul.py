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
            # После '(' не может быть постфиксного оператора
            if i + 1 < len(tokens) and tokens[i+1] in POSTFIX_OPS:
                raise ValueError(f"После '(' не может следовать постфиксный оператор '{tokens[i+1]}'")
        
        elif curr == ')':
            balance -= 1
            if balance < 0:
                raise ValueError("Лишняя закрывающая скобка")
        
        if prev is None:
            continue
            
        # Проверки для пар токенов
        
        # Два операнда подряд
        if is_operand(prev) and is_operand(curr):
            raise ValueError(f"Отсутствует оператор между '{prev}' и '{curr}'")
        
        # Два бинарных оператора подряд
        if prev in OPERATORS and curr in OPERATORS:
            raise ValueError(f"Два бинарных оператора подряд: '{prev}' и '{curr}'")
        
        # Два постфиксных оператора подряд
        if prev in POSTFIX_OPS and curr in POSTFIX_OPS:
            raise ValueError(f"Два постфиксных оператора подряд: '{prev}' и '{curr}'")
        
        # Постфиксный оператор перед операндом (должен быть бинарный оператор)
        if prev in POSTFIX_OPS and is_operand(curr):
            raise ValueError(f"После постфиксного оператора '{prev}' должен следовать бинарный оператор, а не операнд '{curr}'")
        
        # Постфиксный оператор должен следовать за операндом или скобкой
        if curr in POSTFIX_OPS:
            if not (is_operand(prev) or prev == ')'):
                raise ValueError(f"Постфиксный оператор '{curr}' должен следовать за операндом или скобкой, а не за '{prev}'")
        
        # Бинарный оператор перед постфиксным - РАЗРЕШЕНО (x++ + x)
        # поэтому НЕТ проверки if prev in OPERATORS and curr in POSTFIX_OPS
    
    if balance != 0:
        raise ValueError("Несбалансированные скобки")


def get_precedence(op: str) -> int:
    return PRECEDENCE.get(op, 0)


def is_right_assoc(op: str) -> bool:
    return op in RIGHT_ASSOC


def shunting_yard(tokens: List[str]) -> str:
    """Алгоритм сортировочной станции"""
    output, stack = [], []
    
    for i, token in enumerate(tokens):
        # Операнды
        if token not in ALL_OPS and token not in '()' and token not in FUNCTIONS:
            output.append(token)
        
        # Функции
        elif token in FUNCTIONS:
            stack.append(token)
        
        # Постфиксные операторы
        elif token in POSTFIX_OPS:
            output.append(token)
        
        # Левая скобка
        elif token == '(':
            stack.append(token)
        
        # Правая скобка
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()
            if stack and stack[-1] in FUNCTIONS:
                output.append(stack.pop())
        
        # Операторы
        elif token in OPERATORS:
            # Унарный минус
            if token == '-' and (i == 0 or tokens[i-1] in OPERATORS | {'('} | FUNCTIONS):
                token = '~'
            
            # Выталкиваем операторы с бОльшим приоритетом
            while (stack and stack[-1] != '(' and stack[-1] not in FUNCTIONS and
                   (get_precedence(stack[-1]) > get_precedence(token) or
                    (get_precedence(stack[-1]) == get_precedence(token) and not is_right_assoc(token)))):
                output.append(stack.pop())
            stack.append(token)
    
    # Выгружаем оставшиеся операторы
    while stack:
        output.append(stack.pop())
    
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
    print("Операторы: + - * / ^ ! ++ --")
    print("Функции: sin cos tg ctg")
    print("=" * 60)
    
    # Тесты с x +++ x
    tests = [
        "1+1",
        "2+3*4", 
        "sin(x)",
        "x++ + y",
        "x +++ x",      # x ++ + x -> x x ++ +
        "x+++x",        # без пробелов
        "a! + b",
        "x + y++",
    ]
    
    print("\nТЕСТЫ:")
    for expr in tests:
        try:
            result = infix_to_rpn(expr)
            print(f"{expr:15} -> {result}")
        except Exception as e:
            print(f"{expr:15} -> ОШИБКА: {e}")
    
    # Интерактивный режим
    print("\n" + "=" * 60)
    while True:
        expr = input("\nВыражение (exit для выхода): ").strip()
        if expr.lower() == 'exit':
            break
        if expr:
            try:
                print(f"RPN: {infix_to_rpn(expr)}")
            except Exception as e:
                print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
