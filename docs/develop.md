# Develop

## Prerequisites

+ `python3` (_>=3.6_)
+ `python3-setuptools`
+ `python3-pip`
+ `python3-venv` (_optional_)

## Steps

_Create_ the **_virtual environment_** in the project's folder:

```sh
python3 -m venv venv
```

Or if oyu wanna use the `virtualenv` package:

```sh
virtualenv -p python3 venv
```

_Activate_ the virtual environment:

```sh
source venv/bin/activate
```

_Prepare_ the development environment:

```sh
./setup.py develop
```

That's all! ☕️

!!! tip
    To deactivate the **_virtual environment_** simply issue the `deactivate` command.
