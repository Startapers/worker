## installing && configuration:
### dependencies
 - install pyenv (https://github.com/pyenv/pyenv) or other python version manager
 - install appropriate python version
```bash
pyenv install $(cat p_version)
```
 - create a virtual environment
```bash
$(pyenv root)/versions/$(cat p_version)/bin/python -m venv .venv
```
 - install a python package manager
```bash
source .venv/bin/activate && pip install pipenv==$(cat pipenv_version)
```
 - install dependencies
```bash
source .venv/bin/activate && pipenv sync --dev
```
