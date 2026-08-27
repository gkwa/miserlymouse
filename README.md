# miserlymouse

Run caffeinate for a human-readable duration instead of a raw second count.

`caffeinate -t 7200` becomes `miserlymouse 2h`.

## Durations

- `2h`
- `30m`
- `1h24m`
- `1h 24m`
- `1h30m10s`
- `1.5h`
- `90s`
- `1d`
- `1w`
- `1:24` for one hour twenty-four minutes
- `1:24:30` for hours, minutes, seconds
- `7200` bare, meaning seconds

## Cheatsheet

Keep the machine awake for two hours:

```sh
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse 2h
```

See the caffeinate command without running it:

```sh
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --dry-run 1h24m
```

```
caffeinate -t 5040
```

Keep the display awake too:

```sh
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --dry-run --display 2h
```

```
caffeinate -d -t 7200
```

Stay awake while a command runs:

```sh
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --dry-run 30m make build
```

```
caffeinate -t 1800 make build
```

Reject a duration it cannot read:

```sh
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse 2hours
```

```
usage: miserlymouse [-h] [--version] [--display] [--idle] [--disk] [--system]
                    [--user-active] [--dry-run] [--verbose]
                    duration ...
miserlymouse: error: cannot parse duration: '2hours'
```

Full help:

```sh
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse miserlymouse --help
```

```
usage: miserlymouse [-h] [--version] [--display] [--idle] [--disk] [--system]
                    [--user-active] [--dry-run] [--verbose]
                    duration ...

Run caffeinate for a human-readable duration

positional arguments:
  duration           how long to stay awake, such as 1h24m
  utility            optional command to run while awake

options:
  -h, --help         show this help message and exit
  --version          show program's version number and exit
  --display, -d      keep the display awake
  --idle, -i         prevent idle sleep
  --disk, -m         prevent disk idle sleep
  --system, -s       prevent system sleep on AC
  --user-active, -u  declare the user active
  --dry-run          print the caffeinate command instead of running it
  --verbose, -v      raise the log level

durations accept 2h, 30m, 1h24m, 1.5h, 90s, 1d, 1:24, 1:24:30, or bare seconds
```

## Notes

The tool replaces itself with caffeinate through exec, so Ctrl-C and the exit code behave exactly as they would running caffeinate directly.

It prints nothing on the happy path.

Tests:

```sh
uv run --no-active --project /Users/mtm/pdev/taylormonacelli/miserlymouse --directory /Users/mtm/pdev/taylormonacelli/miserlymouse pytest -q
```
