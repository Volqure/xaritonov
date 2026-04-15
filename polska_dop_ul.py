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


def infix_to_rpn(expression: str) -> str:
    """Преобразует инфиксное выражение в обратную польскую запись"""
    tokens = tokenize(expression)
    
    if not tokens:
        raise ValueError("Пустое выражение")
    
    output = []
    stack = []
    
    for i, token in enumerate(tokens):
        # Операнды (числа, переменные)
        if token not in ALL_OPS and token not in '()' and token not in FUNCTIONS:
            output.append(token)
        
        # Функции
        elif token in FUNCTIONS:
            stack.append(token)
        
        # Постфиксные операторы - добавляем к предыдущему операнду
        elif token in POSTFIX_OPS:
            # Постфиксный оператор должен идти после операнда
            if not output:
                raise ValueError(f"Постфиксный оператор '{token}' не может быть в начале")
            # Добавляем сразу после операнда в output
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
            
            # Выталкиваем операторы с бОльшим или равным приоритетом
            while (stack and stack[-1] != '(' and stack[-1] not in FUNCTIONS and
                   (PRECEDENCE.get(stack[-1], 0) > PRECEDENCE.get(token, 0) or
                    (PRECEDENCE.get(stack[-1], 0) == PRECEDENCE.get(token, 0) and 
                     token not in RIGHT_ASSOC))):
                output.append(stack.pop())
            stack.append(token)
    
    # Выгружаем оставшиеся операторы
    while stack:
        output.append(stack.pop())
    
    return ' '.join(output)


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
        "1+1",
    ]
    
    print("\nТЕСТЫ:")
    for expr in tests:
        try:
            result = infix_to_rpn(expr)
            print(f"{expr:15} -> {result}")
        except Exception as e:
            print(f"{expr:15} -> ОШИБКА: {e}")
    
    # Детальный разбор
    print("\n" + "=" * 60)
    expr = "x +++ x"
    tokens = tokenize(expr)
    print(f"'{expr}' -> токены: {tokens}")
    print(f"RPN: {infix_to_rpn(expr)}")
    print("\nПОЧЕМУ ТАК:")
    print("  x +++ x  ->  x ++ + x")
    print("  В RPN постфиксный ++ применяется к первому x")
    print("  Получается: x ++ x +")


if __name__ == "__main__":
    main()
