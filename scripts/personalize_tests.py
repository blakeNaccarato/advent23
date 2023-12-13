"""Personalize tests for a given user."""

from pathlib import Path
from textwrap import dedent

from typer import run


def main(user: str, day: str):
    user = "" if (user := user.casefold()) == "any" else user
    day = "" if day.casefold() == "any" else day.zfill(2)
    path = Path("pytest.ini")
    if not user and not day:
        path.unlink(missing_ok=True)
        return
    path.write_text(
        encoding="utf-8",
        data=dedent(
            f"""\
            [pytest]
            addopts =
                --strict-config
                --strict-markers
                --color yes
                -p no:legacypaths
                -r a
                -k {user}_day{day}
            cache_dir = .cache/.pytest_cache
            markers = slow
            testpaths = tests
            xfail_strict = True
            """
        ),
    )


if __name__ == "__main__":
    run(main)
