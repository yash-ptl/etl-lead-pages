from utils.config import API_URL
import aiohttp
from utils.logger import get_logger

logger = get_logger(__name__)

async def post_animal_batch(session: aiohttp.ClientSession, animals_batch: list):
    """
    Sends a post request with transformed Data
    """
    async with session.post(f'{API_URL}/animals/v1/home', json=animals_batch) as response:
        response.raise_for_status()
        if response.status != 200:
            logger.error(f"Error posting batch: {response.status}")
        return await response.json()
