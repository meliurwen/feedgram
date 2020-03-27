<div align="center">
<img src="img/feedgram_logo.png" alt="MelDon Logo" width="200" >

# FeedGram

[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://gitlab.com/meliurwen/feedgram/blob/master/LICENSE)

</div>

# 2020 Laboratorio di Progettazione

> **_Note:_** It's a private repo, use the `LabProgettazioneDISCo` Gitlab's user in order to access it!

+ **_Project's Link:_** https://gitlab.com/meliurwen/feedgram
+ **_Demo Link:_** _TODO_

## Group Members

+ Salanti Michele - 793891
+ Donati Ivan - 781022

## Purpose

Acquire, through experimental activities, the skills necessary to independently develop a system using agile methodologies by practicing the knowledge acquired during the course of studies.

In this project we'll use **_Trello_** in combination with the _Gitlab's_ **_git_** and **_CI/CD_** infrastructure.

## App

> **Note:** At the moment it's in pre-alpha state; a sensible part of our available resources has been invested on the study on learning agile practices.

A simple to use, but yet powerful Telegram bot app living in the cloud with bare bones functionalities!  ☁️🗒

This **_multi-user bot_** allows to receive _news_, _RSS feeds_, _social networks and other platforms posts_ into a **_single and curated inbox_**!

The first platforms supported will be the most popular ones: _Instagram_, _Youtube_, _Flickr_, _Twitter_, _Artstation_, etc...

## Architecture

The diagram below is the **_high level architecture_** of this project and describes the _interactions_ between the _internal components_ of the app and between the app and the _external ones_:

![High Level Architecture](img/architecture_high_level.png)

As described by the diagram **_the bot does not interact directly with the users_**, but it accomplish this _via the Telegram's stack_ using _APIs expressively provided for the bots_.

The **_interactions with the socials/platforms_** will be done with various methods and techniques that depends on _how_ (and _at which conditions_) each social/platform we interact with exposes the data we need. In most cases _is better use the official APIs_ provided via _HTTP_ methods (GET or POST) or _OAuth_, but in few cases for various reasons the classic _scraping methods are more convenient_.

The **_internal structure_** of the application is mainly composed by a multitude of _specialised python modules_, an _SQLite3_ database and a config file in `ini` format, most of them directly orchestrated by a main module.


## How to Install and Launch

### Debian and derivatives

Install the dependencies:

```sh
apt-get -y install python3 python3-venv python3-pip
```

Enter the project's folder, _create_ the **_virtual environment_** and then _activate_ it:

```sh
cd feedgram
```

```sh
virtualenv -p python3 venv
```

```sh
source venv/bin/activate
```

```sh
pip3 install requests
```

Now launch the bot:

```sh
python3 main.py
```


