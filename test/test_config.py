#!/usr/bin/env python3

from os import path, remove
from unittest.mock import patch
from feedgram.lib.config import Config

# creo il file di configurazione che non esiste con la configurazione di default


def test_config_creation():
    config_path = "./test/config/config_new.ini"

    # Verifico se il file esiste. Nel caso eista lo elimino
    if path.exists(config_path):
        try:
            remove(config_path)
        except OSError as err:  # if failed, report it back to the user ##
            print("Error: %s - %s." % (err.filename, err.strerror))

    assert not path.exists(config_path)
    config = Config(config_path)
    assert path.exists(config_path)
    assert config.status == -7

# manca una chiave


def test_config_miss_key():
    config_path = "./test/config/config_miss_key.ini"
    config = Config(config_path)
    assert config.status == -6

# manca una sezione


def test_config_miss_section():
    config_path = "./test/config/config_miss_section.ini"
    config = Config(config_path)
    assert config.status == -5

# sezioni duplicate


def test_duplicate_section():
    config_path = "./test/config/config_duplicate_section.ini"
    config = Config(config_path)
    assert config.status == -3

# chiavi duplicate


def test_config_duplicate_key():
    config_path = "./test/config/config_duplicate_key.ini"
    assert path.exists(config_path)
    config = Config(config_path)
    assert config.status == -2

# File caricato ed coretto


def test_config_work():
    config_path = "./test/config/config_work.ini"
    assert path.exists(config_path)
    config = Config(config_path)
    assert config.status == 1
    assert config.dictionary["BOT"]["databasefilepath"] == "socialFeedgram.sqlite3"
    assert config.dictionary["API"]["telegramkey"] == "5616486161:aslihfawlhrki2u4hbvlWAYgv"
    assert config.dictionary["BOT"]["privilegekey"] == "mZmUG9fD2njrkyJ7"


def test_oserror():
    with patch('feedgram.lib.config.open') as mock_oserror:
        mock_oserror.side_effect = OSError
        config_path = "./some/path/config_file_test.ini"
        try:
            Config(config_path)
        except OSError:
            print('test passed, sys.exit() called')
