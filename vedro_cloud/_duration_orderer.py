from typing import Awaitable, Callable, Dict, List

from vedro.core import ScenarioOrderer, VirtualScenario

__all__ = ("DurationOrderer",)

DurationRetriever = Callable[[], Awaitable[Dict[str, int]]]


class DurationOrderer(ScenarioOrderer):
    def __init__(self, get_durations: DurationRetriever) -> None:
        self._get_durations = get_durations

    async def sort(self, scenarios: List[VirtualScenario]) -> List[VirtualScenario]:
        timings = await self._get_durations()
        return sorted(scenarios, key=lambda scn: timings.get(scn.unique_hash, 0), reverse=False)
