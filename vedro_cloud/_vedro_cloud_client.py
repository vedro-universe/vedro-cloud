from http import HTTPStatus
from typing import Any, Dict, List, Union

from httpx import AsyncClient

__all__ = ("VedroCloudClient",)


class VedroCloudClient:
    def __init__(self, api_url: str, timeout: float) -> None:
        self._api_url = api_url
        self._timeout = timeout

    async def _do_request(self, method: str, url: str, **kwargs: Any) -> Any:
        async with AsyncClient() as client:
            response = await client.request(method, url, **kwargs)
            assert response.status_code == HTTPStatus.OK
        return response.json()

    async def get_timings(self) -> Dict[str, Union[str, int]]:
        url = f"{self._api_url}/v0.1/scenarios/slow"
        scenarios = await self._do_request("GET", url)
        return {scenario["scenario_hash"]: scenario["median"] for scenario in scenarios}

    async def post_history(self, history: List[Dict[str, Any]]) -> None:
        url = f"{self._api_url}/v0.1/history"
        await self._do_request("POST", url, json=history)
