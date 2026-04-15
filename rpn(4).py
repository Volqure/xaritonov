        if i + 1 < n and expression[i:i + 2] == '++':
            if last_token_type is None:
                raise ValueError("Оператор ++ не может быть в начале выражения")
            if last_token_type not in ['operand', 'rparen']:
                raise ValueError(f"Оператор ++ должен следовать за операндом или скобкой, позиция {i}")
            # Проверка: после ++ не может сразу идти операнд
            j = i + 2
            while j < n and expression[j] == ' ':
                j += 1
            if j < n and (expression[j].isalpha() or expression[j].isdigit()):
                raise ValueError(f"После оператора ++ должен следовать бинарный оператор, позиция {i}")
            tokens.append('++')
            i += 2
            last_token_type = 'postfix_operator'
            continue
        elif i + 1 < n and expression[i:i + 2] == '--':
            if last_token_type is None:
                raise ValueError("Оператор -- не может быть в начале выражения")
            if last_token_type not in ['operand', 'rparen']:
                raise ValueError(f"Оператор -- должен следовать за операндом или скобкой, позиция {i}")
            # Проверка: после -- не может сразу идти операнд
            j = i + 2
            while j < n and expression[j] == ' ':
                j += 1
            if j < n and (expression[j].isalpha() or expression[j].isdigit()):
                raise ValueError(f"После оператора -- должен следовать бинарный оператор, позиция {i}")
            tokens.append('--')
            i += 2
            last_token_type = 'postfix_operator'
            continue

        if ch == '!':
            if last_token_type is None:
                raise ValueError("Факториал не может быть в начале выражения")
            if last_token_type not in ['operand', 'rparen']:
                raise ValueError(f"Факториал должен следовать за операндом или скобкой, позиция {i}")
            # Проверка: после ! не может сразу идти операнд
            j = i + 1
            while j < n and expression[j] == ' ':
                j += 1
            if j < n and (expression[j].isalpha() or expression[j].isdigit() or expression[j] == '('):
                raise ValueError(f"После факториала должен следовать бинарный оператор, позиция {i}")
            tokens.append('!')
            i += 1
            last_token_type = 'postfix_operator'
            continue
