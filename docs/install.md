# Install

## From Compiled Packages

At the moment platforms officially supported are:

+ Docker
+ Debian 10
+ Ubuntu 18.04
+ Python Wheels

Go to the [releases section](https://gitlab.com/meliurwen/feedgram/-/releases) to download the latest installer:

## From Docker

### Prerequisites

+ `docker`

### Launch

```sh
docker run -d --name feedgram --restart unless-stopped \
            -v config.ini:/app/config.ini \
            -v socialFeedgram.sqlite3:/app/socialFeedgram.sqlite3 \
            registry.gitlab.com/meliurwen/feedgram:latest
```

## From Source

### Prerequisites

+ `python3` (_>=3.6_)
+ `python3-setuptools`
+ `python3-pip`

### Install

At the _root_ of the project's folder launch:

```sh
pip3 install .
```

### Uninstall

Anywhere in the system launch:

```sh
pip3 uninstall <package_name>
```

### Upgrade

At the _root_ of the project's folder launch:

```sh
pip3 install --upgrade .
```
