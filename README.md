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
        | halt
        | dup
        | switch
        | drop
        | push
        | pop
        | inc
        | dec
        | ret
        | cmp

op1 ::= call label
        | in positive_number
        | out positive_number 
        | lit var_name
        | lit number
        | jmp label
        | jz label
        | jnz label
        

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

|    Команда     |                                                          Описание                                                          |
|:--------------:|:--------------------------------------------------------------------------------------------------------------------------:|
|     `add`      |           Сложение двух чисел на верхушке стека, результат кладется на верхушку стека данных `[a, b] -> [b + a]`           |
|     `sub`      |           Разность двух чисел на верхушке стека, результат кладется на верхушку стека данных `[a, b] -> [b - a]`           |
|     `mul`      |         Произведение двух чисел на верхушке стека, результа кладется на верхушку стека данных `[a, b] -> [b * a]`          |
|     `div`      |     Целочисленное деление двух чисел с верхушки стека, результат кладется на верхушку стека данных `[a, b] -> [b / a]`     |
|     `mod`      |      Остаток от деления двух чисел с верхушки стека, результат кладется на верхушку стека данных `[a, b] -> [b % a]`       |
|     `cmp`      |   Сравнение двух значений с верхушки стека данных, установка `z_flag` по результату сравнения `[a, b] -> [a, b], z_flag`   |
|     `inc`      |                     Увеличение на единицу значения, лежащего на верхушке стека данных `[a] -> [a + 1]`                     |
|     `dec`      |                     Уменьшение на единицу значения, лежащего на верхушке стека данных `[a] -> [a - 1]`                     |
|     `dup`      |                          Дублирование значения, лежащего на верхушке стека данных `[a] -> [a, a]`                          |
|    `switch`    |                          Поменять местами два верхних значения на стеке данных `[a, b] -> [b, a]`                          |
|     `drop`     |                                          Удалить значение с верхушки стека данных                                          |
|     `push`     | Поместить вместо значения, лежащего на верхушке стека данных, значение взятое из памяти по адресу из верхушки стека данных |
|     `pop`      |        Взять адрес с верхушки стека данных и записать в память следующее значение со стека данных по взятому адресу        |
|  `call label`  |                                           Вызов подпрограммы по указанной метке                                            |
|     `ret`      |                                                  Возврат из подпрограммы                                                   |
| `lit var_name` |                                Загрузка на верхушку стека данных адрес указанной переменной                                |
|  `lit number`  |                                     Загрузка указанного числа на верхушку стека данных                                     |
|  `jmp label`   |                                        Безусловный переход на адрес указанной метки                                        |
|   `jz label`   |                               Условный переход на адрес указанной метки (если `z_flag` == 0)                               |
|  `jnz label`   |                                  Условный переход на адрес указанной (если `z_flag` != 0)                                  |
|     `halt`     |                                                     Останов программы                                                      |


## [Организация памяти](#организация-памяти)

## [Система команд](#система-команд)

## [Транслятор](#транслятор)

## [Модель процессора](#модель-процессора)

## [Тестирование](#тестирование)