import miserlymouse.runner


def test_bare_duration() -> None:
    command = miserlymouse.runner.build_command(7200, {}, [])
    assert command == ["caffeinate", "-t", "7200"]


def test_assertion_flags_precede_timeout() -> None:
    command = miserlymouse.runner.build_command(
        60, {"display": True, "system": True}, []
    )
    assert command == ["caffeinate", "-d", "-s", "-t", "60"]


def test_utility_trails() -> None:
    command = miserlymouse.runner.build_command(60, {}, ["make", "build"])
    assert command == ["caffeinate", "-t", "60", "make", "build"]
