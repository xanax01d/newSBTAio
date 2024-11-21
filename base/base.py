import sqlite3

from aiogram.utils.link import create_telegram_link

from configs.dictionaries import groupsToTables
from configs.admins import admin_ids
from configs.forParse import days
from datetime import datetime
class BotDB:
    """
    Library, used to perform actions with database by bot
        Available actions:
            - Get information about user
            - Get schedule for needed day from database
            - Ban system (give ban for user, unban, get banned users)
            - Clear databases
            - Get captcha info from special database table
    """
    def create_needed_databases(self):
        """
            Creates the necessary tables in the SQLite database if they do not already exist.
            This method checks for the existence of three tables: `user_status`,
            `users_group`, and `reports`. If any of these tables are missing, they
            will be created with the specified schema. This ensures that the database
            is properly set up for storing user information and reports.
        """
        self.cur.execute("""CREATE TABLE IF NOT EXISTS user_status(
                   user_id INTEGER PRIMARY KEY NOT NULL,
                   user_fn TEXT,
                   banned INTEGER NOT NULL
               )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users_group(
                   user_id INTEGER PRIMARY KEY NOT NULL,
                   user_stage TEXT,
                   user_course TEXT,
                   user_group TEXT,
                   username TEXT,
                   user_fn TEXT,
                   chat_id INTEGER
                   )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS reports(
                id INTEGER PRIMARY KEY NOT NULL,
                username TEXT,
                "group" TEXT,
                day TEXT,
                date TEXT)""")
        self.con.commit()
    def __init__(self,base):
        """
        Initializes the library by establishing a connection to the SQLite database.
        Parameters:
            - base (str) : The file path to the SQLite database. If the file is not exists, a new database will be
            created at this location.
            Example:
                BotDB = BotDB("/path/to/database.db")
        """
        self.con = sqlite3.connect(base)
        self.cur = self.con.cursor()
        self.create_needed_databases()

    def add_user_info(self,user_id,username,user_fn,chat_id):
        """
        Inserts or updates user information in the `users_group` table.

        This method adds a new user or updates an existing user's information
        in the `users_group` table based on the provided user ID. If a user
        with the specified ID already exists, their details will be replaced
        with the new values.
        Parameters:
            user_id (int): The unique identifier for the user. This serves as
                           the primary key in the `users_group` table.
            username (str): The username of the user to be added or updated.
            user_fn (str): The first name of the user.
            chat_id (int): The chat identifier associated with the user.
        Returns:
            None: Commits changes to the database.
        Example:
            BotDB.add_user_info(user_id = 1337, username = "bo_sinn", user_fn = "Bo", chat_id = 1337228)
        """
        self.cur.execute("INSERT or REPLACE INTO users_group (user_id, username, user_fn, chat_id) VALUES (?, ?, ?, ?)",
                         (user_id, username, user_fn, chat_id))
        return self.con.commit()
    def add_user_stage(self,user_id,user_stage):
        self.cur.execute("UPDATE users_group SET user_stage = (?) WHERE user_id = (?)",(user_stage,user_id,))
        return self.con.commit()
    def add_user_course(self,user_id,user_course):
        self.cur.execute("UPDATE users_group SET user_course = (?) WHERE user_id = (?)",(user_course,user_id,))
        return self.con.commit()
    def add_user_group(self,user_id,user_group):
        self.cur.execute("UPDATE users_group SET user_group = (?) WHERE user_id = (?)",(user_group,user_id,))
        return self.con.commit()
    def get_user_group(self,user_id):
        self.cur.execute("SELECT user_group FROM users_group WHERE user_id = (?)",(user_id,))
        return self.cur.fetchall()[0][0]
    def get_schedule(self,day,group):
        scheduleDay = days[day]
        table = groupsToTables.get(group)
        self.cur.execute(f"SELECT schedule FROM {table} WHERE day = ?",(scheduleDay,))
        return self.cur.fetchall()[0][0]
    def close(self):
        self.con.close()
    """
    def add_user_bans(self,user_id,user_ban_status,user_fn):
        self.cur.execute("INSERT OR REPLACE INTO user_status VALUES (?,?,?)",(user_id,user_fn,user_ban_status,))
        return self.con.commit()
    """
    def check_ban(self,user_id):
        self.cur.execute("SELECT banned FROM user_status WHERE user_id = ?",(user_id,))
        return self.cur.fetchone()
    def give_ban(self,user_id):
        if user_id not in admin_ids:
            self.cur.execute("UPDATE user_status SET banned = 1 WHERE user_id = ? ",(user_id,))
            return self.con.commit()
    def unban(self,user_id):
        self.cur.execute("UPDATE user_status SET banned = 0 WHERE user_id = ? ",(user_id,))
        return self.con.commit()
    def get_banned_users(self):
        self.cur.execute("SELECT user_id FROM user_status WHERE banned = ?",(1,))
        result = [i[0] for i in (self.cur.fetchall())]
        return result
    def get_users(self):
        self.cur.execute("SELECT user_fn FROM user_status")
        result = [i[0] for i in (self.cur.fetchall())]
        return result
    def get_user_id_by_username(self,user_fn):
        self.cur.execute("SELECT user_id FROM user_status WHERE user_fn = ?",(user_fn,))
        return self.cur.fetchone()[0]
    def get_banned_user_fns(self):
        self.cur.execute("SELECT user_fn FROM user_status WHERE banned = ?",(1,))
        result = [i[0] for i in (self.cur.fetchall())]
        return result
    def get_users_ids(self):
        self.cur.execute("SELECT chat_id FROM users_group")
        result = [i[0] for i in (self.cur.fetchall())]
        return result
    def add_user_chat_id(self,user_id,chat_id):
        self.cur.execute("INSERT OR REPLACE INTO users_group(user_id,chat_id) VALUES(?,?)",(user_id,chat_id,))
        return self.con.commit()
    def check_chat_id(self,user_id):
        self.cur.execute("SELECT chat_id FROM users_group WHERE user_id = ?",(user_id,))
        data = self.cur.fetchone()
        if data is None:
            return False
        return data
    def clear_users_base(self):
        self.cur.execute("DELETE FROM users_group")
        self.con.commit()
    def clear_ban_base(self):
        self.cur.execute("DELETE FROM user_status")
        self.con.commit()
    def add_report(self,user_id, username, group, day):
        self.cur.execute("INSERT INTO reports VALUES(?,?,?,?,?)",
                         (user_id,username,group,day,(datetime.now().date())))
        return self.con.commit()
    
    def add_captcha_info(self, user_id, captcha):
        self.cur.execute("UPDATE captcha_table SET captcha = ? WHERE id = ?", (captcha, user_id))
        if self.cur.rowcount == 0: 
            self.cur.execute("INSERT INTO captcha_table (id, captcha) VALUES (?, ?)",(user_id, captcha))
        return self.con.commit()
    
    def get_captcha(self,user_id):
        self.cur.execute("SELECT captcha FROM captcha_table WHERE id = ?",(user_id,))
        data = self.cur.fetchone()
        if data is None:
            return False
        return data[0]
