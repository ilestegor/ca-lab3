# Basic Stack Machine
- Глотов Егор Дмитриевич, P3232
- `alg -> asm | stack | neum | hw | tick -> instr | struct | stream | port | pstr | prob2 | cache`
- Базовый вариант

## [Язык программирования](#язык-программирования)

``` ebnf
program ::= {function}
type ::= 'int' | 'string'
expression ::= "(" expression ")" | expression operators expression | positivie_number | negative_number

variable_name ::= lowercase_letter | uppercase_letter {lowercase_letter}
assign ::= [type] variable_name "=" value | [type] variable_name "=" read | read_char
comp_expression ::= expression comparison_operators expression
declaration ::= type variable_name
while ::= "while" "(" comp_expression ")" "{" statement "}"
if ::= "if" "(" comp_expression ")" "{" statement "}" [ "else" "{" statemnet "}" ]
statement ::= declaration | assign | while | if | io | jump | call
jump ::= "return" value
call ::= variable_name"(" {declaration} ")"
function ::= "function" type varibale_name"(" {declaration} ")" "{" statement "}"

read ::= "input()"
read_char ::= "input_char()"
print_string ::= "print(" variable_name ")"
print_int ::= "print_int(" variable_name ")"
print_char ::= "print_char(" variable_name ")"

io ::= read | read_char | print_string | print_int | print_char

lowercase_letter ::= [A-Z]
uppercase_letter ::= [a-z]

digit ::= [0-9]
positive_number ::= <any digit except: 0> {digit}
negative_number ::= ["-"] positive_number
number ::= positibe_number | negative_number
value ::= number | variable_name
operators ::= "*" | "/" | "+" | "-" | "%" |
comparison_operators ::= "==" | "<" | ">" | ">=" | "<=" | "!=" 
```
## [Организация памяти](#организация-памяти)
## [Система команд](#система-команд)
## [Транслятор](#транслятор)
## [Модель процессора](#модель-процессора)
## [Тестирование](#тестирование)