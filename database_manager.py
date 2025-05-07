import mysql.connector
import dotenv
import os
from set import Set
from item import Item

db_name = "pokevision"
set_table = "sets"
item_table = "items"

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
		" (id int NOT NULL AUTO_INCREMENT, name VARCHAR(255) NOT NULL, url VARCHAR(255) NOT NULL, " +
		"PRIMARY KEY (id))")
	cursor.close()
	connector.close()

def create_item_table():
	connector = get_connector(db_name)
	cursor = connector.cursor()

	cursor.execute(
		"CREATE TABLE " + item_table + 
		" (id varchar(20) NOT NULL, name VARCHAR(255) NOT NULL, url VARCHAR(255) NOT NULL, set_id int NOT NULL, " +
		"PRIMARY KEY (id), " +
		"FOREIGN KEY (set_id) REFERENCES " + set_table + "(id))")
	connector.close()

def insert_set(set: Set):
	connector = get_connector(db_name)
	cursor = connector.cursor()

	cursor.execute(
		"INSERT INTO " + set_table + " (name, url) "
		"VALUES (%s, %s)", (set.name, set.url,))
	connector.commit()
	cursor.close()
	connector.close()

def insert_items(items: list[Item]):
	connector = get_connector(db_name)
	cursor = connector.cursor()

	for item in items:
		cursor.execute(
			"INSERT INTO " + item_table + " (id, name, url, set_id) "
			"VALUES (%s, %s, %s, %s)", (item.id, item.name, item.url, item.set_id,))
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
