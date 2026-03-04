import aiosqlite

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Iterable

import models
import errors

async def create_tables(base_path: str):
    db = DataBase(base_path)
    async with db.db_cursor() as cursor:
        await TeachersBase.create_table(cursor)
        await UsersBase.create_table(cursor)
        await ShedulesBase.create_table(cursor)

class DataBase:
    def __init__(self, path: str):
        self.path = path

    @asynccontextmanager
    async def db_cursor(self, commit: bool = True) -> AsyncGenerator[aiosqlite.Cursor, None]:
        async with aiosqlite.connect(self.path) as connection:
            cursor = await connection.cursor()
            yield cursor

            if commit:
                await connection.commit()


class TeachersBase:

    @staticmethod
    async def create_table(cursor: aiosqlite.Cursor) -> None:
        await cursor.execute(
            """CREATE TABLE IF NOT EXISTS teachers (
                teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                FIO TEXT
            )"""
        )

    @staticmethod
    async def get_teachers(cursor: aiosqlite.Cursor) -> Iterable[aiosqlite.Row]:
        await cursor.execute("SELECT * FROM teachers")
        return await cursor.fetchall()


class UsersBase:

    @staticmethod
    async def create_table(cursor: aiosqlite.Cursor) -> None:
        await cursor.execute("PRAGMA foreign_keys = ON")
        await cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                name TEXT,
                year INTEGER,
                groupp TEXT,
                is_teacher INTEGER,
                teacher INTEGER,

                FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id) 
                ON DELETE SET NULL
            )"""
        )

    @staticmethod
    async def create_profile(cursor: aiosqlite.Cursor, profile_data: models.Student | models.Teacher) -> None:
        await cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, name, year, groupp, is_teacher, teacher) \
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
    async def update_profile(cursor: aiosqlite.Cursor, profile_data: models.Student | models.Teacher) -> None:
        await cursor.execute(
            "UPDATE users SET username = ?, name = ?, year = ?, groupp = ?, is_teacher = ?, teacher = ? WHERE user_id = ?",
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
    async def get_profile(cursor: aiosqlite.Cursor, user_id: str) -> aiosqlite.Row:
        await cursor.execute("SELECT year, groupp, is_teacher, teacher FROM users WHERE user_id = ?", (user_id,))
        return await cursor.fetchone()
    
    @staticmethod
    async def delete_profile(cursor: aiosqlite.Cursor, user_id: str) -> None:
        await cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))


class ShedulesBase:

    @staticmethod
    async def create_table(cursor: aiosqlite.Cursor) -> None:
        await cursor.execute(
            """CREATE TABLE IF NOT EXISTS shedules (
                group_code TEXT,
                day TEXT,
                time TEXT,
                subject TEXT,
                auditory TEXT,
                teacher TEXT,
                UNIQUE(group_code, day, time)
            )"""
        )

    @staticmethod
    async def set_pair(cursor: aiosqlite.Cursor, pair: models.Pair) -> None:
        await cursor.execute(
            "REPLACE INTO shedules (group_code, day, time, subject, auditory, teacher) \
                VALUES (?, ?, ?, ?, ?, ?)", (
                    pair.group,
                    pair.day,
                    pair.time.isoformat(),
                    pair.subject,
                    pair.auditory,
                    pair.teacher,
                )
        )

    @staticmethod
    async def get_shedule(cursor: aiosqlite.Cursor, group_code: str) -> Iterable[aiosqlite.Row]:
        await cursor.execute(
            "SELECT day, time, subject, auditory, teacher FROM shedules WHERE group_code = ?", (group_code,)
        )
        return await cursor.fetchall()
    
    @staticmethod
    async def get_groups(cursor: aiosqlite.Cursor) -> Iterable[aiosqlite.Row]:
        await cursor.execute("SELECT group_code FROM shedules GROUP BY group_code")
        return await cursor.fetchall()