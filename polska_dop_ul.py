import math
import re
from enum import Enum
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from collections import deque

# ==================== КОНСТАНТЫ И НАСТРОЙКИ ====================

SUPPORTED_FUNCTIONS = {
    'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
    'sinh', 'cosh', 'tanh', 'exp', 'log', 'log10',
    'sqrt', 'cbrt', 'abs', 'ceil', 'floor', 'round'
}

SUPPORTED_CONSTANTS = {
    'pi': math.pi,
    'e': math.e
}


class TokenType(Enum):
    """Типы токенов"""
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    FUNCTION = "FUNCTION"
    CONSTANT = "CONSTANT"
    OPERATOR = "OPERATOR"
    UNARY_OPERATOR = "UNARY_OPERATOR"
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    COMMA = "COMMA"
    FACTORIAL = "FACTORIAL"
    INCREMENT = "INCREMENT"
    DECREMENT = "DECREMENT"
    INVALID = "INVALID"


@dataclass
class Token:
    """Структура токена"""
    value: str
    type: TokenType
    precedence: int = 0
    right_associative: bool = False
    is_binary: bool = True
    
    def is_operator(self) -> bool:
        return self.type in (TokenType.OPERATOR, TokenType.UNARY_OPERATOR)
    
    def is_operand(self) -> bool:
        return self.type in (TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.CONSTANT)


# ==================== СТЕК ====================

class Stack:
    """Реализация стека"""
    def __init__(self):
        self._data = []
    
    def push(self, value):
        self._data.append(value)
    
    def pop(self):
        if self.empty():
            raise IndexError("Stack is empty")
        return self._data.pop()
    
    def peek(self):
        if self.empty():
            raise IndexError("Stack is empty")
        return self._data[-1]
    
    def empty(self) -> bool:
        return len(self._data) == 0
    
    def size(self) -> int:
        return len(self._data)
    
    def clear(self):
        self._data.clear()


# ==================== ЛЕКСИЧЕСКИЙ АНАЛИЗАТОР ====================

