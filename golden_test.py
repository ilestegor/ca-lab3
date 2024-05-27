import contextlib
import io
import logging
import os
import tempfile

import pytest

import machine
import translator

formatter = logging.Formatter('%(levelname)s: %(funcName)s:%(message)s')


def add_custom_log_handler(logger):
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return handler


@pytest.mark.golden_test("golden/*.yml")
def test_translator_and_machine(golden, caplog):
    caplog.set_level(logging.DEBUG)

    logger = logging.getLogger()

    caplog_handler = logging.StreamHandler(caplog.handler.stream)
    caplog_handler.setFormatter(formatter)
    logger.addHandler(caplog_handler)
    if caplog.handler:
        logger.removeHandler(caplog.handler)

    with tempfile.TemporaryDirectory() as tmpdirname:
        source = os.path.join(tmpdirname, "source.txt")
        input_stream = os.path.join(tmpdirname, "input")
        target = os.path.join(tmpdirname, "out.txt")

        with open(source, mode="w", encoding="utf-8") as f:
            f.write(golden["in_source"])
        with open(input_stream, mode="w", encoding="utf-8") as f:
            f.write(golden["in_stdin"])

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main(source, target)
            print("============================================================")
            machine.main(target, input_stream)

        with open(target, "r", encoding="utf-8") as f:
            code = f.read()

        assert code == golden.out["out_code"]
        assert stdout.getvalue().strip() == golden.out["out_stdout"]
        assert caplog.text.strip() == golden.out["out_log"]
