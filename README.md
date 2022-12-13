# Vedro Cloud

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
