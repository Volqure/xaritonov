import math

def infix_to_rpn(expression):
    """
    Преобразует инфиксное выражение в постфиксную запись (RPN).
    
    Аргументы:
        expression: строка с инфиксным выражением (например: "3+4*2")
    
    Возвращает:
        строку в постфиксной записи (например: "3 4 2 * +")
    """
    
    # Приоритеты операторов
    precedence = {
        '!': 4,      # факториал (унарный постфиксный)
        '++': 3,     # инкремент (унарный префиксный/постфиксный)
        '--': 3,     # декремент (унарный префиксный/постфиксный)
        '^': 3,
        '*': 2,
        '/': 2,
        '+': 1,
        '-': 1
    }
    
    # Ассоциативность операторов
    associativity = {
        '++': 'R',   # унарный оператор - правоассоциативный
        '--': 'R',   # унарный оператор - правоассоциативный
        '!': 'L',    # факториал - левоассоциативный
        '^': 'R',
        '*': 'L',
        '/': 'L',
        '+': 'L',
        '-': 'L'
    }
    
    # Список функций
    functions = ['sin', 'cos', 'tg', 'ctg']
    
    # Разбиваем выражение на токены
    tokens = []
    i = 0
    n = len(expression)
    
    while i < n:
        ch = expression[i]
        
        # Пропускаем пробелы
        if ch == ' ':
            i += 1
            continue
        
        # Проверяем на операторы ++ и --
        if i + 1 < n and expression[i:i+2] == '++':
            tokens.append('++')
            i += 2
            continue
        elif i + 1 < n and expression[i:i+2] == '--':
            tokens.append('--')
            i += 2
            continue
        
        # Проверяем на факториал
        if ch == '!':
            tokens.append('!')
            i += 1
            continue
        
        # Проверяем на функции
        if i + 2 < n and expression[i:i+3] == 'sin':
            tokens.append('sin')
            i += 3
            continue
        elif i + 2 < n and expression[i:i+3] == 'cos':
            tokens.append('cos')
            i += 3
            continue
        elif i + 2 < n and expression[i:i+3] == 'ctg':
            tokens.append('ctg')
            i += 3
            continue
        elif i + 1 < n and expression[i:i+2] == 'tg':
            tokens.append('tg')
            i += 2
            continue
        
        # Проверяем на числа
        if ch.isdigit() or ch == '.':
            j = i
            while j < n and (expression[j].isdigit() or expression[j] == '.'):
                j += 1
            tokens.append(expression[i:j])
            i = j
            continue
        
        # Проверяем на операторы и скобки
        if ch in '+-*/^()':
            tokens.append(ch)
            i += 1
            continue
        
        # Если символ не распознан
        raise ValueError(f"Неизвестный символ: {ch}")
    
    # Алгоритм сортировочной станции
    output = []
    stack = []
    
    # Функция для определения, является ли токен унарным оператором
    def is_unary_operator(token, position):
        if token not in ['++', '--']:
            return False
        # Если это первый токен или предыдущий токен - оператор или '('
        if position == 0:
            return True
        prev_token = tokens[position - 1]
        if prev_token in precedence or prev_token == '(':
            return True
        return False
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        # Если токен - число
        if token.replace('.', '').replace('-', '').isdigit() or (token[0] == '-' and len(token) > 1 and token[1:].replace('.', '').isdigit()):
            output.append(token)
        
        # Если токен - функция
        elif token in functions:
            stack.append(token)
        
        # Если токен - '('
        elif token == '(':
            stack.append(token)
        
        # Если токен - ')'
        elif token == ')':
            # Выталкиваем операторы до '('
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            # Удаляем '('
            if stack and stack[-1] == '(':
                stack.pop()
            # Если на вершине стека функция - выталкиваем её
            if stack and stack[-1] in functions:
                output.append(stack.pop())
        
        # Если токен - унарный оператор (префиксный)
        elif token in ['++', '--'] and is_unary_operator(token, i):
            # Для унарных операторов используем специальную метку
            output.append('u' + token)
        
        # Если токен - факториал (постфиксный унарный оператор)
        elif token == '!':
            # Факториал применяется к предыдущему операнду
            output.append('!')
        
        # Если токен - бинарный оператор
        elif token in precedence:
            # Выталкиваем операторы с большим или равным приоритетом
            while (stack and stack[-1] != '(' and 
                   stack[-1] in precedence and
                   ((associativity[token] == 'L' and precedence[stack[-1]] >= precedence[token]) or
                    (associativity[token] == 'R' and precedence[stack[-1]] > precedence[token]))):
                output.append(stack.pop())
            stack.append(token)
        
        i += 1
    
    # Выталкиваем оставшиеся операторы
    while stack:
        output.append(stack.pop())
    
    # Возвращаем RPN строку
    return ' '.join(output)


def main():
    """
    Главная функция программы
    """
    print("Преобразование инфиксной записи в RPN")
    print("Поддерживаемые операторы: +, -, *, /, ^, ++, --, !")
    print("Поддерживаемые функции: sin, cos, tg, ctg")
    print("=" * 60)
    
    # Тестовые примеры
    test_expressions = [
        "3+4",
        "2+3*5",
        "(2+3)*5",
        "sin(1.57)",
        "sin(3+4)",
        "cos(0)",
        "tg(0.785)",
        "2^3+sin(4)",
        "3+4*2/(1-5)^2^3",
        "sin(cos(tg(1)))",
        "3+4*sin(5)+cos(2)",
        "(2+3)*(4-1)^2",
        "sin(30)+cos(60)",
        "2*sin(90)+3*cos(0)",
        "(5+3)*2^3/4",
        # Новые примеры с ++, -- и !
        "x++",
        "++x",
        "x++ + y",
        "++x * y",
        "x!",
        "5!",
        "x! + y",
        "x++ + y!",
        "++x!",
        "x++!",
        "x++ * y--",
        "sin(x!)",
        "cos(++x)",
        "tg(x!--)",
        "5! + 3!",
        "(x++)!",
        "x++ + ++y",
        "x! * y!",
        "sin(x)!"
    ]
    
    for expr in test_expressions:
        try:
            rpn = infix_to_rpn(expr)
            print(f"{expr:30} -> {rpn}")
        except Exception as e:
            print(f"{expr:30} -> Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("Интерактивный режим (введите 'exit' для выхода)")
    print("-" * 60)
    print("Примеры: x++, ++x, 5!, x!+y, ++x*y, sin(x!)")
    print("-" * 60)
    
    while True:
        user_input = input("\nВведите выражение: ").strip()
        
        if user_input.lower() == 'exit':
            break
        
        if not user_input:
            continue
        
        try:
            rpn = infix_to_rpn(user_input)
            print(f"RPN: {rpn}")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()