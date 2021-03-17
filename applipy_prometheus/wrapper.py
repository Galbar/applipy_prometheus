import functools

from aiohttp import web

from applipy import Config
from applipy_http import Context, EndpointMethod, EndpointWrapper
from applipy_metrics import Chronometer, MetricsRegistry
from applipy_metrics.meters import BaseMetric


class MetricsWrapper(EndpointWrapper):

    _metrics: MetricsRegistry

    def __init__(self, metrics: MetricsRegistry, config: Config) -> None:
        self._metrics = metrics

    def wrap(self, method: str, path: str, handler: EndpointMethod) -> EndpointMethod:
        tags = {
            'method': method,
            'path': path,
        }

        @functools.wraps(handler)
        async def wrapper(request: web.Request, context: Context) -> web.StreamResponse:
            status = 500
            _tags = tags.copy()
            _tags['server'] = context.get('server.name') or ''
            context['metrics.tags'] = _tags
            with Chronometer(on_stop=lambda v: self._observe_value(_tags, v)):
                try:
                    response = await handler(request, context)
                    status = response.status
                except web.HTTPException as e:
                    status = e.status_code
                    raise
                except Exception:
                    status = 500
                    raise
                finally:
                    _tags['status'] = status
            return response
        return wrapper

    def _observe_value(self, tags, value) -> BaseMetric:
        return self._metrics.summary('applipy_web_request_duration_seconds', tags).add(value)

    def priority(self) -> int:
        return 100
