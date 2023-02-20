![FeedGram Logo](img/feedgram_logo.png)

# FeedGram

[![pipeline status](https://gitlab.com/meliurwen/feedgram/badges/master/pipeline.svg)](https://gitlab.com/meliurwen/feedgram/commits/master) [![coverage report](https://gitlab.com/meliurwen/feedgram/badges/master/coverage.svg)](https://gitlab.com/meliurwen/feedgram/commits/master) [![Pylint](https://gitlab.com/meliurwen/feedgram/-/jobs/artifacts/master/raw/pylint/pylint.svg?job=pylint)](https://gitlab.com/meliurwen/feedgram/-/jobs/artifacts/master/raw/pylint/pylint.log?job=pylint) [![FeedGram](https://gitlab.com/meliurwen/feedgram/-/jobs/artifacts/master/raw/pylint/app_version.svg?job=pylint)](https://gitlab.com/meliurwen/feedgram/-/jobs/artifacts/master/raw/pylint/app_version.svg?job=pylint) [![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://gitlab.com/meliurwen/feedgram/blob/master/LICENSE)

[![Platform](https://gitlab.com/meliurwen/feedgram/-/jobs/artifacts/master/raw/pylint/plaform.svg?job=pylint)](https://gitlab.com/meliurwen/feedgram/-/jobs/artifacts/master/raw/pylint/plaform.svg?job=pylint) [![Python_ver](https://gitlab.com/meliurwen/feedgram/-/jobs/artifacts/master/raw/pylint/python_ver.svg?job=pylint)](https://gitlab.com/meliurwen/feedgram/-/jobs/artifacts/master/raw/pylint/python_ver.svg?job=pylint) [![Wheel](https://gitlab.com/meliurwen/feedgram/-/jobs/artifacts/master/raw/pylint/wheel.svg?job=pylint)](https://gitlab.com/meliurwen/feedgram/-/jobs/artifacts/master/raw/pylint/wheel.svg?job=pylint) [![pip_install](https://gitlab.com/meliurwen/feedgram/-/jobs/artifacts/master/raw/pylint/pip_install.svg?job=pylint)](https://gitlab.com/meliurwen/feedgram/-/jobs/artifacts/master/raw/pylint/pip_install.svg?job=pylint)

## Main Resources

+ :fontawesome-brands-gitlab: **_Project's Link:_** [gitlab.com/meliurwen/feedgram](https://gitlab.com/meliurwen/feedgram)
+ :fontawesome-brands-telegram: **_Demo Link:_** [t.me/FeedGram_demo_bot](https://t.me/FeedGram_demo_bot)

## App

> **Note:** At the moment it's in pre-alpha state; a sensible part of our available resources has been invested on the study on learning agile practices.

A simple to use, but yet powerful Telegram bot app living in the cloud with advanced functionalities! :cloud::muscle:

This **_multi-user bot_** allows to receive _news_, _RSS feeds_, _social networks and other platforms posts_ into a **_single and curated inbox_**!

The first platforms supported will be the most popular ones: ~~_Instagram_~~, _Youtube_, _Flickr_, _Twitter_, _Artstation_, etc...

## Architecture

The diagram below is the **_high level architecture_** of this project and describes the _interactions_ between the _internal components_ of the app and between the app and the _external ones_:

![High Level Architecture](img/architecture_high_level.png)

As described by the diagram **_the bot does not interact directly with the users_**, but it accomplish this _via the Telegram's stack_ using _APIs expressively provided for the bots_.

The **_interactions with the socials/platforms_** will be done with various methods and techniques that depends on _how_ (and _at which conditions_) each social/platform we interact with exposes the data we need. In most cases _is better use the official APIs_ provided via _HTTP_ methods (GET or POST) or _OAuth_, but in few cases for various reasons the classic _scraping methods are more convenient_.

The **_internal structure_** of the application is mainly composed by a multitude of _specialised python modules_, an _SQLite3_ database and a config file in `ini` format, most of them directly orchestrated by a main module.

## Contribute

> **Main Contributors**: Meliurwen, Ivan Donati

In this project we use _Gitlab's_ **_kanban_**, **_git_**, **_CI/CD_** infrastructure and **_registry_**.

See [here](contributing.md) to know how to report bugs, propose features, merge requests or other forms of contribution! :sunglasses::rocket:
