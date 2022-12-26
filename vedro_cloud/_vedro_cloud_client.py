from http import HTTPStatus
from typing import Any, Dict, List, Optional

from httpx import AsyncClient

__all__ = ("VedroCloudClient",)


class VedroCloudClient:
    def __init__(self, project_id: str, api_url: str, timeout: float) -> None:
        self._project_id = project_id
        self._api_url = api_url
        self._timeout = timeout

    async def _do_request(self, method: str, url: str, **kwargs: Any) -> Any:
        async with AsyncClient() as client:
            resp = await client.request(method, url, **kwargs)
            try:
                body = resp.json()
            except:  # noqa: E722
                body = None
            if (resp.status_code != HTTPStatus.OK) or (body is None):
                raise ValueError(
                    f"Invalid response from '{url}': {resp.status_code} {resp.read()!r}")
        return body

    async def get_timings(self, report_id: Optional[str] = None) -> Dict[str, int]:
        url = f"{self._api_url}/v0.2/projects/{self._project_id}/scenarios"
        params = {"order_by": "duration"}
        if report_id:
            params["report_id"] = report_id
        scenarios = await self._do_request("GET", url, params=params)
        return {scenario["hash"]: scenario["median"] for scenario in scenarios}

    async def post_history(self, history: List[Dict[str, Any]]) -> None:
        url = f"{self._api_url}/v0.2/projects/{self._project_id}/history"
        await self._do_request("POST", url, json=history)
