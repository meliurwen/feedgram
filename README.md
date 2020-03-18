<div align="center">
<img src="img/feedgram_logo.png" alt="MelDon Logo" width="200" >

# FeedGram

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://gitlab.com/Territory91/2019_assignment1_meldon/blob/master/LICENSE)

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

In this project we'll use Trello and the Gitlab's CI/CD infrastructure.

## App

> **Note:** At the moment it's in pre-alpha state; a sensible part of our available resources has been invested on the study on learning agile practices.

A simple Telegram bot app living in the cloud with bare bones functionalities!  ☁️🗒

This multi-user bot allows to receive news, RSS feeds, social networks and other platforms posts into a single and curated inbox!

The first social networks supported will be the most popular ones: Youtube, Instagram ,Flickr, Artstation, Twitter, etc...

## Architecture
> TODO

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
python3 -m venv .
```

```sh
source bin/activate
```

```sh
pip3 install requests
```

Now launch the bot:

```sh
python3 main.py
```


