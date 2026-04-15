from enum import Enum
from typing import List, Set, Dict

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
        
        # Буквы/цифры (переменные, числа, функции)
        if c.isalnum():
            j = i
            while j < n and expr[j].isalnum():
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue
        
        # Постфиксные операторы
        if i + 1 < n and expr[i:i+2] in POSTFIX_OPS:
            tokens.append(expr[i:i+2])
            i += 2
            continue
        
        # Одиночные символы
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
    for i, (prev, curr) in enumerate(zip([''] + tokens[:-1], tokens)):
        if curr == '(':
            balance += 1
        elif curr == ')':
            balance -= 1
            if balance < 0:
                raise ValueError("Лишняя закрывающая скобка")
        
        if i == 0:
            continue
            
        # Проверки для пар токенов
        if is_operand(prev) and is_operand(curr):
            raise ValueError(f"Отсутствует оператор между '{prev}' и '{curr}'")
        if prev in OPERATORS and curr in OPERATORS:
            raise ValueError(f"Два оператора подряд: '{prev}' и '{curr}'")
        if prev in POSTFIX_OPS and is_operand(curr):
            raise ValueError(f"После '{prev}' должен следовать бинарный оператор")
        if curr in POSTFIX_OPS and not is_operand(prev) and prev != ')':
            raise ValueError(f"'{curr}' должен следовать за операндом")
    
    if balance != 0:
        raise ValueError("Несбалансированные скобки")


def get_precedence(op: str) -> int:
    """Возвращает приоритет оператора"""
    return PRECEDENCE.get(op, 0)


def is_right_assoc(op: str) -> bool:
    """Проверяет правоассоциативность"""
    return op in RIGHT_ASSOC


def shunting_yard(tokens: List[str]) -> str:
    """Алгоритм сортировочной станции"""
    output, stack = [], []
    
    for i, token in enumerate(tokens):
        # Операнды
        if token not in ALL_OPS and token not in '()' and token not in FUNCTIONS:
            output.append(token)
        
        # Функции и постфиксные операторы
        elif token in FUNCTIONS:
            stack.append(token)
        elif token in POSTFIX_OPS:
            output.append(token)
        
        # Скобки
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # удаляем '('
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
    """Главная функция"""
    print("=" * 60)
    print("Преобразование инфиксной записи в RPN")
    print("=" * 60)
    print("Операторы: + - * / ^ ! ++ --")
    print("Функции: sin cos tg ctg")
    print("=" * 60)
    
    # Тесты
    tests = ["1+1", "2+3*4", "sin(x)", "x++ + y", "a! + b"]
    print("\nТЕСТЫ:")
    for expr in tests:
        try:
            print(f"{expr:12} -> {infix_to_rpn(expr)}")
        except Exception as e:
            print(f"{expr:12} -> Ошибка: {e}")
    
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
