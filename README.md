# miserlymouse

Runs caffeinate for a human-readable duration instead of a raw second count.

`caffeinate -t 7200` becomes `miserlymouse 2h`.

Execs caffeinate rather than spawning it, so Ctrl-C and the exit code behave exactly as running caffeinate directly.

Prints nothing on the happy path.

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

```sh
# stay awake for two hours
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse 2h

# stay awake for a compound duration
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse 1h24m

# stay awake for thirty minutes
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse 30m

# keep the display awake too, not just the system
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --display 2h

# prevent system sleep while on AC power
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --system 45m

# combine assertions
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --display --system 1h30m

# stay awake while a command runs, then exit with that command's status
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse 30m make build

# print the caffeinate command without running it
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --dry-run 1h24m

# log the exec line to stderr, then run it
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --verbose --verbose 2h

# show the version
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --version

# show all flags and the accepted duration forms
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --help

# run the tests
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse --directory /Users/mtm/pdev/taylormonacelli/miserlymouse pytest -q

# install it so the bare name is on PATH
uv tool install /Users/mtm/pdev/taylormonacelli/miserlymouse
```
