from __future__ import annotations

import re
from enum import Enum


class Token:
    class TokenType(Enum):
        NUMBER = r"-?[0-9]+"
        STRING = r'"[\w\s,.:;!?()\\-]+"'
        READ = r"input"
        READ_CHAR = r"read_char"
        PRINT_INT = r"print_int"
        PRINT_CHAR = r"print_char"
        PRINT_STRING = r"print"
        LET = r"let"
        FUNC = r"function"
        RET = r"return"
        IF = r"if"
        WHILE = r"while"
        ELSE = r"else"
        VAR = r"[a-zA-Z]+[0-9]*[a-zA-Z]*"
        LPAREN = r"\("
        RPAREN = r"\)"
        LBRACE = r"\{"
        RBRACE = r"\}"
        ASSIGN = r"="
        EQUALS = r"=="
        LOWER = r"<"
        GREATER = r">"
        GE = r">="
        LE = r"<="
        NEQ = r"!="
        MUL = r"\*"
        DIV = r"/"
        PLUS = r"\+"
        SUB = r"-"
        MOD = r"%"

    def __init__(self, t_type: Token.TokenType, t_value: str):
        self.type = t_type
        self.value = t_value

    @classmethod
    def construct_token(cls, token_type: Token.TokenType, t_value: str) -> Token:
        return cls(token_type, t_value)


class Lexer:
    tokenized = []

    def __init__(self, source: str) -> None:
        self.src = source

    # Возвращает массив токенов из нашего кода
    def parse_to_tokens(self):
        regex = "|".join(f"(?P<{t.name}>{t.value})" for t in Token.TokenType)
        found_tokens = re.finditer(regex, self.src)
        tokens: list[Token] = []
        for token in found_tokens:
            t_type: str = token.lastgroup
            t_value: str = token.group(t_type)
            if t_type == "STRING":
                tokens.append(Token.construct_token(Token.TokenType[t_type], t_value[1:-1].replace("\\n", "\n")))
            else:
                tokens.append(Token.construct_token(Token.TokenType[t_type], t_value))
        self.tokenized = tokens


class ASTType(Enum):
    NUMBER = "number"
    STRING = "string"
    READ = "input"
    READ_CHAR = "read_char"
    PRINT_INT = "print_int"
    PRINT_CHAR = "print_char"
    print_string = "print_string"
    LET = "let"
    FUNC = "function"
    RET = "return"
    IF = "if"
    WHILE = "while"
    ELSE = "else"
    ROOT = "root"
    MOD = "mod"
    SUB = "sub"
    PLUS = "plus"
    DIV = "div"
    MUL = "mul"
    ASSIGN = "assign"
    VAR = "var"
    ARGS = "args"
    BLOCK = "block"
    CALL = "func_call"
    CONDITION = "condition"
    GREATER = "greater"
    LOWER = "lower"
    GE = "ge"
    LE = "le"
    EQ = "eq"
    NEQ = "neq"


def map_token_2_type(token: Token.TokenType) -> ASTType:
    ast_types: dict[Token.TokenType, ASTType] = {
        getattr(Token.TokenType, node_type.name): node_type for node_type in ASTType if
        hasattr(Token.TokenType, node_type.name)
    }
    return ast_types[token]


class ASTNode:
    def __init__(self, ast_type: ASTType, value: str = ""):
        self.astType = ast_type
        self.children: list[ASTNode] = []
        self.value = value

    def __str__(self) -> str:
        return f"{self.astType} => {self.value}"

    @classmethod
    def from_token(cls, token: Token.TokenType, value: str = "") -> ASTNode:
        return cls(map_token_2_type(token), value)

    @classmethod
    def create_ast_node(cls, token: ASTType, value: str | list) -> ASTNode:
        return cls(token, value)

    def add_child(self, node: ASTNode) -> None:
        self.children.append(node)


