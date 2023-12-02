# advent23

Collaboration on Advent of Code 2023.

Each day, a new challenge is released over at [Advent of Code](https://adventofcode.com/). If a template doesn't exist for a particular question, create one in `src/advent23`. If you are the first one to get the right answer for a given day, update `ANSWERS` in `tests/advent23_tests/answers.py` and commit the changes. One of us must solve the full problem and update `ANSWERS` in order for tests to activate for everyone.

Follow [one-time setup](#one-time-setup) if you don't have Git/Python/etc. installed.

## Setup

Clone this repository by running the command below, and open it in VSCode. Alternatively, you can [do this directly in VSCode](https://code.visualstudio.com/docs/sourcecontrol/github#_cloning-a-repository).

```PowerShell
git clone 'https://github.com/blakeNaccarato/advent23.git' '<destination-directory>'
```

When you first open the cloned directory in VSCode, you will be prompted to install recommended extensions. You should be able to get by without installing them, but they are generally useful extensions for Python development.

Next, either run the setup task (`Tasks: Run Task` in the command palette, then run `setup: Setup project`) or run `./setup.ps1` in the terminal. You will be prompted with, `We noticed a new environment has been created. Do you want to select it for the workspace folder`. Select `Yes` to this prompt.

## One-time setup

These requirements should only need to be installed once on a given machine. Also, make sure you set up a [GitHub](https://github.com/) account.

- [Git](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup): Git allows for version control of your code and is required for versioning your code with GitHub, and using this template.
- [VSCode](https://code.visualstudio.com/docs/setup/setup-overview): This template focuses on custom configuration and extensions in VSCode to speed up the development process.
- [Cross-platform PowerShell](https://github.com/PowerShell/PowerShell#get-powershell): PowerShell is no longer Windows-only. Automations in this template are written for PowerShell, and should run on any platform.
- [Python](https://www.python.org/downloads): Install Python from the link rather than the Windows Store! This gives you the Python launcher, invoked with `py`, facilitates multiple Python versions being installed, and is required for this repository.

## Features requiring certain accounts

These accounts may need to be linked to your GitHub account in order to use some of the features in the recommended extensions for this repository.

- [Sourcery](https://sourcery.ai/): Sourcery does a great job of teaching valuable Python lessons as you code. It will suggest alternative wording for given code patterns, gently guiding you towards more "Pythonic" code.
- [GitLens](https://www.gitkraken.com/gitlens): Installed along with recommended extensions. You may be prompted to create an account, which you can just link to your GitHub account if desired. This extension is indispensable for managing git-versioned projects.
