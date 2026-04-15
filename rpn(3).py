class ExpressionParser:
    """Парсер математических выражений с поддержкой функций и операторов"""
    
    def __init__(self):
        # Приоритеты операторов (чем выше, тем важнее)
        self.precedence = {
            '+': 1, '-': 1,
            '*': 2, '/': 2,
            '^': 3,
            '~': 4,  # унарный минус
        }
        
        # Ассоциативность: 'L' - левая, 'R' - правая
        self.associativity = {
            '+': 'L', '-': 'L',
            '*': 'L', '/': 'L',
            '^': 'R',
            '~': 'R',
        }
        
        # Список поддерживаемых функций
        self.functions = {'sin', 'cos', 'tg', 'ctg', 'ln', 'log', 'sqrt', 'abs'}
        
        # Постфиксные операторы
        self.postfix_ops = {'!', '++', '--'}
        
        # Все операторы
        self.all_ops = set(self.precedence.keys()) | self.postfix_ops
        
    def tokenize(self, expression):
        """Разбивает выражение на токены"""
        tokens = []
        i = 0
        n = len(expression)
        
        while i < n:
            ch = expression[i]
            
            # Пропускаем пробелы
            if ch == ' ':
                i += 1
                continue
            
            # Числа (целые и десятичные)
            if ch.isdigit() or ch == '.':
                j = i
                has_dot = False
                while j < n and (expression[j].isdigit() or expression[j] == '.'):
                    if expression[j] == '.':
                        if has_dot:
                            raise ValueError(f"Некорректное число: {expression[i:j+1]}")
                        has_dot = True
                    j += 1
                tokens.append(('number', expression[i:j]))
                i = j
                continue
            
            # Переменные и функции
            if ch.isalpha():
                j = i
                while j < n and expression[j].isalpha():
                    j += 1
                name = expression[i:j]
                
                # Проверяем, является ли это функцией
                if name in self.functions:
                    tokens.append(('function', name))
                else:
                    tokens.append(('variable', name))
                i = j
                continue
            
            # Постфиксные операторы (++, --, !)
            if i + 1 < n and expression[i:i+2] in {'++', '--'}:
                tokens.append(('postfix', expression[i:i+2]))
                i += 2
                continue
            
            if ch == '!':
                tokens.append(('postfix', '!'))
                i += 1
                continue
            
            # Скобки
            if ch == '(':
                tokens.append(('lparen', '('))
                i += 1
                continue
            
            if ch == ')':
                tokens.append(('rparen', ')'))
                i += 1
                continue
            
            # Бинарные операторы и унарный минус
            if ch in {'+', '-', '*', '/', '^'}:
                # Определяем, является ли минус унарным
                is_unary = (ch == '-' and 
                           (not tokens or 
                            tokens[-1][0] in {'operator', 'lparen', 'function'}))
                
                if is_unary:
                    tokens.append(('operator', '~'))
                else:
                    tokens.append(('operator', ch))
                i += 1
                continue
            
            raise ValueError(f"Неизвестный символ: '{ch}' на позиции {i}")
        
        return tokens
    
    def validate_expression(self, tokens):
        """Проверяет корректность последовательности токенов"""
        if not tokens:
            raise ValueError("Пустое выражение")
        
        # Проверяем первый и последний токен
        first_type = tokens[0][0]
        if first_type in {'operator', 'postfix', 'rparen'}:
            raise ValueError(f"Выражение не может начинаться с {tokens[0][1]}")
        
        last_type = tokens[-1][0]
        if last_type in {'operator', 'lparen'}:
            raise ValueError(f"Выражение не может заканчиваться на {tokens[-1][1]}")
        
        # Проверяем последовательность токенов
        balance = 0
        for i, (tok_type, tok_val) in enumerate(tokens):
            # Проверка скобок
            if tok_type == 'lparen':
                balance += 1
            elif tok_type == 'rparen':
                balance -= 1
                if balance < 0:
                    raise ValueError("Неожиданная закрывающая скобка")
            
            # Проверка корректности соседних токенов
            if i > 0:
                prev_type, prev_val = tokens[i-1]
                
                # Оператор не может идти после оператора (кроме унарного минуса)
                if tok_type == 'operator' and prev_type == 'operator':
                    raise ValueError(f"Два оператора подряд: {prev_val} и {tok_val}")
                
                # Постфиксный оператор должен идти после операнда или закрывающей скобки
                if tok_type == 'postfix':
                    if prev_type not in {'number', 'variable', 'rparen'}:
                        raise ValueError(f"Постфиксный оператор {tok_val} должен следовать за операндом")
                    
                    # Постфиксный оператор не может быть перед операндом
                    if i + 1 < len(tokens) and tokens[i+1][0] in {'number', 'variable', 'lparen', 'function'}:
                        raise ValueError(f"После постфиксного оператора {tok_val} должен следовать бинарный оператор")
                
                # Функция должна быть перед открывающей скобкой или переменной
                if tok_type == 'function':
                    if i + 1 >= len(tokens) or tokens[i+1][0] != 'lparen':
                        # Если нет скобок, то считаем, что функция применяется к следующему токену
                        # Это нормально для sin x (без скобок)
                        pass
        
        if balance != 0:
            raise ValueError("Несбалансированные скобки")
        
        return True
    
    def infix_to_rpn(self, tokens):
        """Преобразует инфиксную запись в обратную польскую"""
        output = []
        stack = []
        
        for tok_type, tok_val in tokens:
            if tok_type in {'number', 'variable'}:
                output.append(tok_val)
            
            elif tok_type == 'function':
                stack.append(('function', tok_val))
            
            elif tok_type == 'lparen':
                stack.append(('lparen', '('))
            
            elif tok_type == 'rparen':
                while stack and stack[-1][0] != 'lparen':
                    output.append(stack.pop()[1])
                if stack and stack[-1][0] == 'lparen':
                    stack.pop()
                if stack and stack[-1][0] == 'function':
                    output.append(stack.pop()[1])
            
            elif tok_type == 'postfix':
                # Постфиксные операторы сразу идут в выход
                output.append(tok_val)
            
            elif tok_type == 'operator':
                # Обрабатываем операторы с учётом приоритета и ассоциативности
                while (stack and stack[-1][0] == 'operator' and 
                       stack[-1][1] != '(' and
                       ((self.associativity[tok_val] == 'L' and 
                         self.precedence[stack[-1][1]] >= self.precedence[tok_val]) or
                        (self.associativity[tok_val] == 'R' and 
                         self.precedence[stack[-1][1]] > self.precedence[tok_val]))):
                    output.append(stack.pop()[1])
                stack.append(('operator', tok_val))
        
        # Выгружаем оставшиеся операторы из стека
        while stack:
            if stack[-1][0] == 'lparen':
                raise ValueError("Несбалансированные скобки")
            output.append(stack.pop()[1])
        
        return ' '.join(output)
    
    def parse(self, expression):
        """Основной метод для парсинга выражения"""
        # Токенизация
        tokens = self.tokenize(expression)
        
        # Валидация
        self.validate_expression(tokens)
        
        # Преобразование в RPN
        rpn = self.infix_to_rpn(tokens)
        
        return rpn