class Parser:
    def __init__(self, tokenized_source):
        self.tokenized_source = tokenized_source
        self.ast_source = []

    @classmethod
    def at(cls, tokens):
        return tokens[0]

    @classmethod
    def shift(cls, tokens):
        tokens.pop(0)

    def parse_primary_expr(self, tokens):
        cur_token = self.at(tokens)
        if cur_token.type == Token.TokenType.VAR:
            tk = ASTNode(map_token_2_type(cur_token.type), cur_token.value)
            self.shift(tokens)
            return tk
        if cur_token.type == Token.TokenType.NUMBER:
            tk = ASTNode(map_token_2_type(cur_token.type), cur_token.value)
            self.shift(tokens)
            return tk
        if cur_token.type == Token.TokenType.LPAREN:
            self.shift(tokens)
            value = self.parse_expr(tokens)
            self.shift(tokens)
            return value
        if cur_token.type == Token.TokenType.STRING:
            tk = ASTNode(map_token_2_type(cur_token.type), cur_token.value)
            self.shift(tokens)
            return tk
        else:
            print("UNEXPECTED TOKEN")
            exit(1)

    def parse_additive_expr(self, tokens):
        left = self.parse_multiplicative_expr(tokens)

        while tokens and (tokens[0].value == "+" or tokens[0].value == "-"):
            operator = ASTNode(map_token_2_type(tokens[0].type), tokens[0].value)
            self.shift(tokens)
            right = self.parse_multiplicative_expr(tokens)
            operator.add_child(left)
            operator.add_child(right)
            left = operator
        return left

    def parse_multiplicative_expr(self, tokens):
        left = self.parse_primary_expr(tokens)

        while tokens and (tokens[0].value == "*" or tokens[0].value == "/" or tokens[0].value == "%"):
            operator = ASTNode(map_token_2_type(tokens[0].type), tokens[0].value)
            self.shift(tokens)
            right = self.parse_primary_expr(tokens)
            operator.add_child(left)
            operator.add_child(right)
            left = operator
        return left

    def parse_expr(self, tokens):
        return self.parse_assignment_expr(tokens)

    def parse_assignment_declaration_operand(self, tokens, node):
        if tokens[0].type == Token.TokenType.READ:
            right = self.parse_function_call(tokens)
            right.astType = ASTType.READ
            node.add_child(right)
            return node, True
        if tokens[0].type == Token.TokenType.VAR and len(tokens) > 1 and tokens[1].value == '(':
            node.add_child(self.parse_function_call(tokens))
            return node, True
        return node, False



    def parse_declaration(self, tokens):
        node: ASTNode = ASTNode.from_token(Token.TokenType.LET)
        self.shift(tokens)
        node.add_child(ASTNode.from_token(Token.TokenType.VAR, tokens[0].value))
        self.shift(tokens)
        self.shift(tokens)
        node, is_complete = self.parse_assignment_declaration_operand(tokens, node)
        if not is_complete:
            node.add_child(self.parse_expr(tokens))
        return node

    def parse_assignment_expr(self, tokens):
        left = self.parse_additive_expr(tokens)

        if tokens and (tokens[0].type == Token.TokenType.ASSIGN):
            operator = ASTNode.from_token(tokens[0].type, tokens[0].value)
            self.shift(tokens)
            node, is_complete = self.parse_assignment_declaration_operand(tokens, operator)
            operator = node
            if not is_complete:
                right = self.parse_assignment_expr(tokens)
                operator.add_child(left)
                operator.add_child(right)
                return operator
            operator.add_child(left)
            return operator
        return left

    def parse_stmt(self, tokens):
        if tokens[0].type == Token.TokenType.LET:
            return self.parse_declaration(tokens)
        if tokens[0].type == Token.TokenType.FUNC:
            return self.parse_function_declaration(tokens)
        if tokens[0].type == Token.TokenType.VAR and tokens[1].value == "(":
            return self.parse_function_call(tokens)
        if tokens[0].type == Token.TokenType.IF:
            return self.parse_if_while_expression(tokens)
        if tokens[0].type == Token.TokenType.WHILE:
            return self.parse_if_while_expression(tokens)
        return self.parse_expr(tokens)

    def parse_if_while_expression(self, tokens):
        token_type = tokens[0].type
        node = ASTNode.from_token(Token.TokenType.WHILE, tokens[0].value)
        self.shift(tokens)
        condition_node = ASTNode.create_ast_node(ASTType.CONDITION, ASTType.CONDITION.value)
        condition = self.parse_comparison_expression(tokens)
        condition_node.add_child(condition)
        node.add_child(condition_node)
        self.shift(tokens)
        block = self.parse_block(tokens)
        node.add_child(block)
        if token_type == Token.TokenType.IF:
            if len(tokens) != 0:
                if tokens[0].type == Token.TokenType.ELSE:
                    else_node = ASTNode.from_token(Token.TokenType.ELSE, tokens[0].value)
                    self.shift(tokens)
                    self.shift(tokens)
                    else_block = self.parse_block(tokens)
                    else_node.add_child(else_block)
                    node.add_child(else_node)
        return node

    def parse_comparison_expression(self, tokens):
        self.shift(tokens)
        left = self.parse_additive_expr(tokens)
        operator = ASTNode.from_token(tokens[0].type, tokens[0].value)
        self.shift(tokens)
        right = self.parse_additive_expr(tokens)
        self.shift(tokens)
        operator.add_child(left)
        operator.add_child(right)
        return operator

    def parse_args(self, tokens):
        self.shift(tokens)
        parameters = []
        while tokens and (tokens[0].value != ')'):
            parameters.append(tokens[0].value)
            self.shift(tokens)
        self.shift(tokens)
        return parameters

    # parsing block inside the if/while/function statements
    def parse_block(self, tokens):
        block_body = ASTNode.create_ast_node(ASTType.BLOCK, ASTType.BLOCK.value)
        while tokens and (tokens[0].type != Token.TokenType.RBRACE):
            block_body.add_child(self.parse_stmt(tokens))
        self.shift(tokens)
        return block_body

    def parse_function_declaration(self, tokens):
        function_node = ASTNode.from_token(Token.TokenType.FUNC, tokens[0].value)
        self.shift(tokens)
        function_name = ASTNode.from_token(Token.TokenType.VAR, tokens[0].value)
        self.shift(tokens)
        function_node.add_child(function_name)
        parameters = ASTNode.create_ast_node(ASTType.ARGS, self.parse_args(tokens))
        function_node.add_child(parameters)
        self.shift(tokens)
        function_node.add_child(self.parse_block(tokens))
        return function_node

    def produce_ast(self):
        node: ASTNode = ASTNode(ASTType.ROOT)

        while self.tokenized_source:
            nod = self.parse_stmt(self.tokenized_source)
            node.add_child(nod)
        self.ast_source = node

    def parse_function_call(self, tokens):
        call_node = ASTNode.create_ast_node(ASTType.CALL, ASTType.CALL.value)
        call_node.add_child(ASTNode.from_token(Token.TokenType.VAR, tokens[0].value))
        self.shift(tokens)
        params = ASTNode.create_ast_node(ASTType.ARGS, self.parse_args(tokens))
        call_node.add_child(params)
        return call_node


prog = '''
    function s(x, y){
        if (a > b){
            a = a + b
            while (b < a){
                s = s + b
            }
        }
    }
    let x = 1
    let y = "32"
    s(x, y)
'''

s = Lexer(prog)
s.parse_to_tokens()

asts = Parser(s.tokenized)
asts.produce_ast()
ast = asts.ast_source
print(ast)
counting = 1


def prints(count):
    for i in ast.children:
        print("-" * count, f"{i.astType} {i.value}")
        if len(i.children) != 0:
            ast.children = i.children
            count += 1
            prints(count)
            count -= 1


prints(counting)

# p = parse(prog)
# k = json.dumps(p, indent=4)
# print(k)
