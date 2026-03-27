import aiosqlite

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any
from pydantic import TypeAdapter

import core.models as models
from core import errors

async def create_tables(db: DataBase):
    async with db.db_cursor() as cursor:
        await TeachersBase.create_table(cursor)
        await GroupsBase.create_table(cursor)
        await UsersBase.create_table(cursor) # создаёт ссылки на TeachersBase & GroupsBase!
        await ShedulesBase.create_table(cursor)

class DataBase:
    def __init__(self, path: str):
        self.path = path

    @staticmethod
    def _dict_factory(cursor: aiosqlite.Cursor, row: aiosqlite.Row) -> dict[str, Any]:
        fields = [column[0] for column in cursor.description]
        return dict(zip(fields, row))

    @asynccontextmanager
    async def db_cursor(self, commit: bool = True) -> AsyncGenerator[aiosqlite.Cursor, None]:
        async with aiosqlite.connect(self.path) as connection:
            connection.row_factory = self._dict_factory
            cursor = await connection.cursor()
            yield cursor

            if commit:
                await connection.commit()


class TeachersBase(DataBase):

    @staticmethod
    async def create_table(cursor: aiosqlite.Cursor) -> None:
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                FIO TEXT
            )"""
        )

    @staticmethod
    async def add_teacher(cursor: aiosqlite.Cursor, teacher: models.Teacher) -> None:
        await cursor.execute("INSERT OR IGNORE INTO teachers (FIO) VALUES (?)", (teacher.FIO,))
        if not cursor.rowcount:
            raise errors.TeacherAlreadyExistsError()

    @staticmethod
    async def get_teachers(cursor: aiosqlite.Cursor) -> list[models.Teacher]:
        await cursor.execute("SELECT * FROM teachers")
        teachers = await cursor.fetchall()
        return TypeAdapter(list[models.Teacher]).validate_python(teachers)


class UsersBase(DataBase):

    @staticmethod
    async def create_table(cursor: aiosqlite.Cursor) -> None:
        await cursor.execute("PRAGMA foreign_keys = ON")
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                group_id INTEGER,
                teacher_id INTEGER,

                FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id) ON DELETE SET NULL,
                FOREIGN KEY (group_id) REFERENCES groups (group_id) ON DELETE SET NULL
            )"""
        )

    @staticmethod
    async def create_profile(cursor: aiosqlite.Cursor, profile_data: models.UserProfile) -> None:
        await cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, group_id, teacher_id) \
                VALUES (?, ?, ?, ?, ?)", (
                    profile_data.user_id,
                    profile_data.username,
                    profile_data.full_name,
                    profile_data.group_id,
                    profile_data.teacher_id,
                )
        )
        if not cursor.rowcount:
            raise errors.UserAlreadyExistsError()

    @staticmethod
    async def update_profile(cursor: aiosqlite.Cursor, profile_data: models.UserProfile) -> None:
        await cursor.execute(
            "UPDATE users SET username = ?, full_name = ?, group_id = ?, teacher_id = ? WHERE user_id = ?",
            (
                profile_data.username,
                profile_data.full_name,
                profile_data.group_id,
                profile_data.teacher_id,
                profile_data.user_id,
            )
        )
        if not cursor.rowcount:
            raise errors.UserNotFoundError()
    
    @staticmethod
    async def get_profile(cursor: aiosqlite.Cursor, user_id: str) -> models.UserProfile:
        await cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        profile = await cursor.fetchone()
        if not profile: raise errors.UserNotFoundError()
        return models.UserProfile.model_validate(profile)
    
    @staticmethod
    async def delete_profile(cursor: aiosqlite.Cursor, user_id: str) -> None:
        await cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))


class ShedulesBase(DataBase):

    @staticmethod
    async def create_table(cursor: aiosqlite.Cursor) -> None:
        await cursor.execute("PRAGMA foreign_keys = ON")
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pairs (
                pair_id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT,
                time TEXT,
                subject TEXT,
                auditory TEXT,
                week_type TEXT,
                group_id INTEGER,
                teacher_id INTEGER,

                UNIQUE(group_id, day, time, week_type),
                FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups (group_id) ON DELETE CASCADE
            )"""
        )

    @staticmethod
    async def set_pair(cursor: aiosqlite.Cursor, pair: models.Pair) -> None:
        await cursor.execute(
            "REPLACE INTO pairs (day, time, subject, auditory, week_type, group_id, teacher_id) \
                VALUES (?, ?, ?, ?, ?, ?, ?)", (
                    pair.day,
                    pair.time.isoformat(),
                    pair.subject,
                    pair.auditory,
                    pair.week_type,
                    pair.group_id,
                    pair.teacher_id,
                )
        )

    @staticmethod
    async def get_student_pairs(cursor: aiosqlite.Cursor, group_id: int) -> list[models.StudentPair]:
        await cursor.execute(
            """
            SELECT pairs.*, teachers.FIO AS teacher_fio FROM pairs
            JOIN teachers ON pairs.teacher_id = teachers.teacher_id
            WHERE pairs.group_id = ?
            """, (group_id,)
        )
        pairs = await cursor.fetchall()
        return TypeAdapter(list[models.StudentPair]).validate_python(pairs)
    
    @staticmethod
    async def get_teacher_pairs(cursor: aiosqlite.Cursor, teacher_id: int) -> list[models.TeacherPair]:
        await cursor.execute(
            """
            SELECT pairs.*, groups.code AS group_code, groups.year FROM pairs
            JOIN groups ON pairs.group_id = groups.group_id
            WHERE pairs.teacher_id = ?
            """, (teacher_id,)
        )
        pairs = await cursor.fetchall()
        return TypeAdapter(list[models.TeacherPair]).validate_python(pairs)
    

class GroupsBase(DataBase):

    @staticmethod
    async def create_table(cursor: aiosqlite.Cursor) -> None:
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                year INTEGER,
                code TEXT,

                UNIQUE(level, year, code)
            )"""
        )

    @staticmethod
    async def create_group(cursor: aiosqlite.Cursor, group: models.Group) -> None:
        await cursor.execute(
            "INSERT OR IGNORE INTO groups (level, year, code) VALUES (?, ?, ?)",
            (group.level, group.year, group.code,)
        )
        if not cursor.rowcount:
            raise errors.GroupAlreadyExistsError()
        
    @staticmethod
    async def get_group(cursor: aiosqlite.Cursor, group_id: int) -> models.Group:
        await cursor.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
        group = await cursor.fetchone()
        if not group: raise errors.GroupNotFoundError()
        return models.Group.model_validate(group)
    
    @staticmethod
    async def get_groups(cursor: aiosqlite.Cursor) -> list[models.Group]:
        await cursor.execute("SELECT * FROM groups")
        groups = await cursor.fetchall()
        return TypeAdapter(list[models.Group]).validate_python(groups)