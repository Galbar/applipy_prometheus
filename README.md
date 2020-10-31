[![pipeline status](https://gitlab.com/applipy/applipy_prometheus/badges/master/pipeline.svg)](https://gitlab.com/applipy/applipy_prometheus/-/pipelines?scope=branches&ref=master)
[![coverage report](https://gitlab.com/applipy/applipy_prometheus/badges/master/coverage.svg)](https://gitlab.com/applipy/applipy_prometheus/-/graphs/master/charts)
[![PyPI Status](https://img.shields.io/pypi/status/applipy-prometheus.svg)](https://pypi.org/project/applipy-prometheus/)
[![PyPI Version](https://img.shields.io/pypi/v/applipy-prometheus.svg)](https://pypi.org/project/applipy-prometheus/)
[![PyPI Python](https://img.shields.io/pypi/pyversions/applipy-prometheus.svg)](https://pypi.org/project/applipy-prometheus/)
[![PyPI License](https://img.shields.io/pypi/l/applipy-prometheus.svg)](https://pypi.org/project/applipy-prometheus/)
[![PyPI Format](https://img.shields.io/pypi/format/applipy-prometheus.svg)](https://pypi.org/project/applipy-prometheus/)

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

By default, the library will add the `MetricsWrapper` to the API that registers
the endpoint `/metrics`, named `prometheus`, and the anonymous API, the one
that is bound without named parameters. This functionalities can be disabled by
setting the configuration values `prometheus.observe_prometheus_api` and
`prometheus.observe_anonymous_api` to `false`.

> A named API is one that is registered with named parameters like so: `bind(with_names(Api, 'api_name'))`.  
> The anonymous API has no named parameters and is usually registered like so: `bind(Api)`.

You can also tell the module to add the `MetricsWrapper` to you named APIs by
setting the configuration value `prometheus.api_names` to a list containing the
names of you named APIs.

> In the case your API is registered with multiple parameter names, the one
> that applies for the wrapper is the name for the `wrappers` parameter.

The wrapper has
[priority](https://gitlab.com/applipy/applipy_http/-/blob/master/docs/endpoint_wrapper.md#endpointwrapper-priority)
`100`.

The metrics are tagged by default with:
 - `method`: HTTP request method (i.e. `GET`, `POST`, etc.)
 - `path`: path of the endpoint handling the request
 - `server`: name of the server handling the request (anonymous server is
   empty string)
 - `status`: status code of the response

On top of that, a dictionary is added to the `Context` with the key
`metrics.tags` where you can add custom tags to the metric.

### Example

#### Full prometheus module config

All keys and their default values:

```yaml
prometheus:
  server_name: null
  observe_prometheus_api: true
  observe_anonymous_api: true
  api_names: []
```

#### Endpoint with custom metric tag

```python
# myendpoint.py

from aiohttp import web
from applipy_http import Endpoint


class MyEndpoint(Endpoint):

    async def get(self, req, ctx):
        ctx['metrics.tags']['custom_tag'] = 'value'
        return web.Response(body='Ok')

    def path(self):
        return '/'
```

#### Usage with anonymous API

```python
# mymodule.py

from applipy import Module
from applipy_http import Api, HttpModule, Endpoint, PathFormatter
from applipy_inject import with_names
from applipy_prometheus import MetricsWrapper
from myendpoint import MyEndpoint


class MyModule(Module):
    def configure(self, bind, register):
        bind(Endpoint, MyEndpoint)
        bind(PathFormatter)
        bind(Api)

    @classmethod
    def depends_on(cls):
        return HttpModule,
```

```yaml
# dev.yaml

app:
  name: test
  modules: [mymodule.MyModule]

http:
  host: 0.0.0.0
  port: 8080
```

#### Usage with anonymous API

```python
# mymodule.py

from applipy import Module
from applipy_http import Api, HttpModule, Endpoint, PathFormatter
from applipy_inject import with_names
from applipy_prometheus import MetricsWrapper
from myendpoint import MyEndpoint


class MyModule(Module):
    def configure(self, bind, register):
        bind(Endpoint, MyEndpoint, name='myApi')
        bind(PathFormatter, name='myApi')
        bind(with_names(Api, 'myApi'))

    @classmethod
    def depends_on(cls):
        return HttpModule,
```

```yaml
# dev.yaml

app:
  name: test
  modules: [mymodule.MyModule]

http:
  host: 0.0.0.0
  port: 8080

prometheus:
  api_names: [myApi]
```
