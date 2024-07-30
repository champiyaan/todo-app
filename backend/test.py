import asyncpg
import asyncio

async def test_connection():
    try:
        conn = await asyncpg.connect(
            user='postgres.crswfdkfanvrymwrsyxt',
            password='@dasdsa$$££DSAGDSJ0`',
            database='postgres',
            host='aws-0-eu-west-2.pooler.supabase.com',
            port=6543,
            ssl='require'  # Ensures SSL is used
        )
        print("Connection successful")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

loop = asyncio.get_event_loop()
loop.run_until_complete(test_connection())
