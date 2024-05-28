import json
from enum import Enum


class Opcode(Enum):
    ADD: str = "add"
    SUB: str = "sub"
    MUL: str = "mul"
    DIV: str = "div"
    MOD: str = "mod"
    CMP: str = "cmp"
    JMP: str = "jmp"
    JZ: str = "jz"
    JNZ: str = "jnz"
    CALL: str = "call"
    RET: str = "ret"
    PUSH: str = "push"
    POP: str = "pop"
    LIT: str = "lit"
    HALT: str = "halt"
    INC: str = "inc"
    DEC: str = "dec"
    DUP: str = "dup"
    SWITCH: str = "switch"
    DROP: str = "drop"
    IN: str = "in"
    OUT: str = "out"

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

    def __str__(self):
        return f"name:{self.name} - addr:{self.addr} - value:{self.value}"


class MemoryCell:
    def __init__(self, address: int, opcode: Opcode = None, arg: int = None):
        self.address = address
        self.opcode = opcode
        self.arg = arg

    def __repr__(self):
        return f"address:{self.address} - opcode:{self.opcode} - arg:{self.arg}"

    def __str__(self):
        return f"address:{self.address} - opcode:{self.opcode} - arg:{self.arg}"


class MachineWord:
    index: int = None
    opcode: Opcode = None
    arg: int | list[int] = None

    def __init__(
        self, index: int, opcode: Opcode = None, arg: int | str = None
    ) -> None:
        self.index = index
        self.opcode = opcode
        self.arg = arg

    def __str__(self) -> str:
        if self.arg is not None:
            return f"opcode:{self.opcode.name} - addr:{self.index} - arg:{self.arg}"
        return f"opcode:{self.opcode.name} -  addr:{self.index}"


def write_code(code: list[MachineWord | Variable], fn: str, custom_ser) -> None:
    with open(fn, "w") as f:
        f.write(json.dumps(code, default=custom_ser, indent=1))


def read_code(source: str) -> list[MemoryCell]:
    with open(source, "r", encoding="utf-8") as f:
        code = json.load(f)

    program: list[MemoryCell] = []
    for i in code:
        if "opcode" in i and "arg" in i and i["arg"] is not None:
            program.append(MemoryCell(i["addr"], Opcode(i["opcode"]), i["arg"]))
            continue
        if "opcode" in i:
            program.append(MemoryCell(i["addr"], Opcode(i["opcode"])))
            continue
        else:
            program.append(MemoryCell(i["addr"], None, i["value"]))
    return program
