"""Personalize tests for a given user."""

from pathlib import Path
from textwrap import dedent

from typer import run


def main(user: str):
    """Personalize tests for a given user.

    Args:
        user: The user to personalize the tests for.
    """
    user = user.casefold()
    path = Path("pytest.ini")
    if user == "all":
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
                -k {user}_
            cache_dir = .cache/.pytest_cache
            markers = slow
            testpaths = tests
            xfail_strict = True
            """
        ),
    )


if __name__ == "__main__":
    run(main)
