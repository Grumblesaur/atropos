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
as well.

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

