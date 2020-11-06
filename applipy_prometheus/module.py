from applipy import Module, Config
from applipy_inject import with_names
from applipy_metrics import MetricsModule
from applipy_http import Api, Endpoint, EndpointWrapper, HttpModule, PathFormatter
from applipy_prometheus.endpoint import PrometheusEndpoint
from applipy_prometheus.wrapper import MetricsWrapper


class PrometheusModule(Module):

    def __init__(self, config: Config) -> None:
        self._config = config.get('prometheus', Config({}))

    def configure(self, bind, register) -> None:
        bind(Endpoint, PrometheusEndpoint, name='prometheus')
        bind(PathFormatter, name='prometheus')
        bind(with_names(Api, 'prometheus'), name=self._config.get('server_name', None))

        if self._config.get('observe_prometheus_api', True):
            bind(EndpointWrapper, MetricsWrapper, name='prometheus')

        if self._config.get('observe_anonymous_api', True):
            bind(EndpointWrapper, MetricsWrapper)

        for api_name in self._config.get('api_names', []):
            if api_name not in (None, 'prometheus'):
                bind(EndpointWrapper, MetricsWrapper, name=api_name)

    @classmethod
    def depends_on(cls):
        return HttpModule, MetricsModule
