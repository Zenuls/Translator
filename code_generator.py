from ast_nodes import *

class CodeGenerator:
    def __init__(self):
        pass

    def generate(self, node, current_indent=0):
        """Главная точка входа для генерации кода из AST."""
        if node is None:
            return ""
            
        indent_str = "    " * current_indent

        if isinstance(node, Program):
            code_lines = []
            has_main_function = False
            
            # Сначала генерируем все объявления
            for decl in node.decls:
                decl_code = self.generate(decl, current_indent)
                if decl_code:
                    code_lines.append(decl_code)
                
                # Проверяем, есть ли функция main
                if isinstance(decl, FunctionDecl) and decl.name == "main":
                    has_main_function = True
            
            # Добавляем вызов main функции если она есть
            if has_main_function:
                code_lines.append("")
                code_lines.append("if __name__ == \"__main__\":")
                code_lines.append("    main()")
            
            return "\n".join(code_lines)

        elif isinstance(node, FunctionDecl):
            # Генерируем параметры с значениями по умолчанию
            params_list = []
            for param in node.params:
                if param.default_value is not None:
                    default_code = self.generate(param.default_value, current_indent)
                    params_list.append(f"{param.name}={default_code}")
                else:
                    params_list.append(param.name)
            
            params = ", ".join(params_list)
            header = f"def {node.name}({params}):"
            body_code = self.generate(node.body, current_indent + 1)
            return f"{header}\n{body_code}"

        elif isinstance(node, Block):
            if not node.statements:
                return indent_str + "pass"
            
            lines = []
            for stmt in node.statements:
                stmt_code = self.generate(stmt, current_indent)
                if stmt_code:
                    # Разбиваем на строки и добавляем правильные отступы
                    for line in stmt_code.split('\n'):
                        if line.strip():  # Непустые строки
                            # Если строка уже имеет отступ, оставляем как есть
                            if not line.startswith("    " * current_indent):
                                lines.append(indent_str + line)
                            else:
                                lines.append(line)
                        else:
                            lines.append("")  # Пустые строки
            return "\n".join(lines)
        
        elif isinstance(node, ArrayDecl):
            # Генерация кода для объявления массива
            if node.init_values:
                # Массив с инициализацией
                init_values = ", ".join(self.generate(val, current_indent) for val in node.init_values)
                return indent_str + f"{node.name} = [{init_values}]"
            else:
                # Массив без инициализации
                if node.size:
                    size = self.generate(node.size, current_indent)
                    return indent_str + f"{node.name} = [0] * {size}"
                else:
                    return indent_str + f"{node.name} = []"

        elif isinstance(node, ArrayAccess):
            array = self.generate(node.array, current_indent)
            index = self.generate(node.index, current_indent)
            return f"{array}[{index}]"


        elif isinstance(node, VariableDecl):
            if node.var_type == "string":
                if node.init_value is None:
                    return indent_str + f"{node.name} = \"\""
                else:
                    init = f" = {self.generate(node.init_value, current_indent)}"
                    return indent_str + f"{node.name}{init}"
            elif node.init_value is None:
                # Значения по умолчанию для разных типов
                if node.var_type == "char":
                    return indent_str + f"{node.name} = '\\0'"
                else:
                    return indent_str + f"{node.name} = 0"
            init = f" = {self.generate(node.init_value, current_indent)}"
            return indent_str + f"{node.name}{init}"

        elif isinstance(node, ForStatement):
            init_code = self.generate(node.init, current_indent) if node.init else ""
            cond_code = self.generate(node.condition, current_indent) if node.condition else "True"
            incr_code = self.generate(node.increment, current_indent) if node.increment else ""
            
            lines = []
            if init_code:
                lines.append(init_code)
            
            lines.append(indent_str + f"while {cond_code}:")
            
            # Тело цикла - ИСПРАВЛЕНИЕ
            body_lines = []
            for stmt in node.body.statements:
                stmt_code = self.generate(stmt, 0)  # Генерируем без отступов
                if stmt_code:
                    # Добавляем отступы к каждой строке statement
                    for line in stmt_code.split('\n'):
                        if line.strip():
                            body_lines.append("    " * (current_indent + 1) + line)
            body_code = "\n".join(body_lines) if body_lines else "    " * (current_indent + 1) + "pass"
            lines.append(body_code)
            
            # Инкремент
            if incr_code:
                lines.append("    " * (current_indent + 1) + incr_code.strip())
            
            return "\n".join(lines)

        elif isinstance(node, WhileStatement):
            cond_code = self.generate(node.condition, current_indent)
            
            lines = [indent_str + f"while {cond_code}:"]
            
            # Тело цикла
            body_lines = []
            for stmt in node.body.statements:
                stmt_code = self.generate(stmt, 0)  # Генерируем без отступов
                if stmt_code:
                    # Добавляем отступы к каждой строке statement
                    for line in stmt_code.split('\n'):
                        if line.strip():
                            body_lines.append("    " * (current_indent + 1) + line)
            body_code = "\n".join(body_lines) if body_lines else "    " * (current_indent + 1) + "pass"
            lines.append(body_code)
            
            return "\n".join(lines)

        elif isinstance(node, DoWhileStatement):
            lines = [indent_str + "while True:"]
            
            # Тело цикла
            body_lines = []
            for stmt in node.body.statements:
                stmt_code = self.generate(stmt, 0)  # Генерируем без отступов
                if stmt_code:
                    # Добавляем отступы к каждой строке statement
                    for line in stmt_code.split('\n'):
                        if line.strip():
                            body_lines.append("    " * (current_indent + 1) + line)
            body_code = "\n".join(body_lines) if body_lines else "    " * (current_indent + 1) + "pass"
            lines.append(body_code)
            
            # Условие выхода
            cond_code = self.generate(node.condition, current_indent)
            lines.append("    " * (current_indent + 1) + f"if not ({cond_code}):")
            lines.append("    " * (current_indent + 2) + "break")
            
            return "\n".join(lines)

        elif isinstance(node, IfStatement):
            cond_code = self.generate(node.condition, current_indent)
            
            lines = [indent_str + f"if {cond_code}:"]
            
            # Then ветка
            then_lines = []
            for stmt in node.then_branch.statements:
                stmt_code = self.generate(stmt, 0)  # Генерируем без отступов
                if stmt_code:
                    # Добавляем отступы к каждой строке statement
                    for line in stmt_code.split('\n'):
                        if line.strip():
                            then_lines.append("    " * (current_indent + 1) + line)
            then_code = "\n".join(then_lines) if then_lines else "    " * (current_indent + 1) + "pass"
            lines.append(then_code)
            
            # Else ветка если есть
            if node.else_branch:
                lines.append(indent_str + "else:")
                else_lines = []
                for stmt in node.else_branch.statements:
                    stmt_code = self.generate(stmt, 0)  # Генерируем без отступов
                    if stmt_code:
                        # Добавляем отступы к каждой строке statement
                        for line in stmt_code.split('\n'):
                            if line.strip():
                                else_lines.append("    " * (current_indent + 1) + line)
                else_code = "\n".join(else_lines) if else_lines else "    " * (current_indent + 1) + "pass"
                lines.append(else_code)
            
            return "\n".join(lines)

        elif isinstance(node, CoutStatement):
            parts = []
            for expr in node.expressions:
                expr_code = self.generate(expr, current_indent)
                if isinstance(expr, Literal) and expr.literal_type == "string":
                    parts.append(expr_code)
                else:
                    parts.append(f"str({expr_code})")
            
            if len(parts) == 1:
                return indent_str + f"print({parts[0]})"
            else:
                # Для вывода с пробелами между элементами
                return indent_str + f"print(' '.join([{', '.join(parts)}]))"

        elif isinstance(node, CinStatement):
            reads = []
            for v in node.variables:
                var_name = self.generate(v, current_indent)
                reads.append(indent_str + f"{var_name} = int(input())")
            return "\n".join(reads)

        elif isinstance(node, ReturnStatement):
            val = self.generate(node.value, current_indent) if node.value else ""
            return indent_str + f"return {val}"

        elif isinstance(node, ExpressionStatement):
            return self.generate(node.expr, current_indent)

        elif isinstance(node, BinaryOperation):
            left = self.generate(node.left, current_indent)
            right = self.generate(node.right, current_indent)
            
            if node.operator == '+=':
                return f"{left} += {right}"
            elif node.operator == '-=':
                return f"{left} -= {right}"
            elif node.operator == '*=':
                return f"{left} *= {right}"
            elif node.operator == '/=':
                return f"{left} //= {right}"  # Целочисленное деление
            elif node.operator == '%=':
                return f"{left} %= {right}"
            elif node.operator == '/':
                return f"{left} // {right}"  # Целочисленное деление
            elif node.operator == '%':
                return f"{left} % {right}"
            else:
                return f"{left} {node.operator} {right}"

        elif isinstance(node, UnaryOperation):
            operand = self.generate(node.operand, current_indent)
            if node.is_postfix:
                if node.operator == "++":
                    return f"{operand} += 1"
                elif node.operator == "--":
                    return f"{operand} -= 1"
            else:
                return f"({node.operator}{operand})"

        elif isinstance(node, Literal):
            if node.literal_type == "string":
                return repr(node.value)
            elif node.literal_type == "char":
                # Для символов используем одинарные кавычки в Python
                return repr(node.value)
            elif node.literal_type == "bool":
                return "True" if node.value else "False"
            return str(node.value)

        elif isinstance(node, VariableReference):
            return node.name

        elif isinstance(node, FunctionCall):
            args = ", ".join(self.generate(arg, current_indent) for arg in node.arguments)
            return f"{node.name}({args})"
        
        elif isinstance(node, TernaryOperation):
            condition = self.generate(node.condition, current_indent)
            then_expr = self.generate(node.then_expr, current_indent)
            else_expr = self.generate(node.else_expr, current_indent)
            return f"{then_expr} if {condition} else {else_expr}"

        else:
            return indent_str + f"# [UNKNOWN NODE {type(node).__name__}]"