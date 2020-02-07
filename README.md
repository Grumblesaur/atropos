# Atropos
Atropos is a tool for playing tabletop RPG games over Discord. Its primary
feature is a simple expression-based programming language that borrows
heavily from the behaviors of Python, but uses a lot of syntactic sugar or
shorthand to make things quicker to type than a Python REPL or a scientific
calculator would.

## Questions

If you're confused about how something works, need to report a bug, or have
an idea for a new feature, you can open an issue on Atropos' Github repository,
which if you're not viewing the code there already, is here:

<https://github.com/Grumblesaur/atropos>

If you're shy, or don't want to make a Github account, you can email me at
james.f.murphy.one@gmail.com
and I can answer your question or add your issue or feature request to the
project myself. If you're having a problem, please have your error message
and the input that caused it ready!

## Quickstart

If you're a newbie user, or you just need to know how to roll dice, here's a
quick guide to a few common operations you'll be using. If you want Atropos
to see your message, make sure to start it with `+roll`. If that collides with
a command in use by some other bot or application on your server, you can
prefix your messages with `+atropos roll` instead.

Roll dice (Examples)
```
  +roll 1d20    ~ rolls a single 20-sided die
  +roll 4d6     ~ rolls four 6-sided dice, and sums their outcomes
  +roll 7d8h4   ~ rolls seven 8-sided dice, keeps the highest four, and sums them
  +roll 10d3l5  ~ rolls ten 3-sided dice, keeps the lowest five, and sums them
                ~ You aren't limited to the kinds of dice you find in a game shop --
                ~ any number of sides greater than 0 will work correctly. If you need
                ~ to roll 3d763, you can do that.
```

For the rest of the examples, I'm going to leave off the `+roll` prefix.

Multiply and divide (Examples)
```
  5 / 10      ~ will evaluate to 0.5
  3 * 20      ~ will evaluate to 60
  8.8 / -2    ~ will evaluate to -4.4
  -3.0 * -3.0 ~ will evaluate to 9.0
  5 // 2      ~ will evalaute to 2 (this always rounds the result down)
```

Add and subtract (Examples)
```
  6 + 4   ~ will evaluate to 10
  5 - 6   ~ will evaluate to -1
```

Repeat (example)
```
  4d6h3 ^ 6  ~ Does the following operation 6 times:
             ~   Rolls four 6-sided dice, keeps the highest three, and sums them.
             ~   Adds that sum to a list.
             ~ Then the list is returned.
             ~
             ~ If you're familiar with D&D, this is a common tactic for creating
             ~ an array of character ability scores.
             ~ List operations will be covered later in the guide.
```

These are all examples of expressions, which can be combined to your heart's
content. You can roll two different dice and add their totals together,
```
  1d6 + 1d10
```
or modify a roll
```
  1d20 + 5
  1d100 - 10
  10 * 5d4
  10 / 1d20
```

Just like with regular math, Atropos' dice engine adheres to an order of
operations (also known as operator precedence). If you're familiar with
PEMDAS, or

  * Parentheses
  * Exponents
  * Multiplication, Division
  * Addition, Subtraction

then you're already familiar with this concept. Atropos has exponents too! They
look like this:
```
  4 ** 2  ~ will evaluate to 16
```

For the operations defined above, the order of precedence is:

  * Parentheses
  * Dice
  * Exponents
  * Negative sign (e.g. -3) and positive sign (+4)
  * Multiplication, Division and Floor Division (the rounding-down division above)
  * Addition, Subtraction

There are many more operations left out of the quickstart guide, but these are
all most games require. Read on if you consider yourself a power user,
a programmer, or a dungeon master/game master/referee.


[TODO: FULL GUIDE]

