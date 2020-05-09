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

