import asyncio
import base64
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator, List
from aiomysql import connect, connection
from pymysql.err import IntegrityError
from bot import utils
import config

# Функция для подключения к БД
@asynccontextmanager
async def get_db_session() -> AsyncGenerator[connection.Connection, None]:
    conn = await connect(
        user=config.DB_USERNAME,
        password=config.DB_PASSWORD,
        db=config.DB_NAME,
        host=config.DB_HOST,
        port=int(config.DB_PORT)
    )

    yield conn  # Передаем управление подключение


async def get_user(tg_id: int) -> set:
    async with get_db_session() as session:
        async with session.cursor() as cursor:
            await cursor.execute(f"SELECT * FROM user WHERE tg_id = {tg_id}")
            user = await cursor.fetchone()
            return user
        

async def get_ticket_by_id(id: int) -> set:
    async with get_db_session() as session:
        async with session.cursor() as cursor:
            query = """
            SELECT * FROM ticket
            WHERE id = %s
            """
            await cursor.execute(query, (id,))
            disk = await cursor.fetchone()
            return disk
        

async def get_last_user_ticket(user_id: int) -> set:
    async with get_db_session() as session:
        async with session.cursor() as cursor:
            query = """
            SELECT * FROM ticket
            WHERE user_id = %s
            ORDER BY id DESC
            """
            await cursor.execute(query, (user_id,))
            disk = await cursor.fetchone()
            return disk


async def is_in_blacklist(tg_id: int) -> bool:
    user = await get_user(tg_id)
    return user[6] is not None and datetime.now() < user[6]


async def is_admin(tg_id: int) -> bool:
    user = await get_user(tg_id)
    return user[4]


async def add_ticket(user_id: int,  
                     content: str) -> bool:
    async with get_db_session() as session:
        async with session.cursor() as cursor:
            try:
                query = """
                INSERT INTO ticket (user_id, content, date, is_done)
                VALUES (%s, %s, %s, %s);
                """
                date = datetime.now()
                client = await cursor.execute(query, (user_id, content, date, False))
                await session.commit()
                return client > 0
            except IntegrityError as ex:
                print("Тикет не создался\n", ex)
                return False


async def update_ticket_status(ticket_id: int, status: bool) -> bool:
    async with get_db_session() as session:
        async with session.cursor() as cursor:
            query = """
            UPDATE ticket
            SET is_done = %s
            WHERE id = %s;
            """
            ticket = await cursor.execute(query, (status, ticket_id))
            await session.commit()
            return ticket > 0
        

async def update_ticket_admin(ticket_id: int, admin_id: int) -> bool:
    async with get_db_session() as session:
        async with session.cursor() as cursor:
            query = """
            UPDATE ticket
            SET admin_id = %s
            WHERE id = %s;
            """
            ticket = await cursor.execute(query, (admin_id, ticket_id))
            await session.commit()
            return ticket > 0