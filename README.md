# Basic Stack Machine

- Глотов Егор Дмитриевич, P3232
- `alg -> asm | stack | neum | hw | tick -> instr | struct | stream | port | pstr | prob2 | cache`
- Упрощенный вариант - `asm | stack | neum | hw | instr | struct | stream | port | pstr | prob2 | -`

## [Язык программирования](#язык-программирования)

``` ebnf
program ::= section_data "\n" section_text

section_text ::= "section .text:" [comment] "\n" {command}

section_data ::= "section .data:" [comment] "\n" {data}

data ::= var comment

var ::= variable_name ":" var_value
 
var_value ::= number
             | string
             | variable_name

command_section ::= label [comment] | command 

command ::= op0 [comment] | op1 [comment]

label ::= "." label_name ":\n\t"

op0 ::= add 
        | sub
        | mul
        | div
        | mod
        | push
        | pop
        | inc
        | dec
        | ret
        | cmp

op1 ::= call label_name
        | in positive_number
        | out positive_number 
        | lit var_name
        | lit "[" var_name "]"
        | lit number

lowercase_letter ::= [A-Z]
uppercase_letter ::= [a-z]

digit ::= [0-9]
positive_number ::= <any digit except: 0> {digit}
negative_number ::= ["-"] positive_number
number ::= positibe_number | negative_number 
string = "\"[\w\s,.:;!?()\\-]+\""
label_name ::= lowercase_letter | uppercase_letter {lowercase_letter} | {uppercase_letter} | {number}
var_name ::= lowercase_letter | uppercase_letter {lowercase_letter} | {uppercase_letter} | {number}
comment ::= ";" {<any symbol except "\n">}
```

Команды:

- `add` - сложение двух значений на верхушке стека, результат кладется на верхушку стека `[a, b] -> [b + a]`
- `sub` - разность двух значений с верхушки стека, результат кладется на верхушку стека `[a. b] -> [b - a]`

## [Организация памяти](#организация-памяти)

## [Система команд](#система-команд)

## [Транслятор](#транслятор)

## [Модель процессора](#модель-процессора)

## [Тестирование](#тестирование)