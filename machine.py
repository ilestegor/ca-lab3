import logging
import sys
import unicodedata
from dataclasses import dataclass
from typing import Callable

from constants import MEMORY_SIZE, DATA_STACK_SIZE, ADDRESS_STACK_SIZE, INSTRUCTIONS_LIMIT
from exception import HaltProgramException
from isa import Opcode, read_code, MemoryCell

AVAILABLE_ALU_BIN_OPERATIONS: dict[Opcode, Callable] = {
    Opcode.ADD: lambda x, y: int(x + y),
    Opcode.SUB: lambda x, y: int(x - y),
    Opcode.MUL: lambda x, y: int(x * y),
    Opcode.DIV: lambda x, y: int(x / y),
    Opcode.MOD: lambda x, y: int(x % y),
    Opcode.CMP: lambda x, y: int(x - y),
}

AVAILABLE_ALU_UNARY_OPERATIONS: dict[Opcode, Callable] = {
    Opcode.INC: lambda x: int(x + 1),
    Opcode.DEC: lambda x: int(x - 1),
}


class Alu:
    z_flag = 0

    def calculate(self, left: int, right: int, opcode: Opcode) -> int:
        assert (
            opcode in AVAILABLE_ALU_BIN_OPERATIONS
            or opcode in AVAILABLE_ALU_UNARY_OPERATIONS
        ), f"Unknown alu operation code: {opcode}"
        if opcode in AVAILABLE_ALU_BIN_OPERATIONS:
            alu_op_handler = AVAILABLE_ALU_BIN_OPERATIONS[opcode]
            calculated_value = alu_op_handler(left, right)
            self.set_flags(calculated_value)
            return calculated_value
        if opcode in AVAILABLE_ALU_UNARY_OPERATIONS:
            alu_op_handler = AVAILABLE_ALU_UNARY_OPERATIONS[opcode]
            calculated_value = alu_op_handler(left)
            self.set_flags(calculated_value)
            return calculated_value

    def set_flags(self, value: int):
        if value == 0:
            self.z_flag = 0
        else:
            self.z_flag = 1


@dataclass(frozen=True)
class Port:
    value: int


STDIN: Port = Port(0)
STDOUT: Port = Port(1)


class IO:
    def __init__(self, ports: dict[Port, list[int]]):
        self.ports: dict[Port, list[int]] = ports

    def read(self, port: Port):
        assert port in self.ports, f"Undefined port {port}"
        value = self.ports[port].pop(0)

        if unicodedata.category(chr(value)) in [
            "Cc",
            "Cf",
            "Cs",
            "Co",
            "Cn",
            "Zl",
            "Zp",
        ]:
            logging.debug("IN: %s\n", value)
            return value
        logging.debug("IN: %s - %s\n", value, chr(value))
        return value

    def write(self, port: Port, value: int):
        assert port in self.ports, f"Undefined port {port.value}"
        self.ports[port].append(value)
        try:
            logging.debug(
                " OUT: %s << %s - %s\n",
                "".join([chr(x) for x in self.ports[STDOUT]]),
                value,
                chr(value),
            )
        except ValueError:
            logging.debug(" OUT: %s\n", self.ports[STDOUT])


class DataPath:
    alu: Alu = None

    data_stack: list | None = None

    address_stack: list | None = None

    data_stack_size: int | None = None

    data_tos_reg_1: int = None

    data_tos_reg_2: int = None

    address_tos_reg_1: int = None

    address_stack_size: int | None = None

    pc: int = None

    mem_size: int = None

    memory: list = None

    io: IO = None

    def __init__(self, memory: list[MemoryCell], io: IO):
        self.data_stack = []
        self.data_tos_reg_1 = 0
        self.data_tos_reg_2 = 0
        self.data_stack_size = DATA_STACK_SIZE
        self.address_stack_size = ADDRESS_STACK_SIZE
        self.address_stack = []
        self.address_tos_reg_1 = 0
        self.pc = 0
        self.io = io
        self.alu = Alu()

        self.memory = [0] * MEMORY_SIZE
        for i in range(len(memory)):
            self.memory[i] = memory[i]
        self.mem_size = MEMORY_SIZE

    def signal_latch_pc(self, value: int):
        self.pc = value

    def signal_read_mem(self, addr: int) -> MemoryCell:
        assert (
            addr < self.mem_size
        ), f"Memory read fault, cell with address - {addr} does not exist"
        return self.memory[addr]

    def signal_write_mem(self, addr: int, value: int) -> None:
        assert (
            addr < self.mem_size
        ), f"Memory write fault, cell with address - {addr} does not exist"
        self.memory[addr] = MemoryCell(addr, None, value)

    def signal_latch_data_stack_reg_1(self, value: int) -> None:
        self.data_tos_reg_1 = value

    def signal_latch_data_stack_reg_2(self, value: int) -> None:
        self.data_tos_reg_2 = value

    def signal_write_data_stack(self, value: int) -> None:
        assert len(self.data_stack) != self.data_stack_size, "Data stack is overflowed"
        self.data_stack.append(value)

    def signal_read_data_stack(self) -> int:
        assert len(self.data_stack) > 0, "Data stack is empty"
        return self.data_stack.pop()

    def signal_read_top_of_address_stack(self) -> int:
        assert len(self.address_stack) > 0, "Address stack is empty"
        return self.address_stack.pop()

    def signal_latch_top_address_stack(self, value: int) -> None:
        self.address_tos_reg_1 = value

    def signal_write_top_address_stack(self, value: int) -> None:
        assert (
            len(self.address_stack) != self.address_stack_size
        ), "Address stack is overflowed"
        self.address_stack.append(value)


class ControlUnit:
    datapath: DataPath = None

    ticks: int = None

    cur_instruction: Opcode = None

    cur_operand: int = None

    executors: dict[Opcode, Callable] = None

    def __init__(self, datapath: DataPath):
        self.datapath = datapath
        self.ticks = 0

        self.executors = {
            Opcode.LIT: self.execute_lit,
            Opcode.ADD: self.execute_binary_alu_operation,
            Opcode.PUSH: self.execute_push,
            Opcode.MUL: self.execute_binary_alu_operation,
            Opcode.DIV: self.execute_binary_alu_operation,
            Opcode.MOD: self.execute_binary_alu_operation,
            Opcode.SUB: self.execute_binary_alu_operation,
            Opcode.INC: self.execute_unary_alu_operation,
            Opcode.DEC: self.execute_unary_alu_operation,
            Opcode.POP: self.execute_pop,
            Opcode.CMP: self.execute_cmp,
            Opcode.DUP: self.execute_dup,
            Opcode.SWITCH: self.execute_switch,
            Opcode.DROP: self.execute_drop,
            Opcode.OUT: self.execute_out,
            Opcode.IN: self.execute_in,
        }

    def tick(self):
        self.ticks += 1

    def init_cycle(self):
        start_instr_address = self.datapath.signal_read_mem(self.datapath.pc).arg
        self.datapath.signal_latch_data_stack_reg_1(start_instr_address)
        self.tick()

        self.datapath.signal_latch_pc(self.datapath.data_tos_reg_1)
        self.tick()

    def decode_and_execute_instruction(self):
        instruction = self.datapath.signal_read_mem(self.datapath.pc)
        self.tick()

        opcode = instruction.opcode
        self.cur_instruction = instruction.opcode
        self.cur_operand = instruction.arg

        if self.decode_and_execute_control_flow_instruction(opcode):
            return

        executor = self.executors.get(opcode)
        executor(opcode)

    def decode_and_execute_control_flow_instruction(self, opcode: Opcode) -> bool:
        if opcode == Opcode.JMP:
            self.execute_jmp()
            return True
        if opcode == Opcode.JNZ:
            self.execute_jnz()
            return True
        if opcode == Opcode.HALT:
            self.execute_halt()
            return True
        if opcode == Opcode.JZ:
            self.execute_jz()
            return True
        if opcode == Opcode.CALL:
            self.execute_call()
            return True
        if opcode == Opcode.RET:
            self.execute_ret()
            return True
        return False

    def execute_lit(self, opcode: Opcode):
        value = self.datapath.signal_read_mem(self.datapath.pc)
        self.datapath.signal_latch_data_stack_reg_1(value.arg)
        self.tick()

        self.datapath.signal_write_data_stack(self.datapath.data_tos_reg_1)
        self.datapath.signal_latch_pc(self.datapath.pc + 1)
        self.tick()
        logging.debug("%s", self.__repr__())

    def execute_unary_alu_operation(self, opcode: Opcode):
        self.datapath.signal_latch_data_stack_reg_1(
            self.datapath.signal_read_data_stack()
        )
        self.tick()

        res = self.datapath.alu.calculate(
            self.datapath.data_tos_reg_1, self.datapath.data_tos_reg_2, opcode
        )
        self.datapath.signal_latch_data_stack_reg_1(res)
        self.tick()

        self.datapath.signal_write_data_stack(self.datapath.data_tos_reg_1)
        self.tick()

        self.datapath.signal_latch_pc(self.datapath.pc + 1)
        self.tick()

        logging.debug("%s", self.__repr__())

    def execute_out(self, opcode: Opcode):
        self.datapath.signal_latch_data_stack_reg_1(
            self.datapath.signal_read_mem(self.datapath.pc).arg
        )
        self.tick()

        self.datapath.signal_latch_data_stack_reg_2(
            self.datapath.signal_read_data_stack()
        )
        self.tick()

        self.datapath.io.write(
            Port(self.datapath.data_tos_reg_1), self.datapath.data_tos_reg_2
        )
        self.tick()

        self.datapath.signal_latch_pc(self.datapath.pc + 1)

    def execute_in(self, opcode: Opcode):
        self.datapath.signal_latch_data_stack_reg_1(
            self.datapath.signal_read_mem(self.datapath.pc).arg
        )
        self.tick()

        self.datapath.signal_latch_data_stack_reg_1(
            self.datapath.io.read(Port(self.datapath.data_tos_reg_1))
        )
        self.tick()

        self.datapath.signal_write_data_stack(self.datapath.data_tos_reg_1)
        self.datapath.signal_latch_pc(self.datapath.pc + 1)
        self.tick()

    def execute_push(self, opcode: Opcode):
        self.datapath.signal_latch_data_stack_reg_1(
            self.datapath.signal_read_data_stack()
        )
        self.datapath.signal_latch_top_address_stack(self.datapath.pc)
        self.tick()

        self.datapath.signal_latch_pc(self.datapath.data_tos_reg_1)
        self.tick()

        self.datapath.signal_latch_data_stack_reg_1(
            self.datapath.signal_read_mem(self.datapath.pc).arg
        )
        self.tick()

        self.datapath.signal_write_data_stack(self.datapath.data_tos_reg_1)
        self.datapath.signal_latch_pc(self.datapath.address_tos_reg_1)
        self.tick()

        self.datapath.signal_latch_pc(self.datapath.pc + 1)
        self.tick()

        logging.debug("%s", self.__repr__())

    def execute_pop(self, opcode: Opcode):
        self.datapath.signal_latch_data_stack_reg_1(
            self.datapath.signal_read_data_stack()
        )
        self.tick()

        self.datapath.signal_latch_data_stack_reg_2(
            self.datapath.signal_read_data_stack()
        )
        self.datapath.signal_latch_top_address_stack(self.datapath.pc)
        self.tick()

        self.datapath.signal_latch_pc(self.datapath.data_tos_reg_1)
        self.tick()

        self.datapath.signal_write_mem(self.datapath.pc, self.datapath.data_tos_reg_2)
        self.tick()

        self.datapath.signal_latch_pc(self.datapath.address_tos_reg_1 + 1)
        self.tick()

        logging.debug(self.__repr__())

    def execute_dup(self, opcode: Opcode):
        self.datapath.signal_latch_data_stack_reg_1(
            self.datapath.signal_read_data_stack()
        )
        self.tick()

        self.datapath.signal_write_data_stack(self.datapath.data_tos_reg_1)
        self.tick()

        self.datapath.signal_write_data_stack(self.datapath.data_tos_reg_1)
        self.tick()

        self.datapath.signal_latch_pc(self.datapath.pc + 1)
        self.tick()

        logging.debug("%s", self.__repr__())

    def execute_switch(self, opcode: Opcode):
        self.datapath.signal_latch_data_stack_reg_1(
            self.datapath.signal_read_data_stack()
        )
        self.tick()

        self.datapath.signal_latch_data_stack_reg_2(
            self.datapath.signal_read_data_stack()
        )
        self.tick()

        self.datapath.signal_write_data_stack(self.datapath.data_tos_reg_1)
        self.tick()

        self.datapath.signal_write_data_stack(self.datapath.data_tos_reg_2)
        self.tick()

        self.datapath.signal_latch_pc(self.datapath.pc + 1)
        self.tick()

        logging.debug("%s", self.__repr__())

    def execute_drop(self, opcode: Opcode):
        self.datapath.signal_latch_data_stack_reg_1(
            self.datapath.signal_read_data_stack()
        )
        self.tick()
        self.datapath.signal_latch_pc(self.datapath.pc + 1)
        logging.debug("%s", self.__repr__())

    def execute_binary_alu_operation(self, opcode: Opcode):
        operand_1 = self.datapath.signal_read_data_stack()
        self.datapath.signal_latch_data_stack_reg_1(operand_1)
        self.tick()

        operand_2 = self.datapath.signal_read_data_stack()
        self.datapath.signal_latch_data_stack_reg_2(operand_2)
        self.tick()

        res = self.datapath.alu.calculate(
            self.datapath.data_tos_reg_1, self.datapath.data_tos_reg_2, opcode
        )
        self.datapath.signal_latch_data_stack_reg_1(res)
        self.tick()

        self.datapath.signal_write_data_stack(self.datapath.data_tos_reg_1)
        self.datapath.signal_latch_pc(self.datapath.pc + 1)
        self.tick()
        logging.debug("%s", self.__repr__())

    def execute_cmp(self, opcode: Opcode):
        self.datapath.signal_latch_data_stack_reg_1(
            self.datapath.signal_read_data_stack()
        )
        self.tick()

        self.datapath.signal_latch_data_stack_reg_2(
            self.datapath.signal_read_data_stack()
        )
        self.tick()

        self.datapath.alu.calculate(
            self.datapath.data_tos_reg_2, self.datapath.data_tos_reg_1, opcode
        )
        self.datapath.signal_write_data_stack(self.datapath.data_tos_reg_2)
        self.tick()

        self.datapath.signal_write_data_stack(self.datapath.data_tos_reg_1)
        self.datapath.signal_latch_pc(self.datapath.pc + 1)
        self.tick()

        logging.debug("%s", self.__repr__())

    def execute_halt(self):
        logging.debug("%s", self.__repr__())
        raise HaltProgramException("Program halted")

    def execute_jmp(self):
        self.datapath.signal_latch_data_stack_reg_1(
            self.datapath.signal_read_mem(self.datapath.pc).arg
        )
        self.tick()

        self.datapath.signal_latch_pc(self.datapath.data_tos_reg_1)
        self.tick()

        logging.debug("%s", self.__repr__())

    def execute_jnz(self):
        if self.datapath.alu.z_flag == 1:
            self.datapath.signal_latch_data_stack_reg_1(
                self.datapath.signal_read_mem(self.datapath.pc).arg
            )
            self.tick()

            self.datapath.signal_latch_pc(self.datapath.data_tos_reg_1)
            self.tick()
            logging.debug("%s", self.__repr__())
            return
        self.datapath.signal_latch_pc(self.datapath.pc + 1)
        self.tick()
        logging.debug("%s", self.__repr__())

    def execute_jz(self):
        if self.datapath.alu.z_flag == 0:
            self.datapath.signal_latch_data_stack_reg_1(
                self.datapath.signal_read_mem(self.datapath.pc).arg
            )
            self.tick()

            self.datapath.signal_latch_pc(self.datapath.data_tos_reg_1)
            self.tick()

            logging.debug("%s", self.__repr__())
            return

        self.datapath.signal_latch_pc(self.datapath.pc + 1)
        self.tick()
        logging.debug("%s", self.__repr__())

    def execute_call(self):
        self.datapath.signal_latch_data_stack_reg_1(
            self.datapath.signal_read_mem(self.datapath.pc).arg
        )
        self.tick()

        self.datapath.signal_latch_pc(self.datapath.pc + 1)
        self.tick()

        self.datapath.signal_latch_top_address_stack(self.datapath.pc)
        self.datapath.signal_write_top_address_stack(self.datapath.address_tos_reg_1)
        self.tick()

        self.datapath.signal_latch_pc(self.datapath.data_tos_reg_1)
        self.tick()

        logging.debug("%s", self.__repr__())

    def execute_ret(self):
        self.datapath.signal_latch_top_address_stack(
            self.datapath.signal_read_top_of_address_stack()
        )
        self.tick()

        self.datapath.signal_latch_pc(self.datapath.address_tos_reg_1)
        self.tick()

        logging.debug("%s", self.__repr__())

    def __repr__(self):
        state_repr = (
            " TICK: {:3} PC {:3} TODS1 {:3} TODS2 {:3} TOAS {:3} Z_FLAG {:3}".format(
                str(self.ticks),
                str(self.datapath.pc),
                str(self.datapath.data_tos_reg_1),
                str(self.datapath.data_tos_reg_2),
                str(self.datapath.address_tos_reg_1),
                str(self.datapath.alu.z_flag),
            )
        )

        data_stack_repr = "DATA_STACK {}".format(self.datapath.data_stack)
        address_stack_repr = "ADDRESS_STACK {}".format(self.datapath.address_stack)

        cur_command = "{} {}".format(self.cur_instruction, self.cur_operand)

        if self.cur_operand is None:
            return "{} {}\n       {}\n       {} \n".format(
                state_repr, self.cur_instruction, data_stack_repr, address_stack_repr
            )
        return "{} {}\n       {}\n       {} \n".format(
            state_repr, cur_command, data_stack_repr, address_stack_repr
        )


