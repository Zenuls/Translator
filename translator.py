from lexer import Lexer
from parser import Parser
from code_generator import CodeGenerator

class CppToPythonTranslator:
    def __init__(self):
        self.lexer = Lexer()
        self.generator = CodeGenerator()
        self.system_messages = []  # Хранилище для системных сообщений
    
    def _add_system_message(self, message: str):
        """Добавляет системное сообщение"""
        self.system_messages.append(message)
    
    def get_system_messages(self) -> list:
        """Возвращает накопленные системные сообщения"""
        return self.system_messages.copy()
    
    def clear_system_messages(self):
        """Очищает системные сообщения"""
        self.system_messages.clear()
    
    def translate(self, cpp_code: str) -> tuple[str, list]:
        """
        Возвращает кортеж: (python_code, system_messages)
        """
        self.clear_system_messages()
        
        try:
            # Лексический анализ
            self._add_system_message("=== Лексический анализ ===")
            tokens = self.lexer.tokenize(cpp_code)
            
            # Формируем информацию о токенах для системного сообщения
            token_info = []
            for i, token in enumerate(tokens):
                token_info.append(f"{i}: {token}")
            if len(tokens) > 25:
                token_info.append(f"... (всего {len(tokens)} токенов)")
            
            self._add_system_message("\n".join(token_info))
            self._add_system_message("Лексический анализ завершен")
            
            # Синтаксический анализ
            self._add_system_message("\n=== Синтаксический анализ ===")
            parser = Parser(tokens)
            ast = parser.parse_program()
            self._add_system_message("Синтаксический анализ завершен")

            # Добавляем AST в системные сообщения
            self._add_system_message(f"AST структура:\n{ast}")
            
            # Генерация кода
            self._add_system_message("\n=== Генерация кода ===")
            python_code = self.generator.generate(ast)
            self._add_system_message("Генерация кода завершена")
            
            return python_code, self.get_system_messages()
            
        except Exception as e:
            # Без traceback, только чистое сообщение об ошибке
            error_msg = f"Ошибка трансляции: {str(e)}"
            self._add_system_message(error_msg)
            return "", self.get_system_messages()

def translate_code(source_code):
    """Функция перевода с раздельным выводом."""
    if not source_code:
        return None, "Ошибка: Исходный код пуст."
    
    translator = CppToPythonTranslator()
    python_code, system_messages = translator.translate(source_code)

    # Объединяем системные сообщения в одну строку для лога
    system_output = "\n".join(system_messages) if system_messages else "Нет системных сообщений"
    
    return python_code, system_output

def clear_all():
    """Очистка окон (возвращает сообщение для лога)."""
    return "Окна очищены."