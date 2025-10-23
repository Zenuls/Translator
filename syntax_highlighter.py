import tkinter as tk
import re

class SyntaxHighlighter:
    def __init__(self):
        # Ключевые слова C++
        self.cpp_keywords = {
            'if', 'else', 'for', 'while', 'do', 'break', 'continue', 'return',
            'switch', 'case', 'default', 'class', 'public', 'private', 'protected',
            'int', 'float', 'double', 'char', 'bool', 'void', 'const', 'new', 'delete',
            'try', 'catch', 'throw', 'using', 'namespace', 'std', 'string', 'vector', 'list',
            'true', 'false', 'auto', 'include', 'cin', 'cout', 'endl', 'main'
        }
        
        # Ключевые слова Python
        self.python_keywords = {
            'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'break', 'continue',
            'return', 'import', 'from', 'as', 'try', 'except', 'finally', 'raise',
            'and', 'or', 'not', 'is', 'in', 'with', 'yield', 'lambda', 'pass',
            'True', 'False', 'None', 'self', 'print', 'input', 'int', 'str', 'bool'
        }
        
        # Цвета для подсветки
        self.colors = {
            'keyword': '#ff79c6',      # розовый
            'string': '#f1fa8c',       # желтый
            'comment': '#6272a4',      # серо-синий
            'number': '#bd93f9',       # фиолетовый
            'function': '#50fa7b',     # зеленый
            'operator': '#ff5555',     # красный
            'preprocessor': '#ffb86c', # оранжевый
            'default': '#f8f8f2'       # белый
        }

    def highlight_cpp(self, text_widget):
        """Подсветка синтаксиса C++"""
        # Удаляем предыдущие теги
        for tag in text_widget.tag_names():
            text_widget.tag_delete(tag)
        
        content = text_widget.get("1.0", tk.END)
        
        # Регулярные выражения для C++
        patterns = [
            (r'#include\s*[<"][^>"]*[>"]', 'preprocessor'),
            (r'//.*?$', 'comment'),
            (r'/\*.*?\*/', 'comment'),
            (r'"(?:\\.|[^"\\])*"', 'string'),
            (r"'(?:\\.|[^'\\])*'", 'string'),
            (r'\b\d+\.\d*\b|\b\.\d+\b|\b\d+\b', 'number'),
            (r'\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()', 'function'),
            (r'[+\-*/%=&|^<>!]=?|&&|\|\||<<|>>|::|->', 'operator'),
        ]
        
        # Добавляем ключевые слова
        keyword_pattern = r'\b(' + '|'.join(re.escape(kw) for kw in self.cpp_keywords) + r')\b'
        patterns.insert(0, (keyword_pattern, 'keyword'))
        
        # Применяем подсветку
        for pattern, tag_name in patterns:
            matches = list(re.finditer(pattern, content, re.MULTILINE | re.DOTALL))
            for match in matches:
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                text_widget.tag_add(tag_name, start, end)
                text_widget.tag_config(tag_name, foreground=self.colors.get(tag_name, self.colors['default']))

    def highlight_python(self, text_widget):
        """Подсветка синтаксиса Python"""
        # Удаляем предыдущие теги
        for tag in text_widget.tag_names():
            text_widget.tag_delete(tag)
        
        content = text_widget.get("1.0", tk.END)
        
        # Регулярные выражения для Python
        patterns = [
            (r'#.*?$', 'comment'),
            (r'""".*?"""', 'comment'),
            (r"'''.*?'''", 'comment'),
            (r'"(?:\\.|[^"\\])*"', 'string'),
            (r"'(?:\\.|[^'\\])*'", 'string'),
            (r'\b\d+\.\d*\b|\b\.\d+\b|\b\d+\b', 'number'),
            (r'\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)', 'function'),
            (r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)', 'function'),
            (r'[+\-*/%=&|^<>!]=?|//|==|!=|<=|>=|and|or|not|is|in', 'operator'),
        ]
        
        # Добавляем ключевые слова
        keyword_pattern = r'\b(' + '|'.join(re.escape(kw) for kw in self.python_keywords) + r')\b'
        patterns.insert(0, (keyword_pattern, 'keyword'))
        
        # Применяем подсветку
        for pattern, tag_name in patterns:
            matches = list(re.finditer(pattern, content, re.MULTILINE | re.DOTALL))
            for match in matches:
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                text_widget.tag_add(tag_name, start, end)
                text_widget.tag_config(tag_name, foreground=self.colors.get(tag_name, self.colors['default']))

    def auto_highlight(self, text_widget, language):
        """Автоматическая подсветка в зависимости от языка"""
        if language == "cpp":
            self.highlight_cpp(text_widget)
        elif language == "python":
            self.highlight_python(text_widget)