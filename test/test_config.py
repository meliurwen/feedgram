#!/usr/bin/env python3

from os import path, remove
from unittest.mock import patch
from feedgram.lib.config import Config

# creo il file di configurazione che non esiste con la configurazione di default


def test_config_creation():

    # Nome del file per il test
    config_path = "./test/config/config_new.ini"

    # Verifico se il file esiste. Nel caso eista lo elimino
    if path.exists(config_path):
        try:
            remove(config_path)
        except OSError as err:  # if failed, report it back to the user ##
            print("Error: %s - %s." % (err.filename, err.strerror))

    # Mi assicuro che il file non esista/ sia stato cancellato
    assert not path.exists(config_path)

    # Eseguo la chiamata al costruttore della classe di configurazione
    # che mi genererà il file di configurazione con i valori base
    # e tenterà di caricarla
    config = Config(config_path)

    # verifico che il file sia stato creato
    assert path.exists(config_path)

    # Verifico che lo stato della classe sia quello coretto
    assert config.status == -7

# manca una chiave


def test_config_miss_key():

    # Nome del file per il test
    config_path = "./test/config/config_miss_key.ini"

    # Mi assicuro che il file esista / che non sia stato cancellato
    assert path.exists(config_path)

    # Eseguo la chiamata al costruttore della classe di configurazione
    # che mi genererà il file di configurazione con i valori base
    # e tenterà di caricarla
    config = Config(config_path)

    # Verifico che lo stato della classe sia quello coretto
    assert config.status == -6

# manca una sezione


def test_config_miss_section():

    # Nome del file per il test
    config_path = "./test/config/config_miss_section.ini"

    # Mi assicuro che il file esista / che non sia stato cancellato
    assert path.exists(config_path)

    # Eseguo la chiamata al costruttore della classe di configurazione
    # che mi genererà il file di configurazione con i valori base
    # e tenterà di caricarla
    config = Config(config_path)

    # Verifico che lo stato della classe sia quello coretto
    assert config.status == -5

# sezioni duplicate


def test_duplicate_section():

    # Nome del file per il test
    config_path = "./test/config/config_duplicate_section.ini"

    # Mi assicuro che il file esista / che non sia stato cancellato
    assert path.exists(config_path)

    # Eseguo la chiamata al costruttore della classe di configurazione
    # che mi genererà il file di configurazione con i valori base
    # e tenterà di caricarla
    config = Config(config_path)

    # Verifico che lo stato della classe sia quello coretto
    assert config.status == -3

# chiavi duplicate


def test_config_duplicate_key():

    # Nome del file per il test
    config_path = "./test/config/config_duplicate_key.ini"

    # Mi assicuro che il file esista / che non sia stato cancellato
    assert path.exists(config_path)

    # Eseguo la chiamata al costruttore della classe di configurazione
    # che mi genererà il file di configurazione con i valori base
    # e tenterà di caricarla
    config = Config(config_path)

    # Verifico che lo stato della classe sia quello coretto
    assert config.status == -2

# FIle caricato ed coretto


def test_config_work():

    # Nome del file per il test
    config_path = "./test/config/config_work.ini"

    # Mi assicuro che il file esista / che non sia stato cancellato
    assert path.exists(config_path)

    # Eseguo la chiamata al costruttore della classe di configurazione
    # che mi genererà il file di configurazione con i valori base
    # e me la caricherà
    config = Config(config_path)

    # Verifico che lo stato della classe sia quello coretto
    assert config.status == 1

    # Verifico che la configurazione abbia i valori aspettati

    assert config.dictionary["BOT"]["databasefilepath"] == "socialFeedgram.sqlite3"

    assert config.dictionary["API"]["telegramkey"] == "5616486161:aslihfawlhrki2u4hbvlWAYgv"

    assert config.dictionary["API"]["youtubev3key"] == "ka3iorq237byfrva4wiymhvtlih4awyhnal"


def test_oserror():
    with patch('feedgram.lib.config.open') as mock_oserror:
        mock_oserror.side_effect = OSError
        config_path = "./some/path/config_file_test.ini"
        try:
            Config(config_path)
        except OSError:
            print('test passed, sys.exit() called')
