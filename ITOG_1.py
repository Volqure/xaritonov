"""Конвертер инфикс → RPN. Упрощенная версия с единым реестром операторов."""

# Единый реестр операторов: имя, арность, приоритет, ассоциативность
OPERATORS = [
    # Скобки (максимальный приоритет 100)
    ("(", 0, 100, None),   # арность 0 означает скобку
    (")", 0, 100, None),
    # Постфиксные операторы (арность 1, идут после операнда)
    ("!", 1, 6, "POST"),   # POST - специальный тип для постфиксных
    ("++", 1, 6, "POST"),
    ("--", 1, 6, "POST"),
    # Префиксные операторы (арность 1, идут перед операндом)
    ("~", 1, 5, "R"),      # унарный минус
    ("sin", 1, 8, "R"),
    ("cos", 1, 8, "R"),
    ("tg", 1, 8, "R"),
    ("ctg", 1, 8, "R"),
    # Бинарные операторы (арность 2)
    ("+", 2, 2, "L"),
    ("-", 2, 2, "L"),
    ("*", 2, 3, "L"),
    ("/", 2, 3, "L"),
    ("^", 2, 4, "R"),
]

class Op:
    """Реестр операторов"""
    reg = {}  # Переименовано с _reg на reg
    
    def __init__(self, name, arity, prec, assoc):
        self.name = name
        self.arity = arity      # 0=скобка, 1=унарный, 2=бинарный
        self.prec = prec        # приоритет (чем выше, тем раньше)
        self.assoc = assoc      # "L"=левая, "R"=правая, "POST"=постфиксный, None=не важно
        Op.reg[name] = self
    
    @classmethod
    def register_all(cls):
        """Регистрация всех операторов из списка OPERATORS"""
        cls.reg.clear()
        for name, arity, prec, assoc in OPERATORS:
            cls(name, arity, prec, assoc)
    
    @classmethod
    def get(cls, name):
        """Получить оператор по имени"""
        return cls.reg.get(name)
    
    @classmethod
    def exists(cls, name):
        """Проверить существование оператора"""
        return name in cls.reg
    
    @classmethod
    def is_unary(cls, name):
        """Проверка на унарный оператор (префиксный или постфиксный)"""
        op = cls.get(name)
        return op is not None and op.arity == 1
    
    @classmethod
    def is_binary(cls, name):
        """Проверка на бинарный оператор"""
        op = cls.get(name)
        return op is not None and op.arity == 2
    
    @classmethod
    def is_prefix(cls, name):
        """Проверка на префиксный унарный оператор (не постфиксный)"""
        op = cls.get(name)
        return op is not None and op.arity == 1 and op.assoc != "POST"
    
    @classmethod
    def is_postfix(cls, name):
        """Проверка на постфиксный оператор"""
        op = cls.get(name)
        return op is not None and op.arity == 1 and op.assoc == "POST"
    
    @classmethod
    def is_left_paren(cls, name):
        """Проверка на открывающую скобку"""
        return name == "("
    
    @classmethod
    def is_right_paren(cls, name):
        """Проверка на закрывающую скобку"""
        return name == ")"
    
    @classmethod
    def is_paren(cls, name):
        """Проверка на любую скобку"""
        return name in "()"
    
    @classmethod
    def is_operand(cls, name):
        """Проверка на операнд (число или переменная)"""
        return not cls.is_paren(name) and not cls.exists(name)


def tokenize(expr):
    """
    Разбивает выражение на токены с учетом всех операторов из реестра.
    
    Пример: "2+3*sin(x)" -> ['2', '+', '3', '*', 'sin', '(', 'x', ')']
    """
    tokens = []
    i = 0
    n = len(expr)
    
    while i < n:
        ch = expr[i]
        
        # Пропуск пробелов
        if ch.isspace():
            i += 1
            continue
        
        # Проверка на двухсимвольные операторы (из реестра)
        if i + 1 < n:
            two_chars = expr[i:i+2]
            if Op.exists(two_chars):
                tokens.append(two_chars)
                i += 2
                continue
        
        # Проверка на односимвольные операторы и скобки (из реестра)
        if Op.exists(ch):
            tokens.append(ch)
            i += 1
            continue
        
        # Числа и идентификаторы (переменные, функции)
        if ch.isalnum() or ch == '.':
            j = i + 1
            while j < n and (expr[j].isalnum() or expr[j] == '.'):
                j += 1
            token = expr[i:j]
            tokens.append(token)
            i = j
            continue
        
        # Если ничего не подошло - ошибка
        raise ValueError(f"Неизвестный символ: '{ch}'")
    
    return tokens


