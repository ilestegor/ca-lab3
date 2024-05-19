from enum import Enum
import json


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

    def __str__(self):
        return str(self.value)


def command2opcode(command: str) -> Opcode:
    try:
        return Opcode[command.upper()]
    except KeyError:
        raise ValueError(f"Unknown opcode {command}")


class Variable:
    def __init__(self, name: str, addr: int, value: str | int, ref_add: int = None):
        self.name = name
        self.addr = addr
        self.value = value
        # self.ref_add = ref_add

    def __str__(self):
        # if self.ref_add is not None:
        #     return f"name:{self.name} - addr:{self.addr} -  ref_addr:{self.ref_add} - value:{self.value}"
        return f"name:{self.name} - addr:{self.addr} - value:{self.value}"




class MachineWord:
    index: int = None
    opcode: Opcode = None
    arg: int | list[int] = None

    def __init__(self, index: int, opcode: Opcode, arg: int | str = None) -> None:
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


def read_code():
    pass
