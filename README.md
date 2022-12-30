# Vedro Cloud

[![Codecov](https://img.shields.io/codecov/c/github/vedro-universe/vedro-cloud/main.svg?style=flat-square)](https://codecov.io/gh/vedro-universe/vedro-cloud)
[![PyPI](https://img.shields.io/pypi/v/vedro-cloud.svg?style=flat-square)](https://pypi.python.org/pypi/vedro-cloud/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/vedro-cloud?style=flat-square)](https://pypi.python.org/pypi/vedro-cloud/)
[![Python Version](https://img.shields.io/pypi/pyversions/vedro-cloud.svg?style=flat-square)](https://pypi.python.org/pypi/vedro-cloud/)

## Installation

### 1. Install package

```shell
$ pip3 install vedro-cloud
```

### 2. Enable plugin

```python
# ./vedro.cfg.py
import vedro
import vedro_cloud
import vedro.plugins.slicer as slicer

class Config(vedro.Config):

    class Plugins(vedro.Config.Plugins):

        class VedroCloud(vedro_cloud.VedroCloud):
            enabled = True
            api_url = "http://localhost:8080"
            project_id = "test"

        class Slicer(slicer.Slicer):
            enabled = False
```

### 3. Run Server

Use `docker-compose.yml` from [vedro-universe/vedro-cloud-api](https://github.com/vedro-universe/vedro-cloud-api)

```shell
$ docker-compose up -d
```

## Usage

```shell
$ vedro run --order-duration
```
