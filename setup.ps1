<#.SYNOPSIS
Set up the project, creating a virtual environment, installing requirements and hooks.
#>

py -3.11 -m venv '.venv' --upgrade-deps
. '.venv/Scripts/activate'
python -m pip install --editable '.' --requirement 'requirements/requirements_dev.txt'
pre-commit install --install-hooks
