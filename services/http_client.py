from abc import ABC, abstractmethod
from typing import Optional

from aiohttp import ClientSession, ClientTimeout


class HttpClient:
    @abstractmethod
    async def get(self, url: str):
        pass


class SimpleHttpClient:

    async def get(self, url: str, headers: Optional[dict] = None) -> dict:
        async with ClientSession(timeout=ClientTimeout(5)) as session:
            async with session.get(url, headers=headers) as response:
                return await response.json()
