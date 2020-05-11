# Atropos
Atropos is a tool for playing tabletop RPG games over Discord. Its primary
feature is a simple expression-based programming language that borrows heavily
from the behaviors of Python, but uses a lot of syntactic sugar or shorthand
to make things quicker to type than a Python REPL or scientific calculator
would allow.

## Questions

If you're confused about how something words, need to report a bug, or have an
idea for a new feature, you can open an issue on Atropos' GitHub repository,
which if you're not viewing the code there already, is here:

<https://github.com/Grumblesaur/atropos>

If you're shy or don't want to make a GitHub account, you can email me at
james.f.murphy.one@gmail.com
and I can answer your question or add your issue or feature request to the
project myself. If you're having a problem, please have your error message
and the input that caused it ready!


## Quickstart

This is a quick guide for some common operations when using Atropos. If you
want Atropos to see your message, make sure to start it with `+roll`. If this
would trigger another bot as well, you can use `+atropos roll` instead.

Roll dice (Examples)
```
  +roll 1d20    ~ a twenty-sided die
  +roll 4d6     ~ sum of 4 six-sided dice
  +roll 7d8h4   ~ sum of highest 4 of 7 eight-sided dice
  +roll 10d3l5  ~ sum of lowest 5 of 10 three-sided dice
  
  ~ Any number of dice or sides 1 or greater will work.
```

For the rest of the examples, I'm going to leave off the `+roll` prefix.

Multiply and divide (Examples)
```
  5 / 10      ~ gives 0.5
  8.8 / -2    ~ gives -4.4
  -3.0 * -3.0 ~ gives 9.0
  5 // 2      ~ gives 2  (// always gives an integer result)
```
Add and subtract (Examples)
```
  6 + 4   ~ gives 10
  5 - 6   ~ gives -1
```
Repeat (Example)
```
  4d6h3 ^ 6  ~ Does the following 6 times:
             ~   sums highest 3 of 4 six-sided dice
             ~   adds sum to a list.
             ~ Returns list.
```
These are all examples of expressions, which can be combined to your heart's
content. You can roll two different dice and add their totals together,
```
  1d6 + 1d10
```
or modify a roll
```
  1d100 - 10
  10 * 5d4
  10 / 1d20
```
Exponents (Examples)
```
  3 ** 2      ~ gives 9
  10 ** (-1)  ~ gives 0.1
```
Just like with regular math, Atropos' dice engine adheres to an order of
operations (also known as operator precedence). For the operations defined
above, the order of precedence is:
  * parentheses
  * dice
  * exponents
  * negative sign
  * multiplication and division
  * addition and subtraction

There are many more operations left out of the quickstart guide, but these are
all most games require. Other help topics will explain other features, and
elaborate on the ones listed.


## Commands

Atropos has a few different commands for interaction.

### roll
Invocation: `+atropos roll <dicelang command>` or `+roll <dicelang command>`

This is the main use case for Atropos. The operators and code constructs will
be described in detail further down the README. For the essentials, refer to
the quickstart guide above.

### help
Invocation: `+atropos help <topic> [option]` or `+help <topic> [option]`

This is the help command. For a list of topics, use the command `+help topics`.
Some topics have further detailed information, and will provide options to view
as well. If an option is searched without a topic, like

```+help [option]```

Atropos will attempt to look it up. If this lookup is ambiguous (that is, if
the same option is available to multiple topics), the user will receive a list
of possible topic-option combinations to try.

If the topic or option is shortened or incomplete, Atropos will attempt to find
a matching file or report a list of possible matches for the user to choose
from.

### view
Invocation: `+atropos view <datastore name>` or `+view <datastore name>`

This allows a user to see all dicelang variables that are available for them
to use. The datastore names are:

  * `globals`  -- See the names of variables available to any Atropos user.
  * `shareds`  -- See the names of variables available to any server user.
  * `privates` -- See the names of variables available only to you.
  * `all`      -- See all three of the above.

`shareds` has the alias `our vars`
`privates` has the alias `my vars`

