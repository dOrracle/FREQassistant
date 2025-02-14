# src/freqtrade_client.py
import aiohttp
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

class FreqtradeClient:
    """Handles communication with FreqTrade REST API"""
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }

    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=self.headers, json=data) as response:
                response.raise_for_status()
                return await response.json()

    async def get_status(self) -> Dict[str, Any]:
        return await self._request('GET', 'status')

    async def start_bot(self) -> Dict[str, Any]:
        return await self._request('POST', 'start')

    async def stop_bot(self) -> Dict[str, Any]:
        return await self._request('POST', 'stop')

    async def deploy_strategy(self, strategy_name: str, strategy_code: str) -> Dict[str, Any]:
        data = {
            'strategy_name': strategy_name,
            'strategy_code': strategy_code
        }
        return await self._request('POST', 'strategy/deploy', data)