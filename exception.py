from __future__ import annotations


class HaltProgramError(Exception):
    def __init__(self):
        super().__init__("Program halted")


class OpcodeError(Exception):
    def __init__(self, opcode: str) -> None:
        super().__init__(f"Uknown opcode: {opcode}")


class LabelNotDefinedError(Exception):
    def __init__(self, label: str) -> None:
        super().__init__(f"Label {label} not defined")


class UnexpectedVariableError(Exception):
    def __init__(self, var: str) -> None:
        super().__init__(f"Unexpected variable {var}")


class VariableOrLabelNotDefinedError(Exception):
    def __init__(self, var: int | list[int] | None) -> None:
        super().__init__(f"Variable or label {var} not defined")