class InfixToRpn:
    def __init__(self, expr):
        """Инициализация конвертера"""
        Op.register_all()
        self.source = expr
        raw_tokens = tokenize(expr)
        self.tokens = self._fold_unary(raw_tokens)
    
    def _fold_unary(self, tokens):
        """
        Заменяет унарный минус '-' на специальный оператор '~'.
        Унарным минус считается в следующих случаях:
        - первый токен
        - после открывающей скобки
        - после бинарного оператора
        - после префиксного оператора
        """
        result = []
        for i, token in enumerate(tokens):
            if token != '-':
                result.append(token)
                continue
            
            # Определяем предыдущий токен (если есть)
            prev = result[-1] if result else None
            
            # Проверяем, является ли минус унарным
            is_unary = (prev is None or 
                       Op.is_left_paren(prev) or 
                       Op.is_binary(prev) or 
                       Op.is_prefix(prev))
            
            if is_unary:
                result.append('~')  # Заменяем на специальный унарный минус
            else:
                result.append('-')  # Оставляем как бинарный
        return result
    
    def _validate(self):
        """
        Проверяет корректность выражения используя информацию из реестра.
        """
        ts = self.tokens
        
        if not ts:
            raise ValueError("Пустое выражение")
        
        # Проверка начала выражения
        first = ts[0]
        if Op.is_binary(first):
            raise ValueError(f"Нельзя начинать с бинарного оператора '{first}'")
        if Op.is_postfix(first):
            raise ValueError(f"Нельзя начинать с постфиксного оператора '{first}'")
        
        # Проверка конца выражения
        last = ts[-1]
        if Op.is_binary(last):
            raise ValueError(f"Нельзя заканчивать бинарным оператором '{last}'")
        if Op.is_prefix(last):
            raise ValueError(f"Нельзя заканчивать префиксным оператором '{last}'")
        if Op.is_right_paren(last):
            # Скобка в конце допустима, но проверим баланс позже
            pass
        
        # Баланс скобок и проверки соседних токенов
        balance = 0
        for i, curr in enumerate(ts):
            # Баланс скобок
            if Op.is_left_paren(curr):
                balance += 1
            elif Op.is_right_paren(curr):
                balance -= 1
                if balance < 0:
                    raise ValueError("Лишняя закрывающая скобка ')'")
            
            if i == 0:
                continue
            
            prev = ts[i-1]
            
            # Проверка: два операнда подряд
            if Op.is_operand(prev) and Op.is_operand(curr):
                raise ValueError(f"Нужен оператор между '{prev}' и '{curr}'")
            
            # Проверка: операнд и открывающая скобка
            if Op.is_operand(prev) and Op.is_left_paren(curr):
                raise ValueError(f"Нужен оператор между '{prev}' и '{curr}'")
            
            # Проверка: закрывающая скобка и открывающая скобка
            if Op.is_right_paren(prev) and Op.is_left_paren(curr):
                raise ValueError(f"Нужен оператор между '{prev}' и '{curr}'")
            
            # Проверка: закрывающая скобка и операнд
            if Op.is_right_paren(prev) and Op.is_operand(curr):
                raise ValueError(f"Нужен оператор между '{prev}' и '{curr}'")
            
            # Проверка: закрывающая скобка и префиксный оператор
            if Op.is_right_paren(prev) and Op.is_prefix(curr):
                raise ValueError(f"Нужен оператор между '{prev}' и '{curr}'")
            
            # Проверка: после постфиксного оператора не может быть открывающей скобки
            if Op.is_postfix(prev) and Op.is_left_paren(curr):
                raise ValueError(f"После постфиксного оператора '{prev}' нужен оператор, а не '('")
            
            # Проверка: после префиксного оператора должно быть выражение
            if Op.is_prefix(prev) and (Op.is_binary(curr) or Op.is_right_paren(curr) or Op.is_postfix(curr)):
                raise ValueError(f"После префиксного оператора '{prev}' нужно выражение, а не '{curr}'")
            
            # Проверка: два бинарных оператора подряд
            if Op.is_binary(prev) and Op.is_binary(curr):
                raise ValueError(f"Два бинарных оператора подряд: '{prev}' и '{curr}'")
            
            # Проверка: постфиксный оператор должен идти после операнда или скобки
            if Op.is_postfix(curr) and not (Op.is_operand(prev) or Op.is_right_paren(prev)):
                raise ValueError(f"Постфиксный оператор '{curr}' должен идти после операнда или ')'")
            
            # Проверка: префиксный оператор не может идти после операнда (нужен бинарный)
            if Op.is_prefix(curr) and Op.is_operand(prev):
                raise ValueError(f"Нужен оператор между '{prev}' и '{curr}'")
            
            # Проверка: после числа не может идти число (уже проверили), 
            # но функция должна иметь оператор перед собой
            if Op.exists(curr) and Op.is_operand(prev) and not Op.is_binary(curr):
                if not (Op.is_prefix(curr) or Op.is_postfix(curr)):
                    raise ValueError(f"Нужен оператор между '{prev}' и '{curr}'")
        
        # Финальная проверка баланса скобок
        if balance != 0:
            raise ValueError("Несбалансированные скобки")
    
    def to_rpn(self):
        """
        Преобразует инфиксное выражение в обратную польскую нотацию (RPN).
        Использует алгоритм сортировочной станции Дейкстры.
        """
        self._validate()
        output = []  # Выходная очередь
        stack = []   # Стек операторов
        
        for token in self.tokens:
            # 1. Операнд - сразу в выход
            if Op.is_operand(token):
                output.append(token)
                # Выталкиваем все префиксные операторы из стека
                while stack and Op.is_prefix(stack[-1]):
                    output.append(stack.pop())
                continue
            
            # 2. Постфиксный оператор - сразу в выход
            if Op.is_postfix(token):
                output.append(token)
                continue
            
            # 3. Префиксный оператор - в стек
            if Op.is_prefix(token):
                stack.append(token)
                continue
            
            # 4. Открывающая скобка - в стек
            if Op.is_left_paren(token):
                stack.append(token)
                continue
            
            # 5. Закрывающая скобка - выталкиваем до открывающей
            if Op.is_right_paren(token):
                while stack and not Op.is_left_paren(stack[-1]):
                    output.append(stack.pop())
                if not stack:
                    raise ValueError("Непарная скобка")
                stack.pop()  # Удаляем '('
                # Выталкиваем префиксные операторы
                while stack and Op.is_prefix(stack[-1]):
                    output.append(stack.pop())
                continue
            
            # 6. Бинарный оператор
            if Op.is_binary(token):
                current_op = Op.get(token)
                
                # Выталкиваем операторы с бОльшим или равным приоритетом
                while (stack and 
                       not Op.is_left_paren(stack[-1]) and 
                       not Op.is_prefix(stack[-1])):
                    top_op = Op.get(stack[-1])
                    if top_op:
                        # Условие выталкивания:
                        # - приоритет верхнего больше
                        # - или приоритет равен и текущий левоассоциативный
                        if (top_op.prec > current_op.prec or
                            (top_op.prec == current_op.prec and current_op.assoc == "L")):
                            output.append(stack.pop())
                        else:
                            break
                    else:
                        break
                stack.append(token)
                continue
            
            # Если дошли сюда - неизвестный токен
            raise ValueError(f"Неизвестный токен: '{token}'")
        
        # Выталкиваем все оставшиеся операторы
        while stack:
            if Op.is_left_paren(stack[-1]):
                raise ValueError("Несбалансированные скобки")
            output.append(stack.pop())
        
        # Финальная проверка: должно получиться одно значение на стеке
        depth = 0
        for token in output:
            if Op.is_operand(token):
                depth += 1
            elif Op.is_postfix(token) or Op.is_prefix(token):
                if depth < 1:
                    raise ValueError(f"Не хватает операнда для '{token}'")
                # Унарные операторы не меняют глубину (1 -> 1)
            elif Op.is_binary(token):
                if depth < 2:
                    raise ValueError(f"Не хватает операндов для '{token}'")
                depth -= 1  # Бинарный: 2 операнда -> 1 результат
            else:
                raise ValueError(f"Некорректный токен в результате: '{token}'")
        
        if depth != 1:
            raise ValueError("Выражение не сводится к одному значению")
        
        return ' '.join(output)


def interactive():
    """Интерактивный режим работы конвертера"""
    print("\n=== Инфикс → RPN ===")
    print("Введите математическое выражение или 'exit' для выхода")
    print("Поддерживаются: + - * / ^ ( ) ! ++ -- sin cos tg ctg")
    print("Унарный минус пишите как обычно: -3 или 5*(-2)")
    print("=" * 50)
    
    while True:
        try:
            expr = input("\n> ").strip()
            if expr.lower() == 'exit':
                break
            if not expr:
                continue
            
            converter = InfixToRpn(expr)
            rpn = converter.to_rpn()
            print(f"RPN: {rpn}")
            
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    interactive()