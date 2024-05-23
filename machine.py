import logging
from dataclasses import dataclass
from typing import Callable

import constants
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
    z_flag = None

    def calculate(self, left: int, right: int, opcode: Opcode) -> int:
        assert opcode in AVAILABLE_ALU_BIN_OPERATIONS or opcode in AVAILABLE_ALU_UNARY_OPERATIONS, \
            f"Unknown alu operation code: {opcode}"
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
        if not self.ports[port]:
            # TODO ADD LOG
            raise ValueError(f"WRONG PORT")
        value = self.ports[port].pop(0)
        return value

    def write(self, port: Port, value: int):
        self.ports[port].append(value)


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
        self.data_stack_size = constants.DATA_STACK_SIZE
        self.address_stack_size = constants.ADDRESS_STACK_SIZE
        self.address_stack = []
        self.address_tos_reg_1 = 0
        self.pc = 0
        self.io = io
        self.alu = Alu()

        self.memory = [0] * constants.MEMORY_SIZE
        for i in range(len(memory)):
            self.memory[i] = memory[i]
        self.mem_size = constants.MEMORY_SIZE

    def signal_latch_pc(self, value: int):
        self.pc = value

    def signal_read_mem(self, addr: int) -> MemoryCell:
        assert addr < self.mem_size, f"Memory read fault, cell with address - {addr} does not exist"
        return self.memory[addr]

    def signal_write_mem(self, addr: int, value: int) -> None:
        assert addr < self.mem_size, f"Memory write fault, cell with address - {addr} does not exist"
        self.memory[addr] = MemoryCell(addr, None, value)

    def signal_latch_data_stack_reg_1(self, value: int) -> None:
        self.data_tos_reg_1 = value

    def signal_latch_data_stack_reg_2(self, value: int) -> None:
        self.data_tos_reg_2 = value

    def signal_write_data_stack(self, value: int) -> None:
        assert (len(self.data_stack) != self.data_stack_size), "Data stack is overflowed"
        self.data_stack.append(value)

    def signal_read_data_stack(self) -> int:
        assert (len(self.data_stack) > 0), "Data stack is empty"
        return self.data_stack.pop()

    def signal_read_top_of_address_stack(self) -> int:
        assert (len(self.address_stack) > 0), "Address stack is empty"
        return self.address_stack.pop()

    def signal_latch_top_address_stack(self, value: int) -> None:
        self.address_tos_reg_1 = value

    def signal_write_top_address_stack(self, value: int) -> None:
        assert (len(self.address_stack) != self.address_stack_size), "Address stack is overflowed"
        self.address_stack.append(value)


#     TODO ADD IO CONTROLLER


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
            Opcode.ADD: self.execute_binary_alu_operation
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

        if self.decode_and_execute_control_flow_instruction(opcode):
            return

        executor = self.executors.get(opcode)
        executor(opcode)

    def execute_lit(self, opcode: Opcode):
        value = self.datapath.signal_read_mem(self.datapath.pc)
        self.datapath.signal_latch_data_stack_reg_1(value.arg)
        self.tick()

        self.datapath.signal_write_data_stack(self.datapath.data_tos_reg_1)
        self.datapath.signal_latch_pc(self.datapath.pc + 1)
        self.tick()
        logging.debug("%s", self.__repr__())

    def execute_binary_alu_operation(self, opcode: Opcode):
        operand_1 = self.datapath.signal_read_data_stack()
        self.datapath.signal_latch_data_stack_reg_1(operand_1)
        self.tick()

        operand_2 = self.datapath.signal_read_data_stack()
        self.datapath.signal_latch_data_stack_reg_2(operand_2)
        self.tick()

        res = self.datapath.alu.calculate(self.datapath.data_tos_reg_1, self.datapath.data_tos_reg_2, opcode)
        self.datapath.signal_latch_data_stack_reg_1(res)
        self.tick()

        self.datapath.signal_write_data_stack(self.datapath.data_tos_reg_1)
        self.datapath.signal_latch_pc(self.datapath.pc + 1)
        self.tick()
        logging.debug("%s", self.__repr__())

    def decode_and_execute_control_flow_instruction(self, opcode: Opcode) -> bool:
        if opcode == Opcode.HALT:
            self.execute_halt()
            return True
        return False

    def execute_halt(self):
        exit(0)

    def __repr__(self):
        state_repr = " TICK: {:3} PC {:3} TODS1 {:3} TODS2 {:3} TOAS {:3} Z_FLAG {:1}".format(
            str(self.ticks),
            str(self.datapath.pc),
            str(self.datapath.data_tos_reg_1),
            str(self.datapath.data_tos_reg_2),
            str(self.datapath.data_tos_reg_2),
            str(self.datapath.address_tos_reg_1),
            str(self.datapath.alu.z_flag)
        )

        data_stack_repr = "DATA STACK {}".format(self.datapath.data_stack)
        address_stack_repr = "ADDRESS STACK {}".format(self.datapath.address_stack)

        cur_command = "COMMAND - {}".format(self.cur_instruction)

        return "{} {}\n{}\n{} \n".format(state_repr, cur_command, data_stack_repr, address_stack_repr)


def simulation(code):
    logging.getLogger().setLevel(logging.DEBUG)
    io_stub = IO({STDIN: [1]})
    datapath = DataPath(code, io_stub)

    control_unit = ControlUnit(datapath)
    instruction_counter = 0

    control_unit.init_cycle()

    instr_len = len(code)
    while instruction_counter < constants.INSTRUCTIONS_LIMIT or instruction_counter < instr_len:
        control_unit.decode_and_execute_instruction()


def main():
    fn = "/Users/ilestegor/Desktop/Универ/2курс/4сем/арх.комп/lab3/out.txt"
    machine_code: list[MemoryCell] = read_code(fn)

    simulation(machine_code)


main()
