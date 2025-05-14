import mysql.connector
import dotenv
import os
from set import Set
from item import Item
from item_details import ItemDetails

db_name = "pokevision"
set_table = "sets"
item_table = "items"
item_details_table = "item_details"

def get_connector(database: str=None):
    dotenv.load_dotenv()
    user = os.getenv('user')
    password = os.getenv('pass')
    host = os.getenv('host')

    if database is None:
        db = mysql.connector.connect(
          host=host,
          user=user,
          password=password,
        )
    else:
        db = mysql.connector.connect(
          host=host,
          user=user,
          password=password,
          database=database,
        )

    return db

def create_db():
    connector = get_connector()
    cursor = connector.cursor()
    cursor.execute("CREATE DATABASE " + db_name)
    cursor.close()
    connector.close()

def drop_all():
    connector = get_connector()
    cursor = connector.cursor()

    # drop db
    try:
        cursor.execute("DROP DATABASE " + db_name)
    except:
        print("Error dropping db")

    cursor.close()
    connector.close()


def create_set_table():
    connector = get_connector(db_name)
    cursor = connector.cursor()

    cursor.execute(
        "CREATE TABLE " + set_table +
        " (id INT NOT NULL AUTO_INCREMENT, name VARCHAR(255) NOT NULL, url VARCHAR(255) NOT NULL UNIQUE, " +
        "PRIMARY KEY (id))")
    cursor.close()
    connector.close()

def create_item_table():
    connector = get_connector(db_name)
    cursor = connector.cursor()

    cursor.execute(
        "CREATE TABLE " + item_table + 
        " (id INT NOT NULL, name VARCHAR(255) NOT NULL, url VARCHAR(255) NOT NULL, set_id INT NOT NULL, " +
        "PRIMARY KEY (id), " +
        "FOREIGN KEY (set_id) REFERENCES " + set_table + "(id))")
    connector.close()

def create_item_details_table():
    connector = get_connector(db_name)
    cursor = connector.cursor()

    cursor.execute(
        "CREATE TABLE " + item_details_table + 
        " (item_id INT NOT NULL, ungraded_price DECIMAL(10, 2), " +
        "psa_1_pop INT, psa_1_price DECIMAL(10, 2), " +
        "psa_2_pop INT, psa_2_price DECIMAL(10, 2), " +
        "psa_3_pop INT, psa_3_price DECIMAL(10, 2), " +
        "psa_4_pop INT, psa_4_price DECIMAL(10, 2), " +
        "psa_5_pop INT, psa_5_price DECIMAL(10, 2), " +
        "psa_6_pop INT, psa_6_price DECIMAL(10, 2), " +
        "psa_7_pop INT, psa_7_price DECIMAL(10, 2), " +
        "psa_8_pop INT, psa_8_price DECIMAL(10, 2), " +
        "psa_9_pop INT, psa_9_price DECIMAL(10, 2), " +
        "psa_10_pop INT, psa_10_price DECIMAL(10, 2), " +
        "PRIMARY KEY (item_id), " +
        "FOREIGN KEY (item_id) REFERENCES " + item_table + "(id))")
    connector.close()

def insert_set(set: Set):
    connector = get_connector(db_name)
    cursor = connector.cursor()

    cursor.execute(
        "INSERT IGNORE INTO " + set_table + " (name, url) "
        "VALUES (%s, %s)", (set.name, set.url,))
    connector.commit()
    cursor.close()
    connector.close()

def insert_items(items: list[Item]):
    connector = get_connector(db_name)
    cursor = connector.cursor()

    for item in items:
        cursor.execute(
            "INSERT IGNORE INTO " + item_table + " (id, name, url, set_id) "
            "VALUES (%s, %s, %s, %s)", (item.id, item.name, item.url, item.set_id,))
    connector.commit()
    cursor.close()
    connector.close()

def insert_item_details(items_details: list[ItemDetails]):
    connector = get_connector(db_name)
    cursor = connector.cursor()

    for item_details in items_details:
        cursor.execute(
            "INSERT INTO " + item_details_table + " (item_id, ungraded_price, " +
            "psa_1_pop, psa_1_price, " +
            "psa_2_pop, psa_2_price, " +
            "psa_3_pop, psa_3_price, " +
            "psa_4_pop, psa_4_price, " +
            "psa_5_pop, psa_5_price, " +
            "psa_6_pop, psa_6_price, " +
            "psa_7_pop, psa_7_price, " +
            "psa_8_pop, psa_8_price, " +
            "psa_9_pop, psa_9_price, " +
            "psa_10_pop, psa_10_price)" +
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" +
            "ON DUPLICATE KEY UPDATE " +
            "ungraded_price = VALUES(ungraded_price), " +
            "psa_1_pop = VALUES(psa_1_pop), psa_1_price = VALUES(psa_1_price), " +
            "psa_2_pop = VALUES(psa_2_pop), psa_2_price = VALUES(psa_2_price), " +
            "psa_3_pop = VALUES(psa_3_pop), psa_3_price = VALUES(psa_3_price), " +
            "psa_4_pop = VALUES(psa_4_pop), psa_4_price = VALUES(psa_4_price), " +
            "psa_5_pop = VALUES(psa_5_pop), psa_5_price = VALUES(psa_5_price), " +
            "psa_6_pop = VALUES(psa_6_pop), psa_6_price = VALUES(psa_6_price), " +
            "psa_7_pop = VALUES(psa_7_pop), psa_7_price = VALUES(psa_7_price), " +
            "psa_8_pop = VALUES(psa_8_pop), psa_8_price = VALUES(psa_8_price), " +
            "psa_9_pop = VALUES(psa_9_pop), psa_9_price = VALUES(psa_9_price), " +
            "psa_10_pop = VALUES(psa_10_pop), psa_10_price = VALUES(psa_10_price)",
            (item_details.item_id, item_details.ungraded_price,
                item_details.psa_1_pop, item_details.psa_1_price,
                item_details.psa_2_pop, item_details.psa_2_price,
                item_details.psa_3_pop, item_details.psa_3_price,
                item_details.psa_4_pop, item_details.psa_4_price,
                item_details.psa_5_pop, item_details.psa_5_price,
                item_details.psa_6_pop, item_details.psa_6_price,
                item_details.psa_7_pop, item_details.psa_7_price,
                item_details.psa_8_pop, item_details.psa_8_price,
                item_details.psa_9_pop, item_details.psa_9_price,
                item_details.psa_10_pop, item_details.psa_10_price,))
    connector.commit()
    cursor.close()
    connector.close()

def get_sets_from_db() -> list[Set]:
    connector = get_connector(db_name)
    cursor = connector.cursor()

    cursor.execute(
        "SELECT id, name, url " + 
        "FROM " + set_table)

    sets = []
    for (id, name, url) in cursor:
        sets.append(Set(id, name, url))    

    cursor.close()
    connector.close()

    return sets

def get_items_from_db(s_id: str=None) -> list[Item]:
    connector = get_connector(db_name)
    cursor = connector.cursor()

    cursor.execute(
        "SELECT id, name, url, set_id " + 
        "FROM " + item_table + ("" if s_id is None else " where set_id=" + str(s_id)))

    items = []
    for (id, name, url, set_id) in cursor:
        items.append(Item(id, name, url, set_id))    

    cursor.close()
    connector.close()

    return items
