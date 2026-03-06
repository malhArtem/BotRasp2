import aiosqlite

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any
from pydantic import TypeAdapter

import core.models as models
import core.errors as errors

async def create_tables(db: DataBase):
    async with db.db_cursor() as cursor:
        await TeachersBase.create_table(cursor)
        await UsersBase.create_table(cursor)
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
            """CREATE TABLE IF NOT EXISTS teachers (
                teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                FIO TEXT
            )"""
        )

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
            """CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                name TEXT,
                year INTEGER,
                group_code TEXT,
                is_teacher INTEGER,
                teacher INTEGER,

                FOREIGN KEY (teacher) REFERENCES teachers (teacher_id) 
                ON DELETE SET NULL
            )"""
        )

    @staticmethod
    async def create_profile(cursor: aiosqlite.Cursor, profile_data: models.UserStudent | models.UserTeacher) -> None:
        await cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, name, year, group_code, is_teacher, teacher) \
                VALUES (?, ?, ?, ?, ?, ?, ?)", (
                    profile_data.id,
                    profile_data.username,
                    profile_data.full_name,
                    profile_data.year,
                    profile_data.group,
                    profile_data.is_teacher,
                    profile_data.teacher_id,
                )
        )

    @staticmethod
    async def update_profile(cursor: aiosqlite.Cursor, profile_data: models.UserStudent | models.UserTeacher) -> None:
        await cursor.execute(
            "UPDATE users SET username = ?, name = ?, year = ?, group_code = ?, is_teacher = ?, teacher = ? WHERE user_id = ?",
            (
                profile_data.username,
                profile_data.full_name,
                profile_data.year,
                profile_data.group,
                profile_data.is_teacher,
                profile_data.teacher_id,
                profile_data.id,
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
        await cursor.execute(
            """CREATE TABLE IF NOT EXISTS shedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_code TEXT,
                day TEXT,
                time TEXT,
                subject TEXT,
                auditory TEXT,
                week_type TEXT,
                teacher INTEGER,

                UNIQUE(group_code, day, time, week_type),
                FOREIGN KEY (teacher) REFERENCES teachers (teacher_id) ON DELETE CASCADE
            )"""
        )

    @staticmethod
    async def set_pair(cursor: aiosqlite.Cursor, pair: models.Pair) -> None:
        await cursor.execute(
            "REPLACE INTO shedules (group_code, day, time, subject, auditory, week_type, teacher) \
                VALUES (?, ?, ?, ?, ?, ?)", (
                    pair.group,
                    pair.day,
                    pair.time.isoformat(),
                    pair.subject,
                    pair.auditory,
                    pair.week_type,
                    pair.teacher,
                )
        )

    @staticmethod
    async def get_student_pairs(cursor: aiosqlite.Cursor, group_code: str) -> list[models.Pair]:
        await cursor.execute(
            "SELECT group_code, day, time, subject, auditory, week_type, teachers.FIO AS teacher FROM shedules \
            JOIN teachers ON shedules.teacher = teachers.teacher_id \
            WHERE group_code = ?", (group_code,)
        )
        pairs = await cursor.fetchall()
        return TypeAdapter(list[models.Pair]).validate_python(pairs)
    
    @staticmethod
    async def get_teacher_pairs(cursor: aiosqlite.Cursor, teacher_id: int) -> list[models.Pair]:
        await cursor.execute(
            "SELECT shedules.group_code, shedules.day, shedules.time, shedules.subject, \
                     shedules.auditory, shedules.week_type, teachers.FIO as teacher FROM teachers \
            JOIN shedules ON shedules.teacher = teachers.teacher_id \
            WHERE teachers.teacher_id = ?", (teacher_id,)
        )
        pairs = await cursor.fetchall()
        return TypeAdapter(list[models.Pair]).validate_python(pairs)
    
    @staticmethod
    async def get_groups(cursor: aiosqlite.Cursor) -> list[dict[str, str]]:
        '''Returns: group'''
        await cursor.execute("SELECT group_code FROM shedules GROUP BY group_code")
        return await cursor.fetchall()