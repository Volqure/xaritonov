def prec(op):
    """Возвращает приоритет оператора"""
    if op in ('+', '-'):
        return 1
    elif op in ('*', '/'):
        return 2
    else:
        return 0


def is_operator(c):
    """Проверяет, является ли символ оператором"""
    return c in ('+', '-', '*', '/')


def infix_to_postfix(s):
    """Преобразует инфиксное выражение в постфиксную запись"""
    stack = []
    result = []
    balance = 0
    expect_operand = True  # Ожидаем операнд (число, переменную или '(')
    
    i = 0
    while i < len(s):
        c = s[i]
        
        # Пропускаем пробелы
        if c.isspace():
            i += 1
            continue
        
        # Операнды (буквы или цифры)
        if c.isalnum():
            if not expect_operand:
                raise RuntimeError("Два операнда подряд (например, A B)")
            result.append(c)
            expect_operand = False
            i += 1
        
        # Левая скобка
        elif c == '(':
            if not expect_operand:
                raise RuntimeError("Недопустимая скобка после операнда или оператора (например, A(B))")
            stack.append(c)
            balance += 1
            i += 1
        
        # Правая скобка
        elif c == ')':
            if expect_operand:
                raise RuntimeError("Отсутствует операнд перед ')' (например, A + ())")
            if balance <= 0:
                raise RuntimeError("Лишняя закрывающая скобка")
            balance -= 1
            
            # Выталкиваем операторы до '('
            while stack and stack[-1] != '(':
                result.append(stack.pop())
            
            if not stack:
                raise RuntimeError("Несовпадение скобок")
            
            # Удаляем '('
            stack.pop()
            expect_operand = False
            i += 1
        
        # Операторы
        elif is_operator(c):
            if expect_operand:
                raise RuntimeError("Оператор в позиции, где должен быть операнд (например, +A, A * (+B))")
            
            # Выталкиваем операторы с бОльшим или равным приоритетом
            while (stack and stack[-1] != '(' and 
                   prec(stack[-1]) >= prec(c)):
                result.append(stack.pop())
            
            stack.append(c)
            expect_operand = True
            i += 1
        
        # Недопустимый символ
        else:
            raise RuntimeError(f"Недопустимый символ '{c}'")
    
    # Проверяем баланс скобок
    if balance != 0:
        raise RuntimeError("Не закрытая скобка")
    
    # Выталкиваем оставшиеся операторы из стека
    while stack:
        if stack[-1] in ('(', ')'):
            raise RuntimeError("Остаток скобок в стеке")
        result.append(stack.pop())
    
    return ''.join(result)


def main():
    """Главная функция"""
    # Тестовые примеры
    test_expressions = [
        "A+B*C",
        "A+B*C/D",
        "(A+B)*C",
        "A*(B+C)",
        "A+B-C",
        "A+B*(C-D)",
        "A B",      # Должна быть ошибка
        "A+",       # Должна быть ошибка
        "(A+B",     # Должна быть ошибка
        "+A",       # Должна быть ошибка
    ]
    
    print("=" * 50)
    print("Преобразование инфиксной записи в постфиксную")
    print("=" * 50)
    
    for expr in test_expressions:
        try:
            result = infix_to_postfix(expr)
            print(f"{expr:20} -> {result}")
        except RuntimeError as e:
            print(f"{expr:20} -> Ошибка: {e}")
    
    # Интерактивный режим
    print("\n" + "=" * 50)
    print("Интерактивный режим (Enter для выхода)")
    print("=" * 50)
    
    while True:
        try:
            expr = input("\nВведите выражение: ").strip()
            if not expr:
                break
            
            result = infix_to_postfix(expr)
            print(f"Результат: {result}")
            
        except RuntimeError as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    main()
