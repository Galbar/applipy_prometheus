from applipy import Module, Config
from applipy_inject import with_names
from applipy_metrics import MetricsModule
from applipy_http import Api, Endpoint, EndpointWrapper, HttpModule, PathFormatter
from applipy_prometheus.endpoint import PrometheusEndpoint
from applipy_prometheus.wrapper import MetricsWrapper


class PrometheusModule(Module):

    def __init__(self, config: Config) -> None:
        self._config = config

    def configure(self, bind, register) -> None:
        bind(Endpoint, PrometheusEndpoint, name='prometheus')
        bind(PathFormatter, name='prometheus')
        bind(EndpointWrapper, MetricsWrapper, name='prometheus')
        bind(Api, with_names(Api, 'prometheus'), name=self._config.get('prometheus.server_name', None))

    @classmethod
    def depends_on(cls):
        return HttpModule, MetricsModule
