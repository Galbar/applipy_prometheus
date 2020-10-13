import functools

from aiohttp import web

from applipy import Config
from applipy_http import Context, EndpointMethod, EndpointWrapper
from applipy_metrics import Chronometer, MetricsRegistry


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
            chrono = Chronometer()
            try:
                _tags = tags.copy()
                _tags['server'] = context.get('server.name') or ''
                context['metrics.tags'] = _tags
                response = await handler(request, context)
                status = response.status
            except web.HTTPException as e:
                status = e.status_code
                raise
            except Exception:
                status = 500
                raise
            finally:
                elapsed = chrono.stop()
                _tags['status'] = status

                self._metrics.summary('applipy_web_request_duration_seconds', _tags).add(elapsed)

            return response

        return wrapper

    def priority(self) -> int:
        return 100