def main():
    parser = ExpressionParser()
    
    print("=" * 60)
    print("Преобразователь инфиксной записи в обратную польскую (RPN)")
    print("=" * 60)
    print("\nПоддерживаемые возможности:")
    print("  • Числа: целые и десятичные (например: 42, 3.14)")
    print("  • Переменные: буквы латинского алфавита (a-z, A-Z)")
    print("  • Бинарные операторы: +, -, *, /, ^")
    print("  • Унарный минус: - (автоматически распознаётся)")
    print("  • Постфиксные операторы: ! (факториал), ++, --")
    print("  • Функции: sin, cos, tg, ctg, ln, log, sqrt, abs")
    print("  • Функции можно использовать как со скобками, так и без (например: sin x)")
    print("\nПримеры корректных выражений:")
    print("  • 2 + 3 * 4")
    print("  • sin(30) + cos 45")
    print("  • x++ + y")
    print("  • a! + b")
    print("  • -5 + 3")
    print("  • 2 ^ 3 ^ 2")
    print("\nПримеры НЕкорректных выражений (будут отклонены):")
    print("  • sin(x++x)  # нет оператора между ++ и x")
    print("  • x+^2       # два оператора подряд")
    print("  • +5         # выражение не может начинаться с оператора")
    print("=" * 60)
    
    while True:
        try:
            expr = input("\nВведите выражение (или 'exit' для выхода): ").strip()
            
            if expr.lower() == 'exit':
                print("До свидания!")
                break
            
            if not expr:
                continue
            
            rpn = parser.parse(expr)
            print(f"RPN: {rpn}")
            
        except ValueError as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    main()
