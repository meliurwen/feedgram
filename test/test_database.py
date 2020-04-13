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


def test_database_creation():

    # creo il database che non esiste con le tabelle base

    # Nome del file per il test
    database_path = "./test/databseTest.sqlite3"

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
    database = MyDatabase(database_path)

    # state = database.status

    # verifico che il file sia stato creato
    assert path.exists(database_path)

    # Verifico che lo stato della classe sia quello coretto
    assert database.status == 1


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
