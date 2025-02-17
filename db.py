import sqlite3 as sq

from aiogram import types


class DB:

    def create_table_users(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users
                             (user_id TEXT, username TEXT, name TEXT, kurs INTEGER, 
                             groupp TEXT, st_or_teach INTEGER, teacher TEXT)""")

        self.db.commit()


    def __init__(self, name: str):
        self.db = sq.connect(name + '.db')
        self.cur = self.db.cursor()
        self.create_table_users()


    def create_table_rasp(self, kurs):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS '{}' 
                          (day TEXT, time TEXT,specialty TEXT, groupp TEXT, subj1 TEXT, 
                          teach1 TEXT, clas1 TEXT, subj2 TEXT, teach3 TEXT, clas2 TEXT)""".format(kurs))

        self.db.commit()


    async def create_profile_student(self, message: types.CallbackQuery, kurs, group):
        self.cur.execute("SELECT 1 FROM users WHERE user_id == '{}'"
                    .format(message.from_user.id))

        user = self.cur.fetchone()

        if not user:
            self.cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?)",
                        (message.from_user.id, message.from_user.username, message.from_user.full_name, kurs, group, 0, ''))
            self.db.commit()


    async def create_profile_teacher(self, message: types.CallbackQuery, teacher):
        self.cur.execute("SELECT 1 FROM users WHERE user_id == '{}'"
                    .format(message.from_user.id))
        user = self.cur.fetchone()

        if not user:
            self.cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?)",
                        (message.from_user.id, message.from_user.username, message.from_user.full_name, 0, 0, 1, teacher))
            self.db.commit()


    async def update_profile(self, callback_query: types.CallbackQuery, user: list):
        self.cur.execute(
            "UPDATE users SET username = '{}', name = '{}', kurs = '{}', groupp = '{}', "
            "st_or_teach = '{}', teacher = '{}' WHERE user_id = '{}'"
            .format(callback_query.from_user.username, callback_query.from_user.full_name, user[0], user[1], user[2],
                    user[3], callback_query.from_user.id))
        self.db.commit()


    async def delete_profile(self, user_id):
        self.cur.execute("DELETE FROM users WHERE user_id = '{}'".format(user_id))
        self.db.commit()


    def add_rasp(self, raw_table: list, kurs):
        self.cur.execute("INSERT INTO '{}' VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(kurs),
                    (raw_table[0], raw_table[1], raw_table[2], raw_table[3], raw_table[4], raw_table[5], raw_table[6],
                     raw_table[7], raw_table[8], raw_table[9]))
        self.db.commit()


    async def get_rasp(self, day, kurs, group: str):
        if kurs != 'СПО':
            split_group = group.split()
            specialty = split_group[0]
            group_cut = split_group[-1]
            print(group)
            if specialty == group:
                self.cur.execute("SELECT * FROM '{}' WHERE day = '{}' AND groupp = '{}'".format(kurs, day, group_cut))
            elif group[-1].isdigit() or group[-1] == ')':
                self.cur.execute("SELECT * FROM '{}' WHERE day = '{}' AND groupp = '{}'".format(kurs, day, group))
            else:
                self.cur.execute("SELECT * FROM '{}' WHERE day = '{}' AND groupp = '{}' AND specialty = '{}'".format(kurs, day,
                                                                                                                group_cut,
                                                                                                                specialty))

        else:
            self.cur.execute("SELECT * FROM '{}' WHERE day = '{}' AND groupp = '{}'".format(kurs, day, group))

        day_rasp = self.cur.fetchall()
        return day_rasp


    async def get_teachers(self):
        kurses = await self.get_kurs()
        teachers = list()
        for kurs in kurses:
            if kurs[1] != 'users' and not ('old' in kurs[1]):
                self.cur.execute("SELECT DISTINCT teach1 FROM '{}' WHERE teach1 IS NOT NULL".format(kurs[1]))
                teachers.extend(self.cur.fetchall())
                self.cur.execute("SELECT DISTINCT teach3 FROM '{}' WHERE teach3 IS NOT NULL".format(kurs[1]))
                teachers.extend(self.cur.fetchall())
        unic_teach = list(set(teachers))
        return unic_teach


    async def get_user(self, user_id):
        self.cur.execute("SELECT kurs, groupp, st_or_teach, teacher FROM users WHERE user_id = '{}'".format(user_id))
        user = self.cur.fetchone()
        return user


    async def get_kurs(self):
        self.cur.execute("SELECT * FROM sqlite_master WHERE type = 'table'")
        return self.cur.fetchall()


    async def get_groups(self, kurs):
        self.cur.execute("SELECT DISTINCT groupp, specialty FROM '{}'".format(kurs))
        groups = self.cur.fetchall()
        self.db.commit()
        return groups


    async def rename_tables(self, kurs):
        self.cur.execute("ALTER TABLE '{}' RENAME TO '{}'".format(kurs, kurs + '_old'))
        self.db.commit()


    async def delete_old(self):
        tables = await self.get_kurs()
        for table in tables:
            if 'old' in table[1] and "СПО" not in table[1]:
                self.cur.execute('DROP TABLE IF EXISTS "{}"'.format(table[1]))
                self.db.commit()


    async def delete_old_spo(self):
        self.cur.execute('DROP TABLE IF EXISTS "СПО_old"')
        self.db.commit()