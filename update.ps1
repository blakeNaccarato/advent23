<#.SYNOPSIS
Update the local virtual environment to the latest tracked dependencies.
#>

# Activate environment
$VENV_ACTIVATE_WINDOWS = '.venv/Scripts/activate'
$VENV_ACTIVATE_UNIX = '.venv/bin/Activate.ps1'
if ( Test-Path $VENV_ACTIVATE_WINDOWS ) { . $VENV_ACTIVATE_WINDOWS }
elseif ( Test-Path $VENV_ACTIVATE_UNIX ) { . $VENV_ACTIVATE_UNIX }
else {
    throw [System.Management.Automation.ItemNotFoundException] 'Could not find a virtual environment.'
}


$path = '.tools/requirements/requirements'
python -m pip install --editable '.' --requirement "$path/requirements_dev.txt'

# Install all types of pre-commit hooks
$h = '--hook-type'
$AllHookTypes = @(
    $h, 'commit-msg'
    $h, 'post-checkout'
    $h, 'post-commit'
    $h, 'post-merge'
    $h, 'post-rewrite'
    $h, 'pre-commit'
    $h, 'pre-merge-commit'
    $h, 'pre-push'
    $h, 'pre-push'
    $h, 'prepare-commit-msg'
)
pre-commit install --install-hooks @AllHookTypes
