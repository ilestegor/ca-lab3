import json
from enum import Enum


class Opcode(Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    CMP = "cmp"
    JMP = "jmp"
    JZ = "jz"
    JNZ = "jnz"
    CALL = "call"
    RET = "ret"
    PUSH = "push"
    POP = "pop"
    LIT = "lit"
    HALT = "halt"
    INC = "inc"
    DEC = "dec"

    def __str__(self):
        return str(self.value)


def command2opcode(command: str) -> Opcode:
    try:
        return Opcode[command.upper()]
    except KeyError:
        raise ValueError(f"Unknown opcode {command}")


class Variable:
    def __init__(self, name: str, addr: int, value: str | int | None):
        self.name = name
        self.addr = addr
        self.value = value
        # self.ref_add = ref_add

    def __str__(self):
        # if self.ref_add is not None:
        #     return f"name:{self.name} - addr:{self.addr} -  ref_addr:{self.ref_add} - value:{self.value}"
        return f"name:{self.name} - addr:{self.addr} - value:{self.value}"


class MemoryCell:
    def __init__(self, address: int, opcode: Opcode = None, arg: int = None):
        self.address = address
        self.opcode = opcode
        self.arg = arg

    def __str__(self):
        return f"address:{self.address} - opcode:{self.opcode} - arg:{self.arg}"


class MachineWord:
    index: int = None
    opcode: Opcode = None
    arg: int | list[int] = None

    def __init__(self, index: int, opcode: Opcode = None, arg: int | str = None) -> None:
        self.index = index
        self.opcode = opcode
        self.arg = arg

    def __str__(self) -> str:
        if self.arg is not None:
            return f"opcode:{self.opcode.name} - addr:{self.index} - arg:{self.arg}"
        return f"opcode:{self.opcode.name} -  addr:{self.index}"


def write_code(code: list[MachineWord | Variable], fn: str, custom_ser) -> None:
    with open(fn, "w") as f:
        f.write(json.dumps(code, default=custom_ser, indent=2))


def read_code(source: str) -> list[MemoryCell]:
    with open(source, "r", encoding='utf-8') as f:
        code = json.load(f)

    program: list[MemoryCell] = []
    for i in code:
        if 'opcode' in i and 'arg' in i and i['arg'] is not None:
            program.append(MemoryCell(i['addr'], Opcode(i['opcode']), i['arg']))
            continue
        if 'opcode' in i:
            program.append(MemoryCell(i['addr'], Opcode(i['opcode'])))
            continue
        else:
            program.append(MemoryCell(i['addr'], None, i['value']))
    return program
