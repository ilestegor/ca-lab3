import re
import sys

from isa import Opcode, MachineWord, write_code, Variable, command2opcode


class Program:
    def __init__(self):
        self.machine_code: list[MachineWord | Variable] = []
        self.current_command_addr = 0
        self.variables: dict[str, Variable] = {}
        self.labels: dict[str, int] = {}

    def add_instruction(self, index: int, opcode: Opcode, arg: int | list[int]):
        self.machine_code.append(MachineWord(index, opcode, arg))


def remove_indent(src_code: str) -> list[str]:
    src_code = src_code.splitlines()
    src_code = [x.strip() for x in src_code]
    return src_code


def remove_comments(src_code: str) -> str:
    return re.sub(r';.*', '', src_code)


def clean_code(src_code: str) -> list[str]:
    src_code = remove_comments(src_code)
    src_code = remove_indent(src_code)
    src_code = [x for x in src_code if x != ""]
    return src_code


def is_variable_exist(program: Program, variable: str) -> bool:
    for i in program.variables:
        if i == variable:
            return True
    return False


def get_variable_by_name(program: Program, name: str) -> Variable:
    for i in program.variables:
        if i == name:
            return program.variables[i]


def get_label_addr_by_name(program: Program, name: str) -> int | None:
    for i in program.labels:
        if i == name:
            return program.labels[i]
    else:
        raise ValueError(f"Syntax error: Label {name} was not defined")


def is_number(s: str) -> bool:
    return bool(re.match(r'^[+-]?\d*\.?\d+$', s))


def is_variable(s: str) -> bool:
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', s))


def is_string(s: str) -> bool:
    return bool(re.match(r'"[><\w\s,.:;!?()\\-]+"', s))


def is_malloc_request(s: str) -> bool:
    return bool(re.match(r'^bf', s))


def translate_section_data(data_block: list[str], program: Program) -> None:
    program.machine_code.append(Variable("start_address", program.current_command_addr, None))
    program.current_command_addr += 1
    for data in data_block:
        decl = [x.strip() for x in data.split(":", 1)]
        var_name = decl[0]
        var_value = decl[1]
        if is_variable_exist(program, var_name):
            raise ValueError(f"Variable {var_name} is already defined")
        else:
            if is_malloc_request(var_value):
                arg = [x.strip() for x in var_value.split(" ")][1]
                if is_number(arg):
                    program.variables[var_name] = Variable(var_name, program.current_command_addr, arg)
                    for i in range(int(arg)):
                        program.machine_code.append(Variable(var_name, program.current_command_addr, 0))
                        program.current_command_addr += 1
                    continue
                else:
                    raise ValueError(f"Syntax error: Variable {var_name} must be number")

            if is_number(var_value):
                program.variables[var_name] = Variable(var_name, program.current_command_addr, int(var_value))
                program.machine_code.append(Variable(var_name, program.current_command_addr, int(var_value)))
                program.current_command_addr += 1
            elif is_variable(var_value):
                if is_variable_exist(program, var_value):
                    var: Variable = get_variable_by_name(program, var_value)
                    program.variables[var_name] = Variable(var_name, program.current_command_addr, var.addr)
                    program.machine_code.append(Variable(var_name, program.current_command_addr, var.addr))
                    program.current_command_addr += 1
                else:
                    raise ValueError(f"Variable {var_value} is not defined to be referenced")
            elif is_string(var_value):
                transformed_string = [ord(x) for x in var_value]
                transformed_string.insert(0, len(transformed_string) - 2)
                program.variables[var_name] = Variable(var_name, program.current_command_addr, transformed_string[0])
                program.machine_code.append(Variable(var_name, program.current_command_addr, transformed_string[0]))
                transformed_string.pop(0)
                transformed_string.remove(34)
                transformed_string.remove(34)
                program.current_command_addr += 1
                for i in transformed_string:
                    program.machine_code.append(Variable(var_name, program.current_command_addr, i))
                    program.current_command_addr += 1
            else:
                raise ValueError(f"Unexpected variable {var_value}")


def is_label(s: str) -> bool:
    return bool(re.match(r'\..*:', s))


def is_indirect(s: str) -> bool:
    return bool(re.match(r'\[[a-zA-Z_][a-zA-Z0-9_]*]', s))


def get_variable_addr(var: Variable, program: Program) -> MachineWord | Variable | None:
    for i in program.variables:
        if program.variables[i].addr == var.value:
            return program.variables[i]


def translate_section_text(command_block: list[str], program: Program) -> None:
    for i in command_block:
        if is_label(i):
            program.labels[i.strip()[:-1]] = program.current_command_addr
            continue

        command_and_arg = i.strip().split(" ")
        if len(command_and_arg) == 2:
            opcode = command2opcode(command_and_arg[0])
            if opcode in {Opcode.JMP, Opcode.JZ, Opcode.JNZ, Opcode.CALL}:
                program.machine_code.append((MachineWord(program.current_command_addr, opcode, command_and_arg[1])))
                program.current_command_addr += 1
                continue
            if is_number(command_and_arg[1]):
                program.machine_code.append(
                    (MachineWord(program.current_command_addr, opcode, int(command_and_arg[1]))))
                program.current_command_addr += 1
                continue
            program.machine_code.append((MachineWord(program.current_command_addr, opcode, command_and_arg[1])))
            program.current_command_addr += 1
        elif len(command_and_arg) == 1 and command_and_arg[0] != "":
            program.machine_code.append(
                MachineWord(program.current_command_addr, command2opcode(command_and_arg[0])))
            program.current_command_addr += 1


def resolve_addresses(program: Program):
    for i in range(len(program.machine_code)):
        if isinstance(program.machine_code[i], MachineWord) and program.machine_code[i].arg is not None and \
                program.machine_code[i].arg in program.labels:
            label_addr = get_label_addr_by_name(program, str(program.machine_code[i].arg))
            program.machine_code[i].arg = label_addr
            continue
        if isinstance(program.machine_code[i], MachineWord) and program.machine_code[i].arg is not None and \
                program.machine_code[i].arg in program.variables:
            var = get_variable_by_name(program, str(program.machine_code[i].arg))
            program.machine_code[i].arg = var.addr
            continue
        if isinstance(program.machine_code[i], MachineWord) and program.machine_code[i].arg is not None and \
                is_indirect(str(program.machine_code[i].arg)):
            var = program.machine_code[i].arg[1:-1]
            if var in program.variables:
                indirect_variable = get_variable_addr(program.variables[var], program)
                if indirect_variable is not None:
                    program.machine_code[i].arg = indirect_variable.value
                else:
                    raise ValueError(f"Variable {var} is not defined to be referenced")
        elif (isinstance(program.machine_code[i], MachineWord) and program.machine_code[i].arg
              is not None and not is_number(str(program.machine_code[i].arg))):
            raise ValueError(f"Variable or label <{program.machine_code[i].arg}> is not defined")

    for i in program.machine_code:
        if isinstance(i, MachineWord):
            program.machine_code[0].value = i.index
            break


def translate(src_code: str):
    program = Program()
    src_code = clean_code(src_code)
    # translate section data

    section_data_index_start = [x for x in range(len(src_code)) if src_code[x] == "section .data:"]
    assert len(section_data_index_start) == 1, "Translation error: data section not found or is in multiple places"
    section_text_start_index = [x for x in range(len(src_code)) if src_code[x] == "section .text:"]
    assert len(section_text_start_index) == 1, "Translation error: text section not found or is in multiple places"

    data_block = src_code[section_data_index_start[0] + 1:section_text_start_index[0]]
    commands_block = src_code[section_text_start_index[0] + 1:len(src_code) + 1]

    translate_section_data(data_block, program)
    translate_section_text(commands_block, program)
    resolve_addresses(program)

    return program.machine_code, abs(len(program.variables) - len(program.machine_code))


def custom_serializer(obj: Variable | MachineWord):
    if isinstance(obj, Variable):
        return {'addr': obj.addr, 'value': obj.value}
    if isinstance(obj, MachineWord):
        if obj.arg is not None:
            return {'opcode': obj.opcode.value, 'addr': obj.index, 'arg': obj.arg}
        return {'opcode': obj.opcode.value, 'addr': obj.index}


def main(source: str, target: str) -> None:
    with open(source, encoding="utf-8") as f:
        src = f.read()

    s, instr = translate(src)

    write_code(s, target, custom_serializer)
    print(f"source LoC: {len(src.splitlines())} code instr: {instr - 1}")


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Usage: python main.py <source_file> <target_file>"
    _, source_code, target_file = sys.argv
    main(source_code, target_file)
