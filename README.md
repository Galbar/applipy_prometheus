# Applipy Prometheus Metrics

    pip install applipy_prometheus

Exposes applipy metrics in prometheus format as an HTTP endpoint with path `/metrics`.

## Usage

Add the `applipy_prometheus.PrometheusModule` to your application. Optionally,
define through which http server to expose the `/metrics` endpoint, if no name
is given it defaults to the anonymous server:

```yaml
# dev.yaml

app:
    name: demo
    modules:
        - applipy_prometheus.PrometheusModule

http:
    internal:
        host: 0.0.0.0
        port: 8080

prometheus.server_name: internal
```

To run this test just install `applipy_prometheus` and `pyyaml` and run the applipy application:

```bash
pip install applipy_prometheus pyyaml
python -m applipy
```

You can now query [http://0.0.0.0:8080/metrics](http://0.0.0.0:8080/metrics)
and you should see some metrics for that endpoint (you'll have to query it
twice to see metrics).

This module uses
[`applipy_metrics`](https://gitlab.com/applipy/applipy_metrics)'s registry to
load the metrics and generate the Prometheus document.

## Metrics Endpoint Wrapper

This library also comes with `MetricsWrapper`. It is an
[`applipy_http.EndpointWrapper`](https://gitlab.com/applipy/applipy_http/-/blob/master/docs/endpoint_wrapper.md)
that can be bound to your APIs and will automatically measure the request time
and store it as a summary with name `applipy_web_request_duration_seconds`.

The wrapper has priority `100`.

The metrics are tagged by default with:
 - `method`: HTTP request method (i.e. `GET`, `POST`, etc.)
 - `path`: path of the endpoint handling the request
 - `server`: name of the server handling the request (anonymous server is
   empty string)
 - `status`: status code of the response

On top of that, a dictionary is added to the `Context` with the key
`metrics.tags` where you can add custom tags to the metric.

### Example

```python
from aiohttp import web
from applipy import Module
from applipy_http import Api, HttpModule, Endpoint, EndpointWrapper, PathFormatter
from applipy_inject import with_names
from applipy_prometheus import MetricsWrapper


class MyEndpoint(Endpoint):

    async def get(self, req, ctx):
        ctx['metrics.tags']['custom_tag'] = 'value'
        return web.Response(body='Ok')


class MyModule(Module):
    def configure(self, bind, register):
        bind(Endpoint, MyEndpoint, name='myApi')
        bind(PathFormatter, name='myApi')

        # Register the MetricsWrapper to my Api
        bind(EndpointWrapper, MetricsWrapper, name='myApi')

        bind(with_names(Api, 'myApi'))

    @classmethod
    def depends_on(cls):
        return HttpModule,
```
