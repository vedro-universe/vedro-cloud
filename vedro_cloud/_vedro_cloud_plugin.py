from typing import Any, Dict, List, Optional, Type, TypedDict, Union
from uuid import uuid4

from rtry import retry
from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ConfigLoadedEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioSkippedEvent,
    StartupEvent,
)

from ._duration_orderer import DurationOrderer
from ._validate_config import validate_config_params
from ._vedro_cloud_client import VedroCloudClient

__all__ = ("VedroCloud", "VedroCloudPlugin",)


class VedroCloudPlugin(Plugin):
    def __init__(self, config: Type["VedroCloud"], *,
                 client_factory: Any = VedroCloudClient) -> None:
        super().__init__(config)
        self._api_url = config.api_url
        self._timeout = config.timeout
        self._project_id = config.project_id
        self._client = client_factory(self._project_id, self._api_url, self._timeout)
        self._report_id = config.report_id
        self._verbose = config.verbose
        self._exit_code = config.exit_code
        self._launch_id: Union[str, None] = None
        self._results: List[Dict[str, Any]] = []
        self._timings: Dict[str, int] = {}
        self._total: Union[int, None] = None
        self._index: Union[int, None] = None

    async def _get_timings(self) -> Dict[str, int]:
        try:
            self._timings = await retry(attempts=3,
                                        delay=1.0)(self._client.get_timings)(self._report_id)
        except Exception as e:
            print(f"-> Failed to retrieve timings: {e!r}")
            exit(self._exit_code)
        if self._verbose:
            print("-> Retrieved timings:", len(self._timings), self._report_id)
        return self._timings

    async def _post_history(self) -> None:
        try:
            await self._client.post_history(self._results)
        except Exception as e:
            print(f"-> Failed to send history: {e!r}")
        if self._verbose:
            print("-> Posted history:", len(self._results))
        self._results = []

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
            .listen(ArgParseEvent, self.on_arg_parse) \
            .listen(ArgParsedEvent, self.on_arg_parsed) \
            .listen(StartupEvent, self.on_startup) \
            .listen(ScenarioSkippedEvent, self.on_scenario_end) \
            .listen(ScenarioPassedEvent, self.on_scenario_end) \
            .listen(ScenarioFailedEvent, self.on_scenario_end) \
            .listen(CleanupEvent, self.on_cleanup)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        self._global_config: ConfigType = event.config

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        group = event.arg_parser.add_argument_group("Vedro Cloud")
        group.add_argument("--order-duration", action="store_true", default=False,
                           help="Set duration scenario order (desc)")
        group.add_argument("--slicer-total", type=int, help="Set total workers")
        group.add_argument("--slicer-index", type=int, help="Set current worker")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        if event.args.order_duration:
            self._global_config.Registry.ScenarioOrderer.register(
                lambda: DurationOrderer(self._get_timings),
                self
            )

        self._total = event.args.slicer_total
        self._index = event.args.slicer_index
        if self._total is not None:
            assert self._index is not None
            assert self._total > 0
        if self._index is not None:
            assert self._total is not None
            assert 0 <= self._index < self._total

        if errors := validate_config_params(self._project_id, self._report_id):
            raise ValueError("\n - " + "\n - ".join(errors))

        if (self._total is not None) and (self._total > 1) and (self._report_id is None):
            raise ValueError("Report ID is required when total workers > 1")

    async def on_startup(self, event: StartupEvent) -> None:
        self._launch_id = str(uuid4())
        if (self._total is None) or (self._index is None):
            return

        durations = []
        async for scenario in event.scheduler:
            duration = 0 if scenario.is_skipped() else self._timings.get(scenario.unique_hash, 0)
            durations.append((duration, scenario.unique_hash))
        durations.sort(reverse=True)

        class SliceInfo(TypedDict):
            sum: int
            scenarios: Dict[str, int]

        slices: List[SliceInfo] = [{"sum": 0, "scenarios": {}} for _ in range(self._total)]
        for duration, scenario_hash in durations:
            slice_index = min(range(self._total),
                              key=lambda i: (slices[i]["sum"], len(slices[i]["scenarios"])))
            slices[slice_index]["sum"] += duration
            slices[slice_index]["scenarios"][scenario_hash] = duration

        async for scenario in event.scheduler:
            if scenario.unique_hash not in slices[self._index]["scenarios"]:
                event.scheduler.ignore(scenario)

    def on_scenario_end(self, event: Union[ScenarioPassedEvent, ScenarioFailedEvent,
                                           ScenarioSkippedEvent]) -> None:
        started_at = event.scenario_result.started_at or 0.0
        ended_at = event.scenario_result.ended_at or 0.0

        self._results.append({
            "id": str(uuid4()),
            "launch_id": self._launch_id,
            "report_id": self._report_id,

            "scenario_hash": event.scenario_result.scenario.unique_hash,
            "scenario_rel_path": str(event.scenario_result.scenario.rel_path),
            "scenario_subject": event.scenario_result.scenario.subject,
            "scenario_namespace": event.scenario_result.scenario.namespace,

            "status": event.scenario_result.status.value,
            "started_at": round(started_at * 1000),
            "ended_at": round(ended_at * 1000),
        })

    async def on_cleanup(self, event: CleanupEvent) -> None:
        await self._post_history()


class VedroCloud(PluginConfig):
    plugin = VedroCloudPlugin

    # Vedro Cloud API
    api_url: str = "http://localhost:8080"

    # Timeout for requests
    timeout: float = 5.0

    # Project ID
    project_id: str = "default"

    # Report ID
    report_id: Optional[str] = None

    # Verbose mode
    verbose: bool = False

    # Exit code on failure
    exit_code: int = 1
