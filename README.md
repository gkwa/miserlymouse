# miserlymouse

Runs caffeinate for a human-readable duration, or until the next time a clock reads some hour.

`caffeinate -t 7200` becomes `miserlymouse 2h`.

Execs caffeinate rather than spawning it, so Ctrl-C and the exit code behave exactly as running caffeinate directly.

Prints nothing on the happy path.

## Modes

`for` takes a duration. A bare duration with no subcommand means `for`.

`until` takes a clock time and resolves it to the next occurrence, so the wait is never longer than 24 hours. Asking for `3pm` at 4pm means 3pm tomorrow.

Options go before the duration or the time. Everything after it belongs to the wrapped command.

## Durations

- `2h`
- `30m`
- `1h24m`
- `1h 24m`
- `1h30m10s`
- `1.5h`
- `.5h`
- `90s`
- `1d`
- `1w`
- `1:24` meaning one hour twenty-four minutes
- `1:24:30` meaning hours, minutes, seconds
- `7200` bare, meaning seconds

## Times

- `3pm`
- `3 p.m.`
- `12.15pm`
- `12:15pm`
- `1215pm`
- `15:00`
- `1500`
- `noon`
- `midnight`

A bare hour such as `3` is rejected, because it reads as both 3pm and 03:00.

```sh
# stay awake for two hours
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse 2h

# stay awake for a compound duration
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse 1h24m

# the same thing, spelled out
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse for 1h24m

# stay awake until the next 3pm
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse until 3pm

# stay awake until a quarter past noon
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse until 12.15pm

# stay awake until the end of the working day, twenty-four hour clock
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse until 17:30

# keep the display awake too, not just the system
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --display until 3pm

# prevent system sleep while on AC power
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --system 45m

# combine assertions
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --display --system 1h30m

# stay awake while a command runs, then exit with that command's status
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse 30m make build

# flags after the duration go to the wrapped command, not to miserlymouse
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse 30m make --jobs 4

# print the caffeinate command without running it
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --dry-run 1h24m

# print the schedule as JSON, then run it
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --json until 3pm

# print the schedule as JSON and run nothing
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --json --dry-run until 3pm

# read one field out of the schedule
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --json --dry-run until 3pm | jq --raw-output .end

# log the exec line to stderr, then run it
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --verbose --verbose 2h

# show the version
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --version

# show all flags and both subcommands
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --help

# run the tests
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse --directory /Users/mtm/pdev/taylormonacelli/miserlymouse pytest -q

# install it so the bare name is on PATH
uv tool install /Users/mtm/pdev/taylormonacelli/miserlymouse
```

## JSON record

`--json` writes the schedule to stdout before caffeinate takes over.

- `mode` is `for` or `until`
- `request` is the string as typed
- `seconds` is what gets passed to `caffeinate -t`
- `duration` is that same span written back out in the duration grammar
- `start` and `end` are local ISO 8601, and `end` is exactly the moment the assertion drops
- `command` is the caffeinate argv
