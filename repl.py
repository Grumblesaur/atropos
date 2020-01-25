#!/usr/bin/env python

from interpreter import Interpreter
import readline
from lark.exceptions import UnexpectedToken 

running = True

dicelark = Interpreter("grammar.lark")
user = "Tester"
server = "Test Server"

print(
"""Dicelark v0.1
Enter !quit or press Ctrl-Z to exit."""
)

while running:
    command = input("dice > ")
    
    if command == "!quit":
        running = False
    else:
        try:
            output = dicelark.execute(command, user, server)
            print(output)
        except UnexpectedToken as e:
            print(f"Unknown command: {command}")