class Lexer:
    """Лексический анализатор: разбивает строку на токены"""
    
    def __init__(self, expression: str):
        self.input = expression
        self.position = 0
        self.error = ""
        self.tokens: List[Token] = []
    
    def _peek(self, offset: int = 0) -> str:
        """Просмотр символа без извлечения"""
        pos = self.position + offset
        if pos >= len(self.input):
            return '\0'
        return self.input[pos]
    
    def _advance(self) -> str:
        """Извлечение символа"""
        if self.position >= len(self.input):
            return '\0'
        ch = self.input[self.position]
        self.position += 1
        return ch
    
    def _skip_whitespace(self):
        """Пропуск пробельных символов"""
        while self.position < len(self.input) and self._peek().isspace():
            self._advance()
    
    def _read_number(self) -> Token:
        """Чтение числа (поддерживает целые, дробные, экспоненциальную запись)"""
        number = []
        
        # Обработка знака
        if self._peek() == '-':
            number.append(self._advance())
        
        has_dot = False
        
        while self.position < len(self.input):
            ch = self._peek()
            if ch.isdigit():
                number.append(self._advance())
            elif ch == '.':
                if has_dot:
                    self.error = "Multiple decimal points in number"
                    return Token("".join(number) + '.', TokenType.INVALID)
                has_dot = True
                number.append(self._advance())
            elif ch.lower() == 'e':
                number.append(self._advance())
                if self._peek() in ('+', '-'):
                    number.append(self._advance())
            else:
                break
        
        num_str = "".join(number)
        
        # Проверка корректности
        if not num_str or num_str == '-' or num_str.endswith('e') or \
           num_str.endswith('E') or num_str.endswith('+') or num_str.endswith('-'):
            self.error = "Invalid number format"
            return Token(num_str, TokenType.INVALID)
        
        return Token(num_str, TokenType.NUMBER)
    
    def _read_identifier(self) -> Token:
        """Чтение идентификатора (функция, константа, переменная)"""
        identifier = [self._advance()]
        
        while self.position < len(self.input):
            ch = self._peek()
            if ch.isalnum() or ch == '_':
                identifier.append(self._advance())
            else:
                break
        
        ident = "".join(identifier)
        
        # Проверка на операторы
        if ident in ('++', '--'):
            return Token(ident, 
                        TokenType.INCREMENT if ident == '++' else TokenType.DECREMENT,
                        precedence=4, right_associative=False, is_binary=False)
        
        if ident == '!':
            return Token(ident, TokenType.FACTORIAL, precedence=4, 
                        right_associative=False, is_binary=False)
        
        # Проверка на функцию
        if ident in SUPPORTED_FUNCTIONS:
            return Token(ident, TokenType.FUNCTION)
        
        # Проверка на константу
        if ident in SUPPORTED_CONSTANTS:
            return Token(ident, TokenType.CONSTANT)
        
        # Иначе это идентификатор (переменная)
        return Token(ident, TokenType.IDENTIFIER)
    
    def _read_operator(self) -> Token:
        """Чтение оператора"""
        ch = self._advance()
        op = ch
        
        # Проверка на двухсимвольный оператор
        if self.position < len(self.input):
            two_char = op + self._peek()
            if two_char in ('++', '--'):
                self._advance()
                return Token(two_char,
                            TokenType.INCREMENT if two_char == '++' else TokenType.DECREMENT,
                            precedence=4, right_associative=False, is_binary=False)
        
        # Определение типа оператора
        if ch in ('+', '-'):
            # Определяем, унарный это оператор или бинарный
            if not self.tokens or \
               self.tokens[-1].type in (TokenType.LEFT_PAREN, TokenType.OPERATOR,
                                        TokenType.UNARY_OPERATOR, TokenType.COMMA,
                                        TokenType.FUNCTION):
                return Token(op, TokenType.UNARY_OPERATOR, precedence=3,
                           right_associative=False, is_binary=False)
            return Token(op, TokenType.OPERATOR, precedence=1,
                        right_associative=False, is_binary=True)
        
        elif ch in ('*', '/'):
            return Token(op, TokenType.OPERATOR, precedence=2,
                        right_associative=False, is_binary=True)
        
        elif ch == '^':
            return Token(op, TokenType.OPERATOR, precedence=3,
                        right_associative=True, is_binary=True)
        
        elif ch == '!':
            return Token(op, TokenType.FACTORIAL, precedence=4,
                        right_associative=False, is_binary=False)
        
        elif ch == '(':
            return Token(op, TokenType.LEFT_PAREN)
        
        elif ch == ')':
            return Token(op, TokenType.RIGHT_PAREN)
        
        elif ch == ',':
            return Token(op, TokenType.COMMA)
        
        else:
            self.error = f"Unknown operator: {ch}"
            return Token(op, TokenType.INVALID)
    
    def tokenize(self) -> List[Token]:
        """Разбивает выражение на токены"""
        self.tokens.clear()
        self.error = ""
        
        while self.position < len(self.input):
            self._skip_whitespace()
            if self.position >= len(self.input):
                break
            
            ch = self._peek()
            
            # Определение типа токена
            if ch.isdigit() or (ch == '-' and self._peek(1).isdigit()):
                # Проверка на оператор минус или число
                if self.tokens and (self.tokens[-1].is_operand() or 
                                   self.tokens[-1].type in (TokenType.RIGHT_PAREN,
                                                            TokenType.FACTORIAL,
                                                            TokenType.INCREMENT,
                                                            TokenType.DECREMENT)):
                    token = self._read_operator()
                else:
                    token = self._read_number()
            elif ch.isalpha() or ch == '_':
                token = self._read_identifier()
            elif ch == '.' and self._peek(1).isdigit():
                token = self._read_number()
            else:
                token = self._read_operator()
            
            if token.type == TokenType.INVALID:
                if not self.error:
                    self.error = "Invalid token"
                return [token]
            
            self.tokens.append(token)
        
        return self.tokens
    
    def get_error(self) -> str:
        return self.error


# ==================== СИНТАКСИЧЕСКИЙ АНАЛИЗАТОР ====================

class Parser:
    """Синтаксический анализатор: проверяет корректность выражения"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.error = ""
    
    def _peek(self) -> Optional[Token]:
        """Просмотр текущего токена"""
        if self.current >= len(self.tokens):
            return None
        return self.tokens[self.current]
    
    def _advance(self) -> Optional[Token]:
        """Переход к следующему токену"""
        token = self._peek()
        if token:
            self.current += 1
        return token
    
    def _match(self, *types: TokenType) -> bool:
        """Проверка соответствия типа токена"""
        token = self._peek()
        if token and token.type in types:
            self._advance()
            return True
        return False
    
    def _check(self, *types: TokenType) -> bool:
        """Проверка типа без извлечения"""
        token = self._peek()
        return token is not None and token.type in types
    
    def _error(self, msg: str):
        """Запись ошибки"""
        if not self.error:
            self.error = msg
    
    # ========== Парсер грамматики ==========
    
    def parse_expression(self) -> bool:
        """Expression → Term { '+' Term | '-' Term }"""
        if not self.parse_term():
            return False
        
        while self._check(TokenType.OPERATOR) and self._peek().value in ('+', '-'):
            self._advance()
            if not self.parse_term():
                return False
        
        return True
    
    def parse_term(self) -> bool:
        """Term → Factor { '*' Factor | '/' Factor }"""
        if not self.parse_factor():
            return False
        
        while self._check(TokenType.OPERATOR) and self._peek().value in ('*', '/'):
            self._advance()
            if not self.parse_factor():
                return False
        
        return True
    
    def parse_factor(self) -> bool:
        """Factor → Power { '^' Power }"""
        if not self.parse_power():
            return False
        
        while self._check(TokenType.OPERATOR) and self._peek().value == '^':
            self._advance()
            if not self.parse_power():
                return False
        
        return True
    
    def parse_power(self) -> bool:
        """Power → Unary { '!' | '++' | '--' }"""
        if not self.parse_unary():
            return False
        
        while self._check(TokenType.FACTORIAL, TokenType.INCREMENT, TokenType.DECREMENT):
            self._advance()
        
        return True
    
    def parse_unary(self) -> bool:
        """Unary → [ '+' | '-' | '++' | '--' ] Primary"""
        if self._check(TokenType.UNARY_OPERATOR) and self._peek().value in ('+', '-'):
            self._advance()
            return self.parse_primary()
        elif self._check(TokenType.INCREMENT, TokenType.DECREMENT):
            self._advance()
            return self.parse_primary()
        elif not self.parse_primary():
            return False
        
        if self._check(TokenType.INCREMENT, TokenType.DECREMENT):
            self._advance()
        
        return True
    
    def parse_primary(self) -> bool:
        """Primary → NUMBER | IDENTIFIER | CONSTANT |
                      FUNCTION '(' Expression { ',' Expression } ')' |
                      '(' Expression ')'"""
        if self._match(TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.CONSTANT):
            return True
        
        elif self._check(TokenType.FUNCTION):
            self._advance()
            
            if not self._match(TokenType.LEFT_PAREN):
                self._error("Expected '(' after function name")
                return False
            
            if not self._match(TokenType.RIGHT_PAREN):
                if not self.parse_expression():
                    return False
                
                while self._match(TokenType.COMMA):
                    if not self.parse_expression():
                        return False
                
                if not self._match(TokenType.RIGHT_PAREN):
                    self._error("Expected ')' after function arguments")
                    return False
            
            return True
        
        elif self._match(TokenType.LEFT_PAREN):
            if not self.parse_expression():
                return False
            
            if not self._match(TokenType.RIGHT_PAREN):
                self._error("Expected ')'")
                return False
            
            return True
        
        else:
            token = self._peek()
            self._error(f"Unexpected token: {token.value if token else 'EOF'}")
            return False
    
    def parse(self) -> bool:
        """Основной метод парсинга"""
        if not self.tokens:
            self._error("Empty expression")
            return False
        
        if not self.parse_expression():
            return False
        
        if self.current < len(self.tokens):
            self._error("Unexpected tokens at end of expression")
            return False
        
        return True
    
    def get_error(self) -> str:
        return self.error


# ==================== КОНВЕРТЕР В RPN ====================

class RPNConverter:
    """Преобразование инфиксной записи в обратную польскую (алгоритм Дейкстры)"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
    
    def convert(self) -> Tuple[str, str]:
        """Конвертирует в RPN. Возвращает (RPN, отладочная информация)"""
        op_stack = Stack()
        output: List[Token] = []
        
        for token in self.tokens:
            if token.is_operand():
                # Операнды сразу в выходную очередь
                output.append(token)
            
            elif token.type == TokenType.FUNCTION:
                op_stack.push(token)
            
            elif token.type == TokenType.LEFT_PAREN:
                op_stack.push(token)
            
            elif token.type == TokenType.RIGHT_PAREN:
                # Выталкиваем до левой скобки
                found_left_paren = False
                while not op_stack.empty():
                    top = op_stack.pop()
                    if top.type == TokenType.LEFT_PAREN:
                        found_left_paren = True
                        # Если сверху функция, выталкиваем её
                        if not op_stack.empty() and op_stack.peek().type == TokenType.FUNCTION:
                            output.append(op_stack.pop())
                        break
                    else:
                        output.append(top)
                
                if not found_left_paren:
                    return "", "Error: Mismatched parentheses"
            
            elif token.type == TokenType.COMMA:
                # Выталкиваем до левой скобки
                while not op_stack.empty() and op_stack.peek().type != TokenType.LEFT_PAREN:
                    output.append(op_stack.pop())
                
                if op_stack.empty():
                    return "", "Error: Mismatched parentheses or misplaced comma"
            
            elif token.is_operator():
                # Операторы выталкиваются согласно приоритету
                while not op_stack.empty() and op_stack.peek().is_operator():
                    top = op_stack.peek()
                    if ((not token.right_associative and token.precedence <= top.precedence) or
                        (token.right_associative and token.precedence < top.precedence)):
                        output.append(op_stack.pop())
                    else:
                        break
                op_stack.push(token)
            
            elif token.type in (TokenType.FACTORIAL, TokenType.INCREMENT, TokenType.DECREMENT):
                # Постфиксные операторы сразу в выходную очередь
                output.append(token)
            
            else:
                return "", f"Error: Invalid token in expression: {token.value}"
        
        # Выталкиваем оставшиеся операторы
        while not op_stack.empty():
            top = op_stack.pop()
            if top.type == TokenType.LEFT_PAREN:
                return "", "Error: Mismatched parentheses"
            output.append(top)
        
        # Форматируем результат
        rpn_parts = []
        debug_parts = []
        
        for token in output:
            rpn_parts.append(token.value)
            
            # Отладочная информация
            type_map = {
                TokenType.NUMBER: "NUM",
                TokenType.FUNCTION: "FUNC",
                TokenType.CONSTANT: "CONST",
                TokenType.IDENTIFIER: "VAR",
                TokenType.OPERATOR: "OP",
                TokenType.UNARY_OPERATOR: "UNARY",
                TokenType.FACTORIAL: "FACT",
                TokenType.INCREMENT: "INC",
                TokenType.DECREMENT: "DEC"
            }
            debug_parts.append(f"[{type_map.get(token.type, '?')}:{token.value}]")
        
        return " ".join(rpn_parts), " ".join(debug_parts)


# ==================== ОСНОВНАЯ ПРОГРАММА ====================

def main():
    """Основная функция программы"""
    debug = False
    history: List[str] = []
    
    print("=" * 60)
    print("RPN Converter v1.4 (Python version)")
    print("=" * 60)
    print("\nCommands:")
    print("  stop    ->  Stop the program")
    print("  debug   ->  Toggle debug mode")
    print("  history ->  Show conversion history")
    print("\nSupported operators:   + - * / ^ ! ++ --")
    print(f"Supported functions:   {' '.join(SUPPORTED_FUNCTIONS)}")
    print(f"Supported constants:   {' '.join(SUPPORTED_CONSTANTS.keys())}")
    print("\nNOTE: Functions work only with brackets!")
    print("Example: sin(10)  ->  10 sin")
    print("         sin 10   ->  Will throw an error!")
    print("=" * 60)
    print()
    
    while True:
        try:
            user_input = input(" > ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "stop":
                print("Goodbye!")
                break
            
            elif user_input.lower() == "debug":
                debug = not debug
                print(f"Debug {'ON' if debug else 'OFF'}\n")
                continue
            
            elif user_input.lower() == "history":
                if not history:
                    print("No history yet.\n")
                else:
                    print("\n--- History ---")
                    for i, expr in enumerate(history[-10:], 1):  # Показываем последние 10
                        print(f"{i}. {expr}")
                    print()
                continue
            
            # Лексический анализ
            lexer = Lexer(user_input)
            tokens = lexer.tokenize()
            
            if tokens and tokens[0].type == TokenType.INVALID:
                print(f"Lexical Error: {lexer.get_error()}\n")
                continue
            
            # Синтаксический анализ
            parser = Parser(tokens)
            if not parser.parse():
                print(f"Syntax Error: {parser.get_error()}\n")
                continue
            
            # Преобразование в RPN
            converter = RPNConverter(tokens)
            rpn, debug_info = converter.convert()
            
            if not rpn:
                print(f"Conversion Error: {debug_info}\n")
            else:
                print(f"RPN: {rpn}")
                if debug:
                    print(f"Debug: {debug_info}")
                    print(f"Tokens: {[(t.value, t.type.name) for t in tokens]}")
                print()
                
                # Сохраняем в историю
                history.append(f"{user_input} -> {rpn}")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Runtime Error: {e}\n")


if __name__ == "__main__":
    main()