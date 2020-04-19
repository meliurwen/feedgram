#!/usr/bin/env python3

from os import path, remove
import sqlite3
from feedgram.lib.database import MyDatabase


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


def test_database_check_number_subscribtions():

    assert path.exists(DATABASE_PATH)
    database = MyDatabase(DATABASE_PATH)

    num_sub = database.check_number_subscribtions(6551474276)

    assert num_sub["user_id"] == 6551474276

    assert num_sub["actual_registrations"] == 0


SUB_BY_POST_LINK = {"social": "instagram",
                    "username": "il_post",
                    "internal_id": None,
                    "social_id": None,
                    "link": "www.instagram.com/il_post",
                    "data": {},
                    "subStatus": "social_id_not_present"
                    }

SUB_BY_POST_LINK2 = {"social": "instagram",
                     "username": "il_post",
                     "internal_id": "1769583068",
                     "social_id": None,
                     "link": "www.instagram.com/il_post",
                     "data": {},
                     "subStatus": "subscribable",
                     "title": "il_post",
                     "status": "public"
                     }


def test_database_get_first_social_id_from_internal_user_social_and_if_present_subscribe1():
    '''
        Tentativo di inscrizione ad un social tramite link senza forzarne
        l'inserimento nel database del social e relazione con l'utente
            => manca il social nel database
            ==> non possiamo inserire la relazione (non forzato)
            ===> dovremo forzare l'inserimento di entrambi
    '''
    assert path.exists(DATABASE_PATH)
    database = MyDatabase(DATABASE_PATH)

    mresult = database.get_first_social_id_from_internal_user_social_and_if_present_subscribe(6551474276, SUB_BY_POST_LINK, False)

    assert mresult['subStatus'] == 'notInDatabase'


def test_database_get_first_social_id_from_internal_user_social_and_if_present_subscribe2():
    '''
        tentativo di inscrizione ad un social tramite link forzando
        l'inserimento del social e aggungengo la relazione con l'utente
            => manca il social nel database
            ==> forziamo nel database il social e la relazione con l'utente
    '''
    assert path.exists(DATABASE_PATH)
    database = MyDatabase(DATABASE_PATH)

    mresult = database.get_first_social_id_from_internal_user_social_and_if_present_subscribe(6551474276, SUB_BY_POST_LINK2, True)
    assert mresult['social_id'] == 1
    assert mresult['subStatus'] == 'CreatedSocialAccAndSubscribed'


def test_database_get_first_social_id_from_internal_user_social_and_if_present_subscribe3():
    '''
        Tentativo di inscrizione ad un social tramite link senza forzarne
        l'inserimento nel database del social e relazione con l'utente
            => il social è presente nel database
            ==> estraggo le informazioni del social dal database
            ===> aggungiamo la relazione tra l'utente e il social
    '''
    assert path.exists(DATABASE_PATH)
    database = MyDatabase(DATABASE_PATH)

    mresult = database.get_first_social_id_from_internal_user_social_and_if_present_subscribe(57356765765, SUB_BY_POST_LINK, False)
    assert mresult['internal_id'] == '1769583068'
    assert mresult['social_id'] == 1
    assert mresult['subStatus'] == 'JustSubscribed'


def test_database_get_first_social_id_from_internal_user_social_and_if_present_subscribe4():
    '''
        Tentativo di ri-inscrizione ad un social
    '''
    assert path.exists(DATABASE_PATH)
    database = MyDatabase(DATABASE_PATH)

    mresult = database.get_first_social_id_from_internal_user_social_and_if_present_subscribe(6551474276, SUB_BY_POST_LINK, False)

    assert mresult['subStatus'] == 'AlreadySubscribed'


def test_database_create_dict_of_user_ids_and_socials():

    assert path.exists(DATABASE_PATH)
    database = MyDatabase(DATABASE_PATH)

    res = database.create_dict_of_user_ids_and_socials

    il_post = {"internal_id": "1769583068",
               "username": "il_post",
               "title": "il_post",
               "retreive_time": "1587222607",
               "status": "public"
               }

    # Il retreive_time cambia ogni volta che si lanciano i test,
    # dato che ad ogni lancio dei test il database viene resettato

    assert res['social_accounts']['instagram'][0]['internal_id'] == il_post['internal_id']
    assert res['social_accounts']['instagram'][0]['username'] == il_post['username']
    assert res['social_accounts']['instagram'][0]['title'] == il_post['title']
    assert res['social_accounts']['instagram'][0]['status'] == il_post['status']

    assert res['subscriptions']['instagram'][il_post['internal_id']] == ['6551474276', '57356765765']


QUERY_TODO_UPDATE = {"update": [{"type": "retreive_time",
                                 "social": "instagram",
                                 "internal_id": "1769583068",
                                 "retreive_time": "999999999"
                                 },
                                {"type": "status",
                                 "social": "instagram",
                                 "internal_id": "1769583068",
                                 "status": "private"
                                 }
                                ],
                     "delete": []
                     }


def test_database_process_messages_queries1():

    assert path.exists(DATABASE_PATH)
    database = MyDatabase(DATABASE_PATH)

    database.process_messages_queries(QUERY_TODO_UPDATE)

    res, _ = myquery(DATABASE_PATH,
                     "SELECT retreive_time, status FROM socials WHERE social = ? AND internal_id = ?",
                     'instagram', 1769583068)

    assert res[0] == 999999999
    assert res[1] == 'private'


QUERY_TODO_DELETE = {"delete": [{"type": "socialAccount",
                                 "social": "instagram",
                                 "internal_id": "1769583068"
                                 }
                                ],
                     "update": []
                     }


def test_database_process_messages_queries2():

    assert path.exists(DATABASE_PATH)
    database = MyDatabase(DATABASE_PATH)

    database.process_messages_queries(QUERY_TODO_DELETE)

    res, _ = myquery(DATABASE_PATH, "SELECT count() FROM registrations")

    assert res[0] == 0

    res, _ = myquery(DATABASE_PATH, "SELECT count() FROM socials")

    assert res[0] == 0


def test_database_clean_dead_subscriptions():

    assert path.exists(DATABASE_PATH)
    database = MyDatabase(DATABASE_PATH)

    # creo una sottoscrizione ad un social di un utente fintizzio
    _ = database.get_first_social_id_from_internal_user_social_and_if_present_subscribe(1234567890, SUB_BY_POST_LINK2, True)

    # rimuovo la relazione tra l'utente e il social
    myquery(DATABASE_PATH, "DELETE FROM registrations WHERE user_id = ?", 1234567890)
    # verifico che sia stata rimossa
    res, _ = myquery(DATABASE_PATH, "SELECT count() FROM registrations")
    assert res[0] == 0

    # verifico che il social sia ancora presente nel database
    res, _ = myquery(DATABASE_PATH, "SELECT count() FROM socials")
    assert res[0] == 1

    database.clean_dead_subscriptions()

    # verifico che il social sia stato rimosso dal database perchè nessuno è inscritto
    res, _ = myquery(DATABASE_PATH, "SELECT count() FROM socials")
    assert res[0] == 0


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
