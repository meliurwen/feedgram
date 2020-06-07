# Testing & Linting

## Prerequisites

+ `python3` (_>=3.6_)
+ `python3-setuptools`
+ `python3-pip`
+ `python3-venv` (_optional_)

## Steps

_Activate_ the **virtual environment** as described in [Develop](develop.md). (optional)

Install the dependencies:

```sh
pip3 install -r test-requirements.txt
```

To launch **Pytest**:

```sh
pytest
```

To launch **Pylint**:

```sh
pylint --output-format=text --rcfile=setup.cfg app/ test/ *.py
```

To launch **Flake8**:

```sh
flake8
```
