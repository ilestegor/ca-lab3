from __future__ import annotations
import re
from enum import Enum
from utils.exceptions import NotValidSyntaxException

class Token(Enum):
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
    VAR = r"[a-zA-Z][a-zA-Z]*"
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

# Возвращает массив токенов из нашего кода
def parse_to_tokens(source: str) -> list[tuple[Token, str]]:
    regex = "|".join(f"(?P<{t.name}>{t.value})" for t in Token)
    found_tokens = re.finditer(regex, source)
    tokens: list[tuple[Token, str]] = []
    for token in found_tokens:
        t_type: str = token.lastgroup
        t_value: str = token.group(t_type)
        if t_type == "STRING":
            tokens.append((Token[t_type], t_value[1:-1].replace("\\n", "\n")))
        else:
            tokens.append((Token[t_type], t_value))
    return tokens

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
    NEQ = "neq"
    ASSIGN = "assign"
    VAR = "var"


# return ast type by token type
def map_token_2_type(token: Token) -> ASTType:
    ast_types: dict[Token, ASTType] = {
         getattr(Token, node_type.name): node_type for node_type in ASTType if hasattr(Token, node_type.name)
    }
    return ast_types[token]
    

# parse to ast simple "let s = 2"
class ASTNode:
    def __init__(self, ast_type: ASTType, value: str = ""):
        self.astType = ast_type
        self.children: list[ASTNode] = []
        self.value = value

    def __str__(self) -> str:
        return f"{self.astType} => {self.value}"

    @classmethod
    def from_token(cls, token: Token, value: str = "") -> ASTNode:
        return cls(map_token_2_type(token), value)

    def add_child(self, node: ASTNode) -> None:
        self.children.append(node)


def at(tokens: list[tuple[Token, str]]) -> Token:
    return tokens[0]

def shift(tokens: list[tuple[Token, str]]):
    if (len(tokens) <= 0):
        raise NotValidSyntaxException("Syntax not valid")
    else:    
        tokens.pop(0)

        


def parse_primary_expr(tokens: list[tuple[Token, str]]):
    cur_token = at(tokens)
    if (cur_token[0] == Token.VAR):
        tk =  ASTNode(map_token_2_type(cur_token[0]), cur_token[1])
        tokens.pop(0)
        return tk
    if (cur_token[0] == Token.NUMBER):
        tk = ASTNode(map_token_2_type(cur_token[0]), cur_token[1])
        tokens.pop(0)
        return tk
    if (cur_token[0] == Token.LPAREN):
        tokens.pop(0)
        value = parse_expr(tokens)
        shift(tokens)
        return value
    else:
        print("UNEXPECTED TOKEN")

def parse_additive_expr(tokens: list[tuple[Token, str]]):

    left = parse_multiplicative_expr(tokens)

    while tokens and (tokens[0][1] == "+" or tokens[0][1] == "-"):
        operator = ASTNode(map_token_2_type(tokens[0][0]), tokens[0][1])
        tokens.pop(0)
        right = parse_multiplicative_expr(tokens)
        operator.add_child(left)
        operator.add_child(right)
        left = operator
    return left

def parse_multiplicative_expr(tokens: list[tuple[Token, str]]):

    left = parse_primary_expr(tokens)

    while  tokens and (tokens[0][1] == "*" or tokens[0][1] == "/"):
        operator = ASTNode(map_token_2_type(tokens[0][0]), tokens[0][1])
        tokens.pop(0)
        right = parse_primary_expr(tokens)
        operator.add_child(left)
        operator.add_child(right)
        left = operator
    return left

def parse_declaration(tokens: list[tuple[Token, str]]):
    
    node: ASTNode = ASTNode.from_token(Token.LET)
    shift(tokens)
    node.add_child(ASTNode.from_token(Token.VAR, tokens[0][1]))
    shift(tokens)
    shift(tokens)
    node.add_child(parse_expr(tokens))
    return node

def parse_expr(tokens: list[tuple[Token, str]]):
    return parse_additive_expr(tokens)


def parse_stmt(tokens: list[tuple[Token, str]]):
    if (tokens[0][0] == Token.LET):
        return parse_declaration(tokens)
    return parse_expr(tokens)


def produce_ast(tokenized_source: list[tuple[Token, str]]) -> ASTNode:
    node: ASTNode = ASTNode(ASTType.ROOT)

    # tokenized_source[0][0] = Token.type
    # tokenized_source[0][1] = value of token from source code 
    while tokenized_source:
        nod = parse_stmt(tokenized_source)
        node.add_child(nod)
    return node

prog = "let s = 3"
ast = produce_ast(parse_to_tokens(prog))
print(parse_to_tokens(prog))
print(ast.astType)

counting = 1
def prints(count):
    for i in ast.children:
        print("-"*count, f"{i.astType} {i.value}")
        if (len(i.children) != 0):
            ast.children = i.children
            count += 1
            prints(count)
            count -=1
prints(counting)