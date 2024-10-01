import asyncio
import aiohttp
import json
import time
from utils.config import BATCH_SIZE
from src.extractor import fetch_page, fetch_animal_details
from src.transformer import transform_animal
from src.loaders import post_animal_batch
from utils.retry import retry
from utils.logger import get_logger

logger = get_logger(__name__)
async def process_batches(session, animals):
    """
    Processing data in batches
    """
    batches = [animals[i:i + BATCH_SIZE] for i in range(0, len(animals), BATCH_SIZE)]
    for batch in batches:
        result = await retry(post_animal_batch, session, batch)
        if result:
            logger.info(f"Posted batch of {len(batch)} animals.")
        else:
            logger.error(f"Failed to post batch of {len(batch)} animals after retries.")

async def main():
    """
    Implements the ETL Process along with Logging
    """
    async with aiohttp.ClientSession() as session:
        # Extract
        first_page = await retry(fetch_page, session, 1)
        if not first_page:
            logger.error("Failed to fetch first page.")
            return

        total_pages = first_page['total_pages']
        animals = first_page['items']

        pages = await asyncio.gather(*[retry(fetch_page, session, page_num) for page_num in range(2, total_pages + 1)])
        valid_pages = [page for page in pages if page is not None]
        animals += [item for page in valid_pages for item in page['items']]

        with open("results/non-detailed.json", "w") as f:
            json.dump(animals, f, indent=4)

        detailed_animals = await asyncio.gather(*[retry(fetch_animal_details, session, animal['id']) for animal in animals])
        detailed_animals = [animal for animal in detailed_animals if animal is not None]

        with open("results/detailed.json", "w") as f:
            json.dump(detailed_animals, f, indent=4)

        # Transform
        transformed_animals = [transform_animal(animal) for animal in detailed_animals]

        with open("results/transformed.json", "w") as f:
            json.dump(transformed_animals, f, indent=4)

        # Load
        await process_batches(session, transformed_animals)

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    logger.info(f"Completed in {time.time() - start_time} seconds")