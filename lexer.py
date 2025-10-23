from dataclasses import dataclass
from typing import List, Set
import re

@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', {self.line}:{self.col})"

class Lexer:
    def __init__(self):
        self.tokens: List[Token] = []
        self.symbol_table: Set[str] = set()
        
        # Регулярные выражения для токенов
        self.patterns = [
            ('INCLUDE', r'#include\s*[<"][^>"]*[>"]'),
            ('WHITESPACE', r'[ \t\r]+'),
            ('NEWLINE', r'\n'),
            ('COMMENT', r'//[^\n]*|/\*.*?\*/'),
            ('STRING', r'"(?:\\.|[^"\\])*"'),
            ('CHAR', r"'(?:\\.|[^'\\])*'"),
            ('NUMBER', r'\d+\.\d*|\.\d+|\d+'),
            ('QUALIFIED_IDENT', r'std::[a-zA-Z_][a-zA-Z0-9_]*'),
            ('IDENT', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('OPERATOR', r'<<=|>>=|\.\.\.|\+\+|--|->|&&|\|\||<<|>>|<=|>=|==|!=|\+=|-=|\*=|\/=|%=|&=|\|=|\^=|<<=|>>=|[+\-*/%&|^<>=!?~.]'),  # ДОБАВЛЕНА ТОЧКА
            ('DELIMITER', r'[(){}\[\];,:]'),
        ]
        
        # Ключевые слова C++
        self.keywords = {
            'if', 'else', 'for', 'while', 'do', 'break', 'continue', 'return',
            'switch', 'case', 'default', 'class', 'public', 'private', 'protected',
            'int', 'float', 'double', 'char', 'bool', 'void', 'const', 'new', 'delete',
            'try', 'catch', 'throw', 'using', 'namespace', 'std', 'string', 'vector', 'list',
            'true', 'false', 'auto', 'include', 'cin', 'cout', 'endl'
        }
        
        self.token_re = re.compile(
            '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.patterns),
            re.DOTALL
        )

    def tokenize(self, source: str) -> List[Token]:
        self.tokens = []
        line = 1
        col = 1
        pos = 0
        
        while pos < len(source):
            # Пропускаем пробелы
            if source[pos] in ' \t\r':
                col += 1
                pos += 1
                continue
                
            # Обработка новой строки
            if source[pos] == '\n':
                line += 1
                col = 1
                pos += 1
                continue
            
            # Ищем совпадение с регулярными выражениями
            match = self.token_re.match(source, pos)
            if not match:
                raise SyntaxError(f"Неизвестный символ '{source[pos]}' в строке {line}:{col}")
            
            token_type = match.lastgroup
            token_value = match.group(token_type)
            
            if token_type == 'WHITESPACE':
                col += len(token_value)
                pos = match.end()
                continue
                
            elif token_type == 'NEWLINE':
                line += 1
                col = 1
                pos = match.end()
                continue
                
            elif token_type == 'COMMENT':
                # Пропускаем комментарии
                newlines = token_value.count('\n')
                if newlines:
                    line += newlines
                    col = 1
                else:
                    col += len(token_value)
                pos = match.end()
                continue
                
            elif token_type == 'INCLUDE':
                self.tokens.append(Token('INCLUDE', token_value, line, col))
                col += len(token_value)
                pos = match.end()
                continue
                
            elif token_type == 'STRING':
                self.tokens.append(Token('STRING', token_value, line, col))
                col += len(token_value)
                pos = match.end()
                continue
                
            elif token_type == 'CHAR':
                self.tokens.append(Token('CHAR', token_value, line, col))
                col += len(token_value)
                pos = match.end()
                continue
                
            elif token_type == 'NUMBER':
                if '.' in token_value:
                    self.tokens.append(Token('FLOAT', token_value, line, col))
                else:
                    self.tokens.append(Token('INT', token_value, line, col))
                col += len(token_value)
                pos = match.end()
                continue
                
            elif token_type == 'QUALIFIED_IDENT':
                # Обрабатываем квалифицированные имена типа std::cout
                if token_value in ['std::cout', 'std::cin', 'std::endl', 'std::string']:
                    # Извлекаем имя без std::
                    simple_name = token_value.split('::')[1]
                    self.tokens.append(Token(simple_name.upper(), simple_name, line, col))
                else:
                    self.symbol_table.add(token_value)
                    self.tokens.append(Token('IDENT', token_value, line, col))
                col += len(token_value)
                pos = match.end()
                continue
                
            elif token_type == 'IDENT':
                if token_value in self.keywords:
                    self.tokens.append(Token(token_value.upper(), token_value, line, col))
                else:
                    self.symbol_table.add(token_value)
                    self.tokens.append(Token('IDENT', token_value, line, col))
                col += len(token_value)
                pos = match.end()
                continue
                
            elif token_type == 'OPERATOR':
                self.tokens.append(Token('OP', token_value, line, col))
                col += len(token_value)
                pos = match.end()
                continue
                
            elif token_type == 'DELIMITER':
                self.tokens.append(Token('DELIM', token_value, line, col))
                col += len(token_value)
                pos = match.end()
                continue
                
            else:
                pos = match.end()
        
        self.tokens.append(Token('EOF', '', line, col))
        return self.tokens