from typing import List

from vedro.core import ScenarioOrderer, VirtualScenario

from ._vedro_cloud_client import VedroCloudClient

__all__ = ("OptimalOrderer",)


class OptimalOrderer(ScenarioOrderer):
    def __init__(self, vedro_cloud_client: VedroCloudClient) -> None:
        self._client = vedro_cloud_client

    async def sort(self, scenarios: List[VirtualScenario]) -> List[VirtualScenario]:
        timings = await self._client.get_timings()
        return sorted(scenarios, key=lambda scn: timings.get(scn.unique_hash, 0), reverse=True)