def read_input(fn: str) -> list[int]:
    with open(fn) as f:
        fs = f.read()
        data: list = [ord(x) for x in fs]
        data.insert(0, len(data))
        return data


def simulation(
    code: list[MemoryCell], input_data: list[int]
) -> tuple[list[int], int, int]:
    io: IO = IO({STDIN: input_data, STDOUT: []})
    datapath: DataPath = DataPath(code, io)

    control_unit: ControlUnit = ControlUnit(datapath)
    instruction_counter: int = 0

    control_unit.init_cycle()

    try:
        while instruction_counter < INSTRUCTIONS_LIMIT:
            control_unit.decode_and_execute_instruction()
            instruction_counter += 1
    except HaltProgramException:
        instruction_counter += 1
        pass

    if instruction_counter == INSTRUCTIONS_LIMIT:
        logging.warning("Instruction limit")

    return (
        control_unit.datapath.io.ports[STDOUT],
        instruction_counter,
        control_unit.ticks,
    )


def main(source_code_fn: str, input_data_fn: str) -> None:
    machine_code: list[MemoryCell] = read_code(source_code_fn)
    input_str: list[int] = read_input(input_data_fn)

    res = simulation(machine_code, input_str)

    if len(res[0]) != 0:
        try:
            print("".join([chr(x) for x in res[0]]))
        except ValueError:
            [print(x) for x in res[0]]
    print(f"instruction_count: {res[1]}, ticks: {res[2]}".rstrip("\n"))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG, format="%(levelname)s: %(funcName)s:%(message)s"
    )
    logging.getLogger().setLevel(logging.DEBUG)
    assert (
        len(sys.argv) == 3
    ), "Not enough arguments: usage - machine.py <source_code_fn> <input_data_fn>"
    _, source, input_data = sys.argv
    main(source, input_data)
