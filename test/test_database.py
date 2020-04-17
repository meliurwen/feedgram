#!/usr/bin/env python3

from os import path, remove
import sqlite3
from app.lib.database import MyDatabase


def myquery(db_path, query, *args, foreign=False, fetch=1):
    con = None
    data = None
    rowcount = 0

    print('Executing: {} with args {} with foreign_keys={}.'.format(query, args, foreign))
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        if foreign:
            cur.execute("PRAGMA foreign_keys = ON")
        cur.execute(query, tuple(args))

        if fetch > 1:
            data = cur.fetchmany(fetch)
        elif fetch == 0:
            data = cur.fetchall()
        else:
            data = cur.fetchone()

        rowcount = cur.rowcount

        if not data:
            con.commit()
    except sqlite3.Error as err:
        print("Database error: {}".format(err))
    except sqlite3.Warning as err:
        print("Exception in query: {}".format(err))
    finally:
        if con:
            con.close()
    return data, rowcount


DATABASE_PATH = "./test/databseTest.sqlite3"


def test_database_table_error():

    # Nome del file per il test
    database_path = "./test/databse_table_error.sqlite3"

    # Verifico se il file esiste. Nel caso eista lo elimino
    if path.exists(database_path):
        try:
            remove(database_path)
        except OSError as err:  # if failed, report it back to the user ##
            print("Error: {} - {}.".format(err.filename, err.strerror))

    # Mi assicuro che il file non esista/ sia stato cancellato
    assert not path.exists(database_path)

    # Eseguo la chiamata al costruttore della classe di configurazione
    # che mi genererà il file di configurazione con i valori base
    # e tenterà di caricarla
    MyDatabase(database_path)

    # Mi assicuro che il file sia stato creato
    assert path.exists(database_path)

    # Rimuovo una tabella
    myquery(database_path, 'DROP TABLE admins')

    # Rieseguo il costruttore che antrà ad aprire il database precedentemnte
    # creato ma senza una tabella
    database = MyDatabase(database_path)

    # Verifico che lo stato della classe sia quello coretto
    assert database.status == -1


def test_database_creation():

    # creo il database che non esiste con le tabelle base

    # Verifico se il file esiste. Nel caso eista lo elimino
    if path.exists(DATABASE_PATH):
        try:
            remove(DATABASE_PATH)
        except OSError as err:  # if failed, report it back to the user ##
            print("Error: {} - {}.".format(err.filename, err.strerror))

    # Mi assicuro che il file non esista/ sia stato cancellato
    assert not path.exists(DATABASE_PATH)

    # Eseguo la chiamata al costruttore della classe di configurazione
    # che mi genererà il file di configurazione con i valori base
    # e tenterà di caricarla
    database = MyDatabase(DATABASE_PATH)

    # state = database.status

    # verifico che il file sia stato creato
    assert path.exists(DATABASE_PATH)

    # Verifico che lo stato della classe sia quello coretto
    assert database.status == 1


def test_database_alredy_exist():

    # Mi assicuro che il file non esista/ sia stato cancellato
    assert path.exists(DATABASE_PATH)

    # Eseguo la chiamata al costruttore della classe di configurazione
    # che mi genererà il file di configurazione con i valori base
    # e tenterà di caricarla
    database = MyDatabase(DATABASE_PATH)

    # Verifico che lo stato della classe sia quello coretto
    assert database.status == 1


def test_database_user_id_not_exist():

    # Mi assicuro che il file non esista/ sia stato cancellato
    assert path.exists(DATABASE_PATH)

    # Eseguo la chiamata al costruttore della classe di configurazione
    # che mi genererà il file di configurazione con i valori base
    # e tenterà di caricarla
    database = MyDatabase(DATABASE_PATH)

    us_exist = database.check_utente(6551474276)

    assert not us_exist


def test_database_subscribe():

    # Mi assicuro che il file non esista/ sia stato cancellato
    assert path.exists(DATABASE_PATH)

    # Eseguo la chiamata al costruttore della classe di configurazione
    # che mi genererà il file di configurazione con i valori base
    # e tenterà di caricarla
    database = MyDatabase(DATABASE_PATH)

    database.subscribe_user(6551474276, "username", 75692378, 1, 10)

    us_exist, _ = myquery(DATABASE_PATH, "SELECT 1 FROM users WHERE user_id = ?;", 6551474276)

    assert bool(us_exist)


def test_database_user_id_exist():

    # Mi assicuro che il file non esista/ sia stato cancellato
    assert path.exists(DATABASE_PATH)

    # Eseguo la chiamata al costruttore della classe di configurazione
    # che mi genererà il file di configurazione con i valori base
    # e tenterà di caricarla
    database = MyDatabase(DATABASE_PATH)

    us_exist = database.check_utente(6551474276)

    assert us_exist


def test_database_unsubscribe():

    # Mi assicuro che il file non esista/ sia stato cancellato
    assert path.exists(DATABASE_PATH)

    # Eseguo la chiamata al costruttore della classe di configurazione
    # che mi genererà il file di configurazione con i valori base
    # e tenterà di caricarla
    database = MyDatabase(DATABASE_PATH)

    database.unsubscribe_user(6551474276)

    us_exist, _ = myquery(DATABASE_PATH, "SELECT 1 FROM users WHERE user_id = ?;", 6551474276)

    assert not bool(us_exist)
