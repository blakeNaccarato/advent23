"""Abdul's solutions."""

import re


def color_outcome(color: str, data_input):
    """Return a list of sets which represent the outcome of
    each color for all games.
    """
    color_outcome_all_games = []

    number_pattern = re.compile(pattern=r"(Game \d{1,5}):\s")
    color_pattern = re.compile(pattern=rf"(\d{{1,5}} {color})")

    for game in data_input:
        # Separate each game into separate pulls
        m = re.search(number_pattern, game)
        game_pulls = game[m.end() :]
        single_pull = re.split(r";\s+", game_pulls)
        temp_set = set()

        # Populate set for each game containing all results for color
        for each_outcome in single_pull:
            color_result = re.search(color_pattern, each_outcome)
            if color_result is not None:
                temp_set.add(int(color_result[0].strip(f"{color}")))
            else:
                temp_set.add(0)

        color_outcome_all_games.append(temp_set)

    print(color_outcome_all_games)  # noqa: T201
    return color_outcome_all_games


def compare_color_set(color_set: set, color: str):
    for val in color_set:
        if color == "red" and val > 12:
            return False
        if color == "green" and val > 13:
            return False
        if color == "blue" and val > 14:
            return False
    return color_set


# Ruff thinks we don't need the `color` argument below, we must've changed this function
# to not use that argument after we wrote it. We could remove the argument outright, or
# we could add a leading underscore to the argument name to indicate that it's not used.
# Since you are using this throughout your notebook, I can see why you left the argument
# in, but a refactor would probably correct that throughout.


def get_min_possible(color_set: set, color: str):  # noqa: ARG001
    return max(color_set)
