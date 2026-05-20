from collections import deque
import operator
import math


class Operator:
    def __init__(self, symbol, precedence, arity, func):
        self.symbol = symbol
        self.precedence = precedence
        self.arity = arity  # 'binary' или 'unary'
        self.func = func


class RPNConverter:
    def __init__(self):
        self.output = []
        self.stack = deque()
        self.operand_count = 0  # счетчик операндов

        # Таблица операторов с приоритетами и функциями
        self.operators = {
            '+': Operator('+', 1, 'binary', operator.add),
            '-': Operator('-', 1, 'binary', operator.sub),
            '*': Operator('*', 2, 'binary', operator.mul),
            '/': Operator('/', 2, 'binary', operator.truediv),
            '^': Operator('^', 3, 'binary', operator.pow),
            'tg': Operator('tg', 4, 'unary', math.tan),
            'sin': Operator('sin', 4, 'unary', math.sin),
            'cos': Operator('cos', 4, 'unary', math.cos),
            '!': Operator('!', 4, 'unary', math.factorial),
            '++': Operator('++', 4, 'unary', lambda x: x + 1),
            '--': Operator('--', 4, 'unary', lambda x: x - 1),
        }
        
        # Сортировка операторов по длине для корректного распознавания (сначала длинные)
        self.operator_patterns = sorted(self.operators.keys(), key=len, reverse=True)

    def tokenize(self, expression):
        """
        Токенизация выражения:
        1. Если в строке есть пробелы - разделяем по пробелам (приоритетный режим)
        2. Если пробелов нет - выполняем умную токенизацию
        """
        # Если есть пробелы - используем простое разделение (приоритетный режим)
        if ' ' in expression:
            tokens = expression.split()
            # Проверяем валидность токенов
            for token in tokens:
                self._validate_token(token)
            return tokens
        
        # Если пробелов нет - выполняем умную токенизацию
        return self._smart_tokenize(expression)
    
    def _validate_token(self, token):
        """Проверяет валидность одного токена"""
        valid_tokens = set(self.operators.keys()) | {'(', ')'}
        
        # Проверка: число (целое или десятичное)
        try:
            float(token)
            return
        except ValueError:
            pass
        
        # Проверка: переменная (буквы и цифры, но не оператор)
        if token.isalnum() and token not in self.operators:
            return
        
        # Проверка: оператор или скобка
        if token in valid_tokens:
            return
        
        # Если ничего не подошло - ошибка
        raise ValueError(f"Ошибка токенизации: неизвестный токен '{token}'")
    
    def _smart_tokenize(self, expression):
        """
        Умная токенизация выражения без пробелов
        Разбивает на числа, переменные, операторы и скобки
        """
        tokens = []
        i = 0
        length = len(expression)
        
        while i < length:
            char = expression[i]
            
            # Пропускаем пробелы (на случай если они есть)
            if char.isspace():
                i += 1
                continue
            
            # Обработка чисел (целых и десятичных)
            if char.isdigit() or (char == '.' and i + 1 < length and expression[i + 1].isdigit()):
                # Собираем число
                num_start = i
                has_dot = False
                while i < length and (expression[i].isdigit() or expression[i] == '.'):
                    if expression[i] == '.':
                        if has_dot:
                            raise ValueError(f"Ошибка токенизации: некорректное число (две точки) в позиции {num_start}")
                        has_dot = True
                    i += 1
                token = expression[num_start:i]
                tokens.append(token)
                continue
            
            # Обработка операторов (включая многосимвольные)
            matched = False
            for op in self.operator_patterns:
                if expression.startswith(op, i):
                    tokens.append(op)
                    i += len(op)
                    matched = True
                    break
            
            if matched:
                continue
            
            # Обработка скобок
            if char in '()':
                tokens.append(char)
                i += 1
                continue
            
            # Обработка переменных (буквы и цифры)
            if char.isalpha():
                var_start = i
                while i < length and (expression[i].isalpha() or expression[i].isdigit()):
                    i += 1
                token = expression[var_start:i]
                # Проверяем, не является ли это оператором (уже должно быть обработано)
                if token in self.operators:
                    # Это оператор, но почему-то не был обработан паттернами
                    tokens.append(token)
                else:
                    # Это переменная
                    tokens.append(token)
                continue
            
            # Если символ не распознан
            raise ValueError(f"Ошибка токенизации: неизвестный символ '{char}' на позиции {i}")
        
        # Проверяем валидность всех токенов
        for token in tokens:
            self._validate_token(token)
        
        return tokens

    def is_operator(self, token):
        return token in self.operators

    def get_arity(self, token):
        return self.operators[token].arity

    def check_operand_count(self, required, operation_type):
        """Проверяет достаточность операндов для операции"""
        if self.operand_count < required:
            raise ValueError(
                f"Ошибка в расчете выражения: недостаточно операндов для {operation_type} операции. "
                f"Требуется {required}, доступно {self.operand_count}"
            )

    def shunting_yard(self, expression):
        # Сначала токенизация
        tokens = self.tokenize(expression)
        
        print(f"DEBUG: Токены = {tokens}")  # Для отладки

        # Сброс состояния
        self.output = []
        self.stack = deque()
        self.operand_count = 0

        for token in tokens:
            # Проверка: является ли токен операндом (число или переменная)
            try:
                # Пробуем преобразовать в число
                float(token)
                self.output.append(token)
                self.operand_count += 1
                continue
            except ValueError:
                pass

            # Проверка: переменная
            if token.isalnum() and token not in self.operators:
                self.output.append(token)
                self.operand_count += 1
                continue

            # Левая скобка
            if token == '(':
                self.stack.append(token)
                continue

            # Правая скобка
            if token == ')':
                # Выталкиваем операторы из стека до левой скобки
                while self.stack and self.stack[-1] != '(':
                    popped = self.stack.pop()
                    self.output.append(popped)

                    # Проверка операндов
                    arity = self.get_arity(popped)
                    if arity == 'binary':
                        self.check_operand_count(2, "бинарной")
                        self.operand_count -= 1
                    elif arity == 'unary':
                        self.check_operand_count(1, "унарной")

                # Удаляем левую скобку
                if self.stack and self.stack[-1] == '(':
                    self.stack.pop()
                else:
                    raise ValueError("Ошибка: несогласованные скобки")
                continue

            # Если токен - оператор
            if self.is_operator(token):
                op = self.operators[token]

                # Пока стек не пуст и на вершине оператор (не скобка)
                while (self.stack and self.stack[-1] != '(' and
                       self.is_operator(self.stack[-1])):
                    top_op = self.operators[self.stack[-1]]
                    # Если верхний оператор имеет больший или равный приоритет (и левоассоциативен)
                    if top_op.precedence > op.precedence:
                        popped = self.stack.pop()
                        self.output.append(popped)

                        # Проверка операндов
                        if top_op.arity == 'binary':
                            self.check_operand_count(2, "бинарной")
                            self.operand_count -= 1
                        elif top_op.arity == 'unary':
                            self.check_operand_count(1, "унарной")
                    else:
                        break

                self.stack.append(token)
                continue

            raise ValueError(f"Ошибка: неизвестный токен '{token}'")

        # Добавляем оставшиеся операторы из стека
        while self.stack:
            if self.stack[-1] == '(' or self.stack[-1] == ')':
                raise ValueError("Ошибка: несогласованные скобки")

            popped = self.stack.pop()
            self.output.append(popped)

            # Проверка операндов
            arity = self.get_arity(popped)
            if arity == 'binary':
                self.check_operand_count(2, "бинарной")
                self.operand_count -= 1
            elif arity == 'unary':
                self.check_operand_count(1, "унарной")

        # Финальная проверка: в итоге должен остаться 1 операнд
        if self.operand_count != 1:
            raise ValueError(
                f"Ошибка в расчете выражения: некорректное количество операндов в выражении. "
                f"Ожидается 1, получено {self.operand_count}"
            )

        return ' '.join(self.output)


# Основная программа с вечным циклом
def main():
    converter = RPNConverter()
    print("Калькулятор обратной польской нотации (RPN)")
    print("Вводите выражения:")
    print("  - С пробелами: ( 5 + 3 ) * 2")
    print("  - Без пробелов: (5+3)*2")
    print("  - Смешанный режим: (5 + 3)*2")
    print("Для выхода введите 'stop'")
    print("-" * 50)

    while True:
        try:
            expr = input("Введите выражение: ").strip()

            if expr.lower() == 'stop':
                print("Программа завершена.")
                break

            if not expr:
                print("Пустая строка. Попробуйте снова.")
                continue

            rpn = converter.shunting_yard(expr)
            print(f"RPN: {rpn}")
            print("✓ Выражение корректно!")
            print("-" * 50)

        except ValueError as e:
            print(f"✗ {e}")
            print("-" * 50)
        except Exception as e:
            print(f"✗ Непредвиденная ошибка: {e}")
            print("-" * 50)


if __name__ == "__main__":
    main()