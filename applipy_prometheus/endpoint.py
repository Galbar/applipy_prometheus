from aiohttp import web
from applipy import Config
from applipy_metrics import MetricsRegistry
from applipy_http import Context, Endpoint
from collections import defaultdict


class PrometheusEndpoint(Endpoint):

    _registry: MetricsRegistry
    _app_name: str

    def __init__(self, config: Config, _registry: MetricsRegistry) -> None:
        self._registry = _registry
        self._app_name = config.get('app.name')

    async def get(self, request: web.Request, context: Context) -> web.StreamResponse:
        response = web.StreamResponse()
        response.content_type = 'text/plain; version=0.0.4'
        await response.prepare(request)

        metrics = self._registry.dump_metrics(True)

        grouped_metrics = defaultdict(list)

        for metric, value in metrics.items():
            tags = metric.get_tags().copy()
            tags['app_name'] = self._app_name
            grouped_metrics[metric.get_key()].append((tags, value))

        for name, entries in grouped_metrics.items():
            _, value = entries[0]
            if 'avg' in value:
                write = self._write_summary
            elif 'value' in value:
                write = self._write_gauge
            elif 'count' in value:
                write = self._write_counter
            else:
                continue

            await write(response, name, entries)
            await response.write(b'\n')

        await response.write_eof()

        return response

    async def _write_counter(self, response, name, entries):
        await response.write(f'# TYPE {name} counter\n'.encode('utf-8'))
        for tags, value in entries:
            await self._write_metric(response, name, tags, value['count'])

    async def _write_gauge(self, response, name, entries):
        await response.write(f'# TYPE {name} gauge\n'.encode('utf-8'))
        for tags, value in entries:
            await self._write_metric(response, name, tags, value['value'])

    async def _write_summary(self, response, name, entries):
        await response.write(f'# TYPE {name} summary\n'.encode('utf-8'))
        for tags, value in entries:
            await self._write_metric(response, f'{name}_avg', tags, value['avg'])
            await self._write_metric(response, f'{name}_count', tags, value['count'])
            await self._write_metric(response, f'{name}_max', tags, value['max'])
            await self._write_metric(response, f'{name}_min', tags, value['min'])
            await self._write_metric(response, f'{name}_std_dev', tags, value['std_dev'])
            await self._write_metric(response, f'{name}_sum', tags, value['sum'])
            tags['quantile'] = 0.75
            await self._write_metric(response, name, tags, value['75_percentile'])
            tags['quantile'] = 0.95
            await self._write_metric(response, name, tags, value['95_percentile'])
            tags['quantile'] = 0.99
            await self._write_metric(response, name, tags, value['99_percentile'])
            tags['quantile'] = 0.999
            await self._write_metric(response, name, tags, value['999_percentile'])

    async def _write_metric(self, response, name, tags, value):
        await response.write(name.encode('utf-8'))
        if len(tags):
            await response.write(b'{')

            await response.write((
                ','.join(f'{label_name}="{self._sanitize_label_value(str(label_value))}"'
                         for label_name, label_value in tags.items())
            ).encode('utf-8'))

            await response.write(b'}')

        await response.write(b' ')
        await response.write(str(value).encode('utf-8'))
        await response.write(b'\n')

    def _sanitize_label_value(self, value):
        return value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

    def path(self) -> str:
        return '/metrics'
