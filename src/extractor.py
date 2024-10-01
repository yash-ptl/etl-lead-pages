import aiohttp
from utils.config import API_URL

async def fetch_page(session: aiohttp.ClientSession, page_num: int):
    """
    Fetches details of all the animals pagewise
    """
    async with session.get(f'{API_URL}/animals/v1/animals?page={page_num}') as response:
        response.raise_for_status()
        return await response.json()

async def fetch_animal_details(session: aiohttp.ClientSession, animal_id: int):
    """
    Fetches details of particular animal with the given animal_id
    """
    async with session.get(f'{API_URL}/animals/v1/animals/{animal_id}') as response:
        response.raise_for_status()
        return await response.json()