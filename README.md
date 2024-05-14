# Basic Stack Machine
- Глотов Егор Дмитриевич, P3232
- `alg -> asm | stack | neum | hw | tick -> instr | struct | stream | port | pstr | prob2 | cache`
- Базовый вариант

## [Язык программирования](#язык-программирования)

``` ebnf
program ::= {function} | {assign} | {call}

expression ::= "(" expression ")" | expression operators expression | positivie_number | negative_number

variable_name ::= lowercase_letter | uppercase_letter {lowercase_letter}
assign ::= "let" variable_name "=" expression | read | read_char | value
comp_expression ::= expression comparison_operators expression
declaration ::= "let" variable_name
while ::= "while" "(" comp_expression ")" "{" statement "}"
if ::= "if" "(" comp_expression ")" "{" statement "}" [ "else" "{" statemnet "}" ]
statement ::= declaration | assign | while | if | io | jump | call
jump ::= "return" value
call ::= variable_name"(" {variable_name} ")"
function ::= "function" varibale_name"(" {variable_name} ")" "{" statement "}"

read ::= "input()"
print_string ::= "print(" variable_name ")"
print_int ::= "print_int(" variable_name ")"
print_char ::= "print_char(" variable_name ")"

io ::= read | print_string | print_int | print_char

lowercase_letter ::= [A-Z]
uppercase_letter ::= [a-z]

digit ::= [0-9]
positive_number ::= <any digit except: 0> {digit}
negative_number ::= ["-"] positive_number
number ::= positibe_number | negative_number
value ::= number | variable_name
operators ::= "*" | "/" | "+" | "-" | "%" |
comparison_operators ::= "==" | "<" | ">" | ">=" | "<=" | "!=" 
string = "\"[\w\s,.:;!?()\\-]+\""
```
## [Организация памяти](#организация-памяти)
## [Система команд](#система-команд)
## [Транслятор](#транслятор)
## [Модель процессора](#модель-процессора)
## [Тестирование](#тестирование)