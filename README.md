This is a command line shell for the OpenSwitch project.

[![Build Status](https://travis-ci.org/bluecmd/ops-cli-py.svg?branch=split)](https://travis-ci.org/bluecmd/ops-cli-py)
[![Coverage Status](https://coveralls.io/repos/github/bluecmd/ops-cli-py/badge.svg?branch=split)](https://coveralls.io/github/bluecmd/ops-cli-py?branch=split)
[![Code Climate](https://codeclimate.com/github/bluecmd/ops-cli-py/badges/gpa.svg)](https://codeclimate.com/github/bluecmd/ops-cli-py)

Documentation on adding new commands is in [NEW-COMMAND.md](NEW-COMMAND.md).
For more information on the internal workings, see [DESIGN.md](DESIGN.md).

Features
========
* Fully readline-compatible command line
* Tab completion on all commands and options
* Modular and dynamically pluggable commands
* Inline help on commands and options
* Per-subsystem debug facility
* Tokenizing parser with automatic type checking
* Expressive command module syntax for declaring options
* Nested contexts with custom command trees
* Running config infrastructure

TODO
====
* Better exception/error message integration
* Options ordering
* Better OVSDB link
* Full page help on commands
* Terminal size and paging
* Output filter (grep, skip)
* Syntax highlighting
