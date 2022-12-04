from typing import Any, Dict, List, Type, Union
from uuid import uuid4

from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ConfigLoadedEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioSkippedEvent,
)

from ._optimal_orderer import OptimalOrderer
from ._vedro_cloud_client import VedroCloudClient

__all__ = ("VedroCloud", "VedroCloudPlugin",)


class VedroCloudPlugin(Plugin):
    def __init__(self, config: Type["VedroCloud"]) -> None:
        super().__init__(config)
        self._api_url = config.api_url
        self._timeout = config.timeout
        self._results: List[Dict[str, Any]] = []
        self._client: Union[VedroCloudClient, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
            .listen(ArgParseEvent, self.on_arg_parse) \
            .listen(ArgParsedEvent, self.on_arg_parsed) \
            .listen(ScenarioSkippedEvent, self.on_scenario_end) \
            .listen(ScenarioPassedEvent, self.on_scenario_end) \
            .listen(ScenarioFailedEvent, self.on_scenario_end) \
            .listen(CleanupEvent, self.on_cleanup)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        self._global_config: ConfigType = event.config

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        pass

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._client = VedroCloudClient(self._api_url, self._timeout)
        self._global_config.Registry.ScenarioOrderer.register(
            lambda: OptimalOrderer(self._client),
            self
        )

    def on_scenario_end(self, event: Union[ScenarioPassedEvent, ScenarioFailedEvent,
                                           ScenarioSkippedEvent]) -> None:
        started_at = event.scenario_result.started_at or 0.0
        ended_at = event.scenario_result.ended_at or 0.0
        self._results.append({
            "id": str(uuid4()),
            "scenario_id": event.scenario_result.scenario.unique_id,
            "scenario_hash": event.scenario_result.scenario.unique_hash,
            "scenario_path": str(event.scenario_result.scenario.rel_path),
            "scenario_subject": event.scenario_result.scenario.subject,
            "status": event.scenario_result.status.value,
            "started_at": round(started_at * 1000),
            "ended_at": round(ended_at * 1000),
        })

    async def on_cleanup(self, event: CleanupEvent) -> None:
        assert self._client is not None
        try:
            await self._client.post_history(self._results)
        except Exception as e:
            print(f"Failed to send history: {e!r}")
        finally:
            self._results = []


class VedroCloud(PluginConfig):
    plugin = VedroCloudPlugin

    # Vedro Cloud API
    api_url: str = "http://localhost:8080"

    # Timeout for requests
    timeout: float = 5.0
