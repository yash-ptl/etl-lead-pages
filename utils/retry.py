import asyncio
import aiohttp
import random
from utils.config import MAX_RETRIES

async def retry(func, *args, retries=MAX_RETRIES, delay=1):
    for attempt in range(retries):
        try:
            return await func(*args)
        except aiohttp.ClientError as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < retries - 1:
                sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                await asyncio.sleep(sleep_time)
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    print(f"All {retries} retries failed.")
    return None