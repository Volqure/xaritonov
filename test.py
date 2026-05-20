from collections import deque
import operator
import math


class Operator:
    def __init__(self, symbol, precedence, arity, func):
        self.symbol = symbol
        self.precedence = precedence
        self.arity = arity
        self.func = func


class RPNConverter:
    def __init__(self):
        self.output = []
        self.stack = deque()
        self.operand_count = 0

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

    def tokenize(self, expression):
        """Разбивает выражение на токены по пробелам и проверяет их валидность"""
        tokens = expression.split()
        valid_tokens = set(self.operators.keys()) | {'(', ')'}

        for token in tokens:
            try:
                float(token)
                continue
            except ValueError:
                pass

            if token.isalnum() and token not in self.operators:
                continue

            if token in valid_tokens:
                continue

            raise ValueError(f"Ошибка токенизации: неизвестный токен '{token}'")

        return tokens

    def is_operator(self, token):
        return token in self.operators

    def get_arity(self, token):
        return self.operators[token].arity

    def check_operand_count(self, required, operation_type):
        if self.operand_count < required:
            raise ValueError(
                f"Ошибка в расчете выражения: недостаточно операндов для {operation_type} операции. "
                f"Требуется {required}, доступно {self.operand_count}"
            )

    def shunting_yard(self, expression):
        tokens = self.tokenize(expression)
        
        self.output = []
        self.stack = deque()
        self.operand_count = 0
        last_was_operand = False  # Флаг для проверки двух операндов подряд
        
        for i, token in enumerate(tokens):
            # Проверка: является ли токен операндом (число)
            try:
                float(token)
                # ПРОВЕРКА: два операнда подряд
                if last_was_operand:
                    raise ValueError(
                        f"Ошибка: два операнда подряд. Предыдущий операнд: {tokens[i-1]}, "
                        f"текущий операнд: {token}"
                    )
                self.output.append(token)
                self.operand_count += 1
                last_was_operand = True
                continue
            except ValueError:
                pass
            
            # Проверка: переменная
            if token.isalnum() and token not in self.operators:
                # ПРОВЕРКА: два операнда подряд
                if last_was_operand:
                    raise ValueError(
                        f"Ошибка: два операнда подряд. Предыдущий операнд: {tokens[i-1]}, "
                        f"текущая переменная: {token}"
                    )
                self.output.append(token)
                self.operand_count += 1
                last_was_operand = True
                continue
            
            # Левая скобка
            if token == '(':
                self.stack.append(token)
                # Скобка не меняет last_was_operand
                continue
            
            # Правая скобка
            if token == ')':
                while self.stack and self.stack[-1] != '(':
                    popped = self.stack.pop()
                    self.output.append(popped)
                    
                    arity = self.get_arity(popped)
                    if arity == 'binary':
                        self.check_operand_count(2, "бинарной")
                        self.operand_count -= 1
                        last_was_operand = False
                    elif arity == 'unary':
                        self.check_operand_count(1, "унарной")
                        # Унарный не сбрасывает last_was_operand
                
                if self.stack and self.stack[-1] == '(':
                    self.stack.pop()
                else:
                    raise ValueError("Ошибка: несогласованные скобки")
                continue
            
            # Если токен - оператор
            if self.is_operator(token):
                op = self.operators[token]
                
                while (self.stack and self.stack[-1] != '(' and
                       self.is_operator(self.stack[-1])):
                    top_op = self.operators[self.stack[-1]]
                    if top_op.precedence > op.precedence:
                        popped = self.stack.pop()
                        self.output.append(popped)
                        
                        if top_op.arity == 'binary':
                            self.check_operand_count(2, "бинарной")
                            self.operand_count -= 1
                            last_was_operand = False
                        elif top_op.arity == 'unary':
                            self.check_operand_count(1, "унарной")
                            # Унарный не сбрасывает
                    else:
                        break
                
                self.stack.append(token)
                # КЛЮЧЕВОЙ МОМЕНТ: для бинарного оператора сбрасываем флаг
                if op.arity == 'binary':
                    last_was_operand = False
                # Для унарного НЕ сбрасываем last_was_operand
                continue
            
            raise ValueError(f"Ошибка: неизвестный токен '{token}'")
        
        # Выталкиваем оставшиеся операторы
        while self.stack:
            if self.stack[-1] == '(' or self.stack[-1] == ')':
                raise ValueError("Ошибка: несогласованные скобки")
            
            popped = self.stack.pop()
            self.output.append(popped)
            
            arity = self.get_arity(popped)
            if arity == 'binary':
                self.check_operand_count(2, "бинарной")
                self.operand_count -= 1
                last_was_operand = False
            elif arity == 'unary':
                self.check_operand_count(1, "унарной")
                # Унарный не сбрасывает
        
        if self.operand_count != 1:
            raise ValueError(
                f"Ошибка в расчете выражения: некорректное количество операндов. "
                f"Ожидается 1, получено {self.operand_count}"
            )
        
        return ' '.join(self.output)


def main():
    converter = RPNConverter()
    print("Калькулятор обратной польской нотации (RPN)")
    print("Вводите выражения через пробел (например: ( 5 + 3 ) * 2 )")
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
