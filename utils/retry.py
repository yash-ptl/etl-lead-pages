import asyncio
import aiohttp
import random
from utils.config import MAX_RETRIES
from utils.logger import get_logger

logger = get_logger(__name__)
async def retry(func, *args, retries=MAX_RETRIES, delay=1):
    """
    Implements retry functionality 
    """
    for attempt in range(retries):
        try:
            return await func(*args)
        except aiohttp.ClientError as e:
            logger.error(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < retries - 1:
                sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Retrying in {sleep_time:.2f} seconds...")
                await asyncio.sleep(sleep_time)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break
    logger.error(f"All {retries} retries failed.")
    return None