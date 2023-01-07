import pymysql

user = '***'
password = '***'
db_name = '***'
host = 'sql11.freesqldatabase.com'
apk_id = ""
photos = []


class DB:
    connection = None
    cur_msg = 0

    def __init__(self):
        selection = "SELECT * FROM `survey`"
        cursor = self.query(selection)
        rows = cursor.fetchall()
        self.cur_msg = 0
        for row in rows:
            self.cur_msg = max(self.cur_msg, int(row['msgid']))

    def connect(self):
        self.connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )

    def query(self, sql):
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        return cursor

    def create_table(self, name):
        create = f"CREATE TABLE {name} (id int AUTO_INCREMENT, name varchar(8000) COLLATE utf8_general_ci, text varchar(8000) COLLATE utf8_general_ci, PRIMARY KEY (id))"
        self.query(create)

    def all_feedback(self):
        selection = "SELECT * FROM `survey`"
        cursor = self.query(selection)
        rows = cursor.fetchall()
        return rows

    def clear(self, name):
        clear_query = f"DELETE FROM `{name}`"
        self.query(clear_query)

    def add_feedback(self, username, text, mark):
        self.cur_msg += 1
        insert_query = f"INSERT INTO `survey` (name, text, mark, msgid) VALUES ('{username}', '{text}', '{mark}', '{self.cur_msg}')"
        self.query(insert_query)

    def update_photos(self):
        global photos
        self.clear("photos")
        for photo in photos:
            update_query = f"INSERT INTO `photos` (file_id) VALUES ('{photo}')"
            self.query(update_query)
        photos.clear()

    def update_game(self):
        global apk_id
        self.clear("apk")
        update_query = f"INSERT INTO `apk` (file_id) VALUES ('{apk_id}')"
        self.query(update_query)
        apk_id = ""

    def get_photos(self):
        get_query = "SELECT * FROM `photos`"
        cursor = self.query(get_query)
        return cursor.fetchall()

    def get_apk(self):
        get_query = "SELECT * FROM `apk`"
        cursor = self.query(get_query)
        return cursor.fetchall()

    def remove(self, ind):
        try:
            remove_query = f"DELETE FROM survey WHERE msgid = '{ind}'"
            self.query(remove_query)
        except:
            return


class User:
    username = ''
    comment = ''
    mark = 0
    fullname = ''
    isTyping = False
    admin_enter = False
    updating_photos = False
    updating_game = False

    def __init__(self, fullname):
        self.fullname = fullname

    def reset(self):
        self.username = ''
        self.comment = ''
        self.isTyping = False
        self.admin_enter = False
        self.mark = 0
        self.updating_photos = False
        self.updating_game = False
