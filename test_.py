import pytest
import aiohttp
from aiohttp import ClientSession, ClientResponse, ClientError
from unittest.mock import patch, AsyncMock, mock_open

from src.extractor import fetch_page, fetch_animal_details
from src.loaders import post_animal_batch
from src.transformer import transform_animal
from main import process_batches, retry , main

MOCK_PAGE_RESPONSE = {
    "items": [{"id": 1, "name": "Animal 1"}, {"id": 2, "name": "Animal 2"}],
    "total_pages": 2
}
MOCK_ANIMAL_DETAILS = {
    "id": 1,
    "name": "Animal 1",
    "friends": "lion",
    "born_at": 1609459200000  
}
MOCK_POST_RESPONSE = {"status": "success"}

@pytest.fixture
def mock_session():
    return AsyncMock(spec=ClientSession)

@pytest.mark.asyncio
async def test_retry_success():
    mock_func = AsyncMock(return_value="success")
    result = await retry(mock_func, "arg")
    assert result == "success"
    assert mock_func.call_count == 1

@pytest.mark.asyncio
async def test_retry_with_client_error():
    mock_func = AsyncMock(side_effect=[ClientError, ClientError, "success"])
    result = await retry(mock_func, "arg", retries=3, delay=0)
    assert result == "success"
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_retry_all_failures():
    mock_func = AsyncMock(side_effect=ClientError)
    result = await retry(mock_func, "arg", retries=3, delay=0)
    assert result is None
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_fetch_page(mock_session):
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.json.return_value = MOCK_PAGE_RESPONSE
    mock_session.get.return_value.__aenter__.return_value = mock_response
    
    result = await fetch_page(mock_session, 1)
    assert result == MOCK_PAGE_RESPONSE
    mock_session.get.assert_called_once_with('http://localhost:3123/animals/v1/animals?page=1')

@pytest.mark.asyncio
async def test_fetch_animal_details(mock_session):
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.json.return_value = MOCK_ANIMAL_DETAILS
    mock_session.get.return_value.__aenter__.return_value = mock_response
    
    result = await fetch_animal_details(mock_session, 1)
    assert result == MOCK_ANIMAL_DETAILS
    mock_session.get.assert_called_once_with('http://localhost:3123/animals/v1/animals/1')

@pytest.mark.asyncio
async def test_post_animal_batch(mock_session):
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.json.return_value = MOCK_POST_RESPONSE
    mock_response.status = 200
    mock_session.post.return_value.__aenter__.return_value = mock_response
    
    result = await post_animal_batch(mock_session, [MOCK_ANIMAL_DETAILS])
    assert result == MOCK_POST_RESPONSE
    mock_session.post.assert_called_once_with('http://localhost:3123/animals/v1/home', json=[MOCK_ANIMAL_DETAILS])

def test_transform_animal():
    transformed = transform_animal(MOCK_ANIMAL_DETAILS)
    assert transformed['friends'] == [ "lion"]
    assert transformed['born_at'] == '2021-01-01T00:00:00+00:00'

@pytest.mark.asyncio
async def test_process_batches(mock_session):
    mock_session.post.return_value.__aenter__.return_value.json.return_value = MOCK_POST_RESPONSE
    mock_session.post.return_value.__aenter__.return_value.status = 200
    
    animals = [MOCK_ANIMAL_DETAILS] * 150  
    await process_batches(mock_session, animals)
    assert mock_session.post.call_count == 2


@pytest.mark.asyncio
async def test_retry_success():
    async def always_successful():
        return "Success"

    result = await retry(always_successful)
    assert result == "Success"


@pytest.mark.asyncio
async def test_retry_failure():
    async def always_fail():
        raise aiohttp.ClientError("Test Error")

    result = await retry(always_fail, retries=3)
    assert result is None


@pytest.mark.asyncio
@patch('utils.retry', new_callable=AsyncMock)
@patch('aiohttp.ClientSession')
async def test_main(mock_client_session, mock_retry):
    mock_session = mock_client_session.return_value.__aenter__.return_value

    mock_retry.side_effect = [
        {
            'total_pages': 1,
            'items': [{'id': 1, 'name': 'Lion'}, {'id': 2, 'name': 'Tiger'}],
        }
    ]

    with patch('builtins.open', new_callable=mock_open):
        await main()

    assert mock_retry is not None 



if __name__ == "__main__":
    pytest.main([__file__])

