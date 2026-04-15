def shunting_yard(tokens: List[str]) -> str:
    """Алгоритм сортировочной станции"""
    output = []
    op_stack = []  # стек для операторов
    postfix_stack = []  # стек для постфиксных операторов
    
    for i, token in enumerate(tokens):
        # Операнды
        if token not in ALL_OPS and token not in '()' and token not in FUNCTIONS:
            output.append(token)
            # Если есть накопленные постфиксные операторы - добавляем их после операнда
            while postfix_stack:
                output.append(postfix_stack.pop())
        
        # Функции
        elif token in FUNCTIONS:
            op_stack.append(token)
        
        # Постфиксные операторы - сохраняем во временный стек
        elif token in POSTFIX_OPS:
            postfix_stack.append(token)
        
        # Левая скобка
        elif token == '(':
            op_stack.append(token)
        
        # Правая скобка
        elif token == ')':
            while op_stack and op_stack[-1] != '(':
                output.append(op_stack.pop())
            if op_stack and op_stack[-1] == '(':
                op_stack.pop()
            if op_stack and op_stack[-1] in FUNCTIONS:
                output.append(op_stack.pop())
        
        # Операторы
        elif token in OPERATORS:
            # Унарный минус
            if token == '-' and (i == 0 or tokens[i-1] in OPERATORS | {'('} | FUNCTIONS):
                token = '~'
            
            # Выталкиваем операторы с бОльшим приоритетом
            while (op_stack and op_stack[-1] != '(' and op_stack[-1] not in FUNCTIONS and
                   (get_precedence(op_stack[-1]) > get_precedence(token) or
                    (get_precedence(op_stack[-1]) == get_precedence(token) and not is_right_assoc(token)))):
                output.append(op_stack.pop())
            op_stack.append(token)
    
    # Выгружаем оставшиеся операторы
    while op_stack:
        output.append(op_stack.pop())
    
    return ' '.join(output)
