from __future__ import annotations

import json
from enum import Enum

import exception


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
        raise exception.OpcodeError(command) from exception


class Variable:
    def __init__(self, name: str, addr: int, value: str | int | None):
        self.name = name
        self.addr = addr
        self.value = value

    def __str__(self):
        return f"name:{self.name} - addr:{self.addr} - value:{self.value}"


class MemoryCell:
    def __init__(self, address: int, opcode: Opcode | None = None, arg: int | None = None):
        self.address = address
        self.opcode = opcode
        self.arg = arg

    def __repr__(self):
        return f"address:{self.address} - opcode:{self.opcode} - arg:{self.arg}"

    def __str__(self):
        return f"address:{self.address} - opcode:{self.opcode} - arg:{self.arg}"


class MachineWord:
    index: int | None = None
    opcode: Opcode
    arg: int | list[int] | None = None

    def __init__(self, index: int, opcode: Opcode, arg: int | list[int] | str | None = None) -> None:
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
    with open(source, encoding="utf-8") as f:
        code = json.load(f)

    program: list[MemoryCell] = []
    for i in code:
        if "opcode" in i and "arg" in i and i["arg"] is not None:
            program.append(MemoryCell(i["addr"], Opcode(i["opcode"]), i["arg"]))
            continue
        if "opcode" in i:
            program.append(MemoryCell(i["addr"], Opcode(i["opcode"])))
            continue
        program.append(MemoryCell(i["addr"], None, i["value"]))
    return program
