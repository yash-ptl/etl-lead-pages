from utils.config import API_URL
import aiohttp

async def post_animal_batch(session: aiohttp.ClientSession, animals_batch: list):
    async with session.post(f'{API_URL}/animals/v1/home', json=animals_batch) as response:
        response.raise_for_status()
        if response.status != 200:
            print(f"Error posting batch: {response.status}")
        return await response.json()
