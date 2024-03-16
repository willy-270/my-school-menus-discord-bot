import asyncio
import aiosqlite

class Database:
    async def connect(**kwargs):
        try:
            db = await aiosqlite.connect('database.db')
            c = await db.cursor()
            await c.execute('''
                CREATE TABLE IF NOT EXISTS servers
                (server_id INTEGER, channel_id INTEGER, send_images INTEGER, timezone TEXT)
            ''')
            await db.commit()
            return db
        except Exception as e:
            print(e)
            return None
        
    async def insert_config_values(db, values):
        c = await db.cursor()
        await c.execute('''INSERT INTO servers (server_id, channel_id, send_images) VALUES (?, ?, ?)''', values)
        await db.commit()

    async def get_config_values(db, server_id):
        c = await db.cursor()
        await c.execute('''SELECT channel_id, send_images, timezone FROM servers WHERE server_id=?''', (server_id,))
        return await c.fetchone()

    








