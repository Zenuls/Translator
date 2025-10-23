from typing import List, Optional
from lexer import Token
from ast_nodes import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None

    # -------------------- Токены --------------------
    def next_token(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def expect(self, token_type: str, value: str = None) -> Token:
        if not self.current_token:
            raise SyntaxError(f"Ожидался {token_type}, но достигнут конец файла")
        if self.current_token.type == token_type and (value is None or self.current_token.value == value):
            token = self.current_token
            self.next_token()
            return token
        raise SyntaxError(f"Ожидался {token_type}, получен {self.current_token.type} в {self.current_token.line}:{self.current_token.col}")

    def match(self, token_type: str, value: str = None) -> bool:
        if self.current_token and self.current_token.type == token_type and (value is None or self.current_token.value == value):
            self.next_token()
            return True
        return False

    # -------------------- Программа --------------------
    def parse_program(self) -> Program:
        declarations = []
        while self.current_token and self.current_token.type != "EOF":
            if self.current_token.type in ["INCLUDE", "USING"]:
                self.skip_include_or_using()
            elif self.current_token.type == "CLASS":
                declarations.append(self.parse_class())
            elif self.current_token.type in ["INT", "FLOAT", "DOUBLE", "VOID", "STRING", "BOOL", "CHAR"]:  # ДОБАВЛЕНО BOOL
                declarations.append(self.parse_declaration())
            else:
                self.next_token()
        return Program(declarations)

    def skip_include_or_using(self):
        if self.current_token.type == "INCLUDE":
            self.next_token()
        elif self.current_token.type == "USING":
            self.next_token()
            if self.match("NAMESPACE") and self.match("STD"):
                self.match("DELIM", ";")

    # -------------------- Объявления --------------------
    def parse_declaration(self):
        # Тип
        decl_type = self.current_token.value
        self.next_token()

        # Обработка std::string
        if decl_type == "string" and self.current_token and self.current_token.type == "IDENT":
            name = self.current_token.value
            self.next_token()
            
            # Инициализация строки
            init_value = None
            if self.match("OP", "="):
                if self.current_token and self.current_token.type == "STRING":
                    init_value = Literal(self.current_token.value[1:-1], "string")
                    self.next_token()
                else:
                    init_value = self.parse_expression()
            
            self.expect("DELIM", ";")
            return VariableDecl(decl_type, name, init_value)

        declarations = []

        # Обрабатываем список переменных через запятую
        while True:
            # Имя
            if not self.current_token or (self.current_token.type != "IDENT" and self.current_token.type not in ["MAIN"]):
                raise SyntaxError(f"Ожидался идентификатор после типа {decl_type}")
            
            name = self.current_token.value
            self.next_token()

            # ОБРАБОТКА МАССИВОВ - ЗАМЕНА ПРОПУСКА НА РАЗБОР
            is_array = False
            array_size = None
            array_init_values = []
            
            if self.current_token and self.current_token.type == "DELIM" and self.current_token.value == "[":
                is_array = True
                self.next_token()  # пропускаем [
                
                # Размер массива
                if self.current_token and self.current_token.type in ["INT", "FLOAT"]:
                    array_size = Literal(self.current_token.value, "number")
                    self.next_token()
                
                self.expect("DELIM", "]")

            # Функция (только если не массив)
            if not is_array and self.match("DELIM", "("):
                params = self.parse_parameters()
                self.expect("DELIM", ")")
                body = self.parse_block_statement() if self.current_token and self.current_token.type == "DELIM" and self.current_token.value == "{" else Block([])
                return FunctionDecl(decl_type, name, params, body)

            # Инициализация массивов { }
            if is_array and self.match("OP", "="):
                self.expect("DELIM", "{")
                while self.current_token and not (self.current_token.type == "DELIM" and self.current_token.value == "}"):
                    if self.current_token.type == "DELIM" and self.current_token.value == ",":
                        self.next_token()
                        continue
                    array_init_values.append(self.parse_expression())
                self.expect("DELIM", "}")

            # Инициализация переменной (для не-массивов)
            init_value = None
            if not is_array and self.match("OP", "="):
                init_value = self.parse_expression()
            
            # СОЗДАЕМ СООТВЕТСТВУЮЩИЙ УЗЕЛ AST
            if is_array:
                declarations.append(ArrayDecl(decl_type, name, array_size, array_init_values))
            else:
                declarations.append(VariableDecl(decl_type, name, init_value))
            
            # Проверяем, есть ли следующая переменная
            if not self.match("DELIM", ","):
                break
        
        self.expect("DELIM", ";")
        
        # Если объявлена одна переменная, возвращаем ее, иначе возвращаем блок
        if len(declarations) == 1:
            return declarations[0]
        else:
            return Block(declarations)

    def parse_parameters(self):
        params = []
        while self.current_token and not (self.current_token.type == "DELIM" and self.current_token.value == ")"):
            if self.current_token.type in ["INT", "FLOAT", "DOUBLE", "VOID", "STRING", "BOOL", "CHAR"]:
                param_type = self.current_token.value
                self.next_token()
                if self.current_token.type != "IDENT":
                    raise SyntaxError("Ожидалось имя параметра")
                param_name = self.current_token.value
                self.next_token()
                 # Обработка значения по умолчанию
                default_value = None
                if self.match("OP", "="):
                    default_value = self.parse_expression()
                
                params.append(Parameter(param_type, param_name, default_value))
                self.match("DELIM", ",")
            else:
                break
        return params

    # -------------------- Блоки --------------------
    def parse_block_statement(self) -> Block:
        if self.match("DELIM", "{"):
            statements = []
            while self.current_token and not (self.current_token.type == "DELIM" and self.current_token.value == "}"):
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            self.expect("DELIM", "}")
            return Block(statements)
        else:
            stmt = self.parse_statement()
            return Block([stmt] if stmt else [])

    # -------------------- Операторы --------------------
    def parse_statement(self):
        if not self.current_token:
            return None

        token_type = self.current_token.type

        if token_type == "IF":
            return self.parse_if_statement()
        elif token_type == "FOR":
            return self.parse_for_statement()
        elif token_type == "WHILE":
            return self.parse_while_statement()
        elif token_type == "DO":
            return self.parse_do_while_statement()
        elif token_type == "RETURN":
            return self.parse_return_statement()
        elif token_type == "COUT":
            return self.parse_cout_statement()
        elif token_type == "CIN":
            return self.parse_cin_statement()
        elif token_type in ["INT", "FLOAT", "DOUBLE", "STRING", "BOOL", "CHAR"]:
            decl = self.parse_declaration()
            # Если declaration вернул Block (несколько переменных), нужно вернуть его как есть
            return decl
        elif token_type == "DELIM" and self.current_token.value == "{":
            return self.parse_block_statement()
        else:
            expr = self.parse_expression()
            self.match("DELIM", ";")
            return ExpressionStatement(expr)

    # -------------------- if, for, while --------------------
    def parse_if_statement(self) -> IfStatement:
        self.expect("IF")
        self.expect("DELIM", "(")
        condition = self.parse_expression()
        self.expect("DELIM", ")")
        then_branch = self.parse_block_statement()
        else_branch = self.parse_block_statement() if self.match("ELSE") else None
        return IfStatement(condition, then_branch, else_branch)

    def parse_for_statement(self) -> ForStatement:
        self.expect("FOR")
        self.expect("DELIM", "(")

        init = None
        if self.current_token.type in ["INT", "FLOAT", "DOUBLE", "BOOL", "CHAR"]:
            var_type = self.current_token.value
            self.next_token()
            if self.current_token.type != "IDENT":
                raise SyntaxError(f"Ожидался идентификатор после типа {var_type}")
            var_name = self.current_token.value
            self.next_token()
            init_value = self.parse_expression() if self.match("OP", "=") else None
            init = VariableDecl(var_type, var_name, init_value)
        elif not (self.current_token.type == "DELIM" and self.current_token.value == ";"):
            init = ExpressionStatement(self.parse_expression())
        self.expect("DELIM", ";")

        condition = self.parse_expression() if not (self.current_token.type == "DELIM" and self.current_token.value == ";") else None
        self.expect("DELIM", ";")

        increment = self.parse_expression() if not (self.current_token.type == "DELIM" and self.current_token.value == ")") else None
        self.expect("DELIM", ")")

        body = self.parse_block_statement()
        return ForStatement(init, condition, increment, body)

    def parse_while_statement(self) -> WhileStatement:
        self.expect("WHILE")
        self.expect("DELIM", "(")
        condition = self.parse_expression()
        self.expect("DELIM", ")")
        body = self.parse_block_statement()
        return WhileStatement(condition, body)

    def parse_do_while_statement(self) -> DoWhileStatement:
        self.expect("DO")
        body = self.parse_block_statement()
        self.expect("WHILE")
        self.expect("DELIM", "(")
        condition = self.parse_expression()
        self.expect("DELIM", ")")
        self.match("DELIM", ";")
        return DoWhileStatement(body, condition)

    def parse_return_statement(self) -> ReturnStatement:
        self.expect("RETURN")
        value = self.parse_expression() if self.current_token and self.current_token.type != "DELIM" else None
        self.match("DELIM", ";")
        return ReturnStatement(value)

    # -------------------- cout / cin --------------------
    def parse_cout_statement(self):
        self.expect("COUT")
        expressions = []
        
        # Обрабатываем цепочку операторов <<
        while True:
            if not self.match("OP", "<<"):
                break
                
            # Если следующий токен - endl
            if self.current_token and self.current_token.type == "ENDL":
                expressions.append(Literal("\n", "string"))
                self.next_token()
            # Если следующий токен - строка
            elif self.current_token and self.current_token.type == "STRING":
                expressions.append(Literal(self.current_token.value[1:-1], "string"))
                self.next_token()
            # Если следующий токен - символ
            elif self.current_token and self.current_token.type == "CHAR":
                char_value = self.current_token.value[1:-1]
                # Обрабатываем escape-последовательности
                if char_value == '\\n':
                    char_value = '\n'
                elif char_value == '\\t':
                    char_value = '\t'
                elif char_value == '\\r':
                    char_value = '\r'
                elif char_value == '\\\\':
                    char_value = '\\'
                elif char_value == '\\\'':
                    char_value = "'"
                elif char_value == '\\"':
                    char_value = '"'
                expressions.append(Literal(char_value, "string"))
                self.next_token()
            # Любое другое выражение
            else:
                expressions.append(self.parse_expression())
        
        self.expect("DELIM", ";")
        return CoutStatement(expressions)

    def parse_cin_statement(self):
        self.expect("CIN")
        variables = []
        while self.match("OP", ">>"):
            if self.current_token.type == "IDENT":
                variables.append(VariableReference(self.current_token.value))
                self.next_token()
        self.expect("DELIM", ";")
        return CinStatement(variables)

    # -------------------- Классы --------------------
    def parse_class(self):
        self.expect("CLASS")
        name = self.expect("IDENT").value
        self.expect("DELIM", "{")
        members = []
        while self.current_token and not (self.current_token.type == "DELIM" and self.current_token.value == "}"):
            members.append(self.parse_declaration())
        self.expect("DELIM", "}")
        self.match("DELIM", ";")
        return VariableDecl("class", name, Block(members))

    # -------------------- Выражения --------------------
    def parse_expression(self) -> ASTNode:
        return self.parse_assignment()

    def parse_assignment(self) -> ASTNode:
        """Присваивание имеет самый низкий приоритет"""
        left = self.parse_ternary()  # Следующий по приоритету - тернарный оператор
        
        if self.current_token and self.current_token.type == "OP" and self.current_token.value in ["=", "+=", "-=", "*=", "/=", "%="]:
            op = self.current_token.value
            self.next_token()
            right = self.parse_assignment()  # Правая ассоциативность
            return BinaryOperation(op, left, right)
        
        return left

    def parse_ternary(self) -> ASTNode:
        """Тернарный оператор имеет приоритет выше присваивания"""
        condition = self.parse_logical_or()
        
        if self.match("OP", "?"):
            then_expr = self.parse_expression()
            # Принимаем как OP, так и DELIM для :
            if self.match("OP", ":") or (self.current_token and self.current_token.type == "DELIM" and self.current_token.value == ":" and self.match("DELIM", ":")):
                else_expr = self.parse_ternary()
                return TernaryOperation(condition, then_expr, else_expr)
            else:
                raise SyntaxError(f"Ожидалось ':', получен {self.current_token.type} в {self.current_token.line}:{self.current_token.col}")
        
        return condition

    def parse_logical_or(self) -> ASTNode:
        """Логическое ИЛИ: ||"""
        left = self.parse_logical_and()
        while self.current_token and self.current_token.type == "OP" and self.current_token.value == "||":
            op = self.current_token.value
            self.next_token()
            right = self.parse_logical_and()
            left = BinaryOperation(op, left, right)
        return left

    def parse_logical_and(self) -> ASTNode:
        """Логическое И: &&"""
        left = self.parse_equality()
        while self.current_token and self.current_token.type == "OP" and self.current_token.value == "&&":
            op = self.current_token.value
            self.next_token()
            right = self.parse_equality()
            left = BinaryOperation(op, left, right)
        return left

    def parse_equality(self) -> ASTNode:
        left = self.parse_relational()
        while self.current_token and self.current_token.type == "OP" and self.current_token.value in ["==", "!="]:
            op = self.current_token.value
            self.next_token()
            right = self.parse_relational()
            left = BinaryOperation(op, left, right)
        return left

    def parse_relational(self) -> ASTNode:
        left = self.parse_additive()
        while self.current_token and self.current_token.type == "OP" and self.current_token.value in ["<", ">", "<=", ">="]:
            op = self.current_token.value
            self.next_token()
            right = self.parse_additive()
            left = BinaryOperation(op, left, right)
        return left

    def parse_additive(self) -> ASTNode:
        left = self.parse_multiplicative()
        while self.current_token and self.current_token.type == "OP" and self.current_token.value in ["+", "-"]:
            op = self.current_token.value
            self.next_token()
            right = self.parse_multiplicative()
            left = BinaryOperation(op, left, right)
        return left

    def parse_multiplicative(self) -> ASTNode:
        left = self.parse_unary()
        while self.current_token and self.current_token.type == "OP" and self.current_token.value in ["*", "/", "%"]:
            op = self.current_token.value
            self.next_token()
            right = self.parse_unary()
            left = BinaryOperation(op, left, right)
        return left

    def parse_unary(self) -> ASTNode:
        if self.current_token and self.current_token.type == "OP" and self.current_token.value in ["+", "-", "!", "++", "--"]:
            op = self.current_token.value
            self.next_token()
            operand = self.parse_unary()
            return UnaryOperation(op, operand)
        return self.parse_primary()

    def parse_primary(self) -> ASTNode:
        node = self.parse_primary_base()
        while self.current_token and self.current_token.type == "OP" and self.current_token.value in ["++", "--"]:
            op = self.current_token.value
            self.next_token()
            node = UnaryOperation(op, node, is_postfix=True)
        return node

    def parse_primary_base(self) -> ASTNode:
        if not self.current_token:
            raise SyntaxError("Неожиданный конец выражения")
        token = self.current_token
        if token.type == "IDENT" and token.value.startswith("std::"):
            # Преобразуем std::cout в cout и т.д.
            simple_name = token.value[5:]  # убираем "std::"
            self.next_token()
            
            # Проверяем, является ли это cout/cin/endl
            if simple_name in ["cout", "cin", "endl"]:
                if simple_name == "cout":
                    # Обрабатываем как cout statement
                    return self.parse_cout_statement()
                elif simple_name == "cin":
                    return self.parse_cin_statement()
                elif simple_name == "endl":
                    return Literal("\n", "string")
            
                # Для других случаев создаем обычную ссылку на переменную
            node = VariableReference(simple_name)
            if self.current_token and self.current_token.type == "DELIM" and self.current_token.value == "(":
                return self.parse_function_call(simple_name)
            node = self.parse_array_access(node)  # Добавляем обработку доступа к массиву
            return node
        elif token.type == "IDENT":
            self.next_token()
            node = VariableReference(token.value)
            if self.current_token and self.current_token.type == "DELIM" and self.current_token.value == "(":
                return self.parse_function_call(token.value)
            node = self.parse_array_access(node)  # Добавляем обработку доступа к массиву
            return node
        elif token.type in ["INT", "FLOAT"]:
            self.next_token()
            return Literal(token.value, "number")
        elif token.type == "STRING":
            self.next_token()
            return Literal(token.value[1:-1], "string")
        elif token.type == "CHAR":  # ДОБАВЛЕНО: обработка символьных литералов
            self.next_token()
            # Извлекаем символ из кавычек: 'A' -> A
            char_value = token.value[1:-1]
            # Обрабатываем escape-последовательности
            if char_value == '\\n':
                char_value = '\n'
            elif char_value == '\\t':
                char_value = '\t'
            elif char_value == '\\r':
                char_value = '\r'
            elif char_value == '\\\\':
                char_value = '\\'
            elif char_value == '\\\'':
                char_value = "'"
            elif char_value == '\\"':
                char_value = '"'
            return Literal(char_value, "char")
        elif token.type in ["TRUE", "FALSE"]:
            self.next_token()
            return Literal(token.type == "TRUE", "bool")
        elif token.type == "IDENT":
            self.next_token()
            if self.current_token and self.current_token.type == "DELIM" and self.current_token.value == "(":
                return self.parse_function_call(token.value)
            return VariableReference(token.value)
        
        elif token.type == "DELIM" and token.value == "(":
            self.next_token()
            expr = self.parse_expression()
            self.expect("DELIM", ")")
            expr = self.parse_array_access(expr)
            return expr
        else:
            raise SyntaxError(f"Неожиданный токен: {token.type} '{token.value}'")

    def parse_function_call(self, name: str) -> FunctionCall:
        self.expect("DELIM", "(")
        args = []
        while self.current_token and not (self.current_token.type == "DELIM" and self.current_token.value == ")"):
            if self.current_token.type == "DELIM" and self.current_token.value == ",":
                self.next_token()
                continue
            args.append(self.parse_expression())
        self.expect("DELIM", ")")
        return FunctionCall(name, args)

    def parse_array_access(self, array_node: ASTNode) -> ASTNode:
        """Обрабатывает доступ к элементам массива через []"""
        while self.current_token and self.current_token.type == "DELIM" and self.current_token.value == "[":
            self.next_token()  # Пропускаем '['
            index_expr = self.parse_expression()
            self.expect("DELIM", "]")
            array_node = ArrayAccess(array_node, index_expr)
        return array_node