# Contributing

Runtime dependencies stay at zero (Python standard library only).

## Local check

~~~sh
make test
~~~

That is the local maintainer check in the README. When tests pass, the
local check is complete.

## Record the session

~~~sh
make publish
~~~

A full maintainer pass includes both the local check and this step.
