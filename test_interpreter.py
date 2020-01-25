import interpreter
import pytest

class TestInterpreter:

    @pytest.mark.parametrize("command, expected",
                            [["[]",                  []],
                             ["[2]",                 [2]],
                             ["[1,2,3]",             [1,2,3]],
                             ['["a","b","c"]',       ["a","b","c"]],
                             ["[True, False]",       [True, False]],
                             ["[1,2,3][0]",          1],
                             ['["a","b"][1]',        "b"],
                             ["[[[True]]][0][0][0]", True],
                             ["1",                   1],
                             ["1+1",                 2],
                             ["1-1",                 0],
                             ["1+1-1",               1],
                             ["1*1",                 1],
                             ["2*2",                 4],
                             ["2**2",                4],
                             ["2**3",                8],
                             ["2%%8",                3],
                             ["4/2",                 2],
                             ["5/2",                 2.5],
                             ["5//2",                2],
                             ["[1] + [1]",           [1,1]],
                             ["[1] - [1]",           []],
                             ["[1,2] - [1,2]",       []],
                             ["[1,2,3] - [1,2]",     [3]],
                             ["[1,2] + [1,2]",       [1,2,1,2]]])
    def test_execute(self, command, expected):
        dicelark = interpreter.Interpreter("grammar.lark")
        user = "Tester"
        server = "Test Server"

        actual = dicelark.execute(command, user, server)

        assert actual == expected
