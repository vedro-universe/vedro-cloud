from baby_steps import then, when
from vedro.core import Plugin

from vedro_cloud import VedroCloud, VedroCloudPlugin


def test_plugin():
    with when:
        plugin = VedroCloudPlugin(VedroCloud)

    with then:
        assert isinstance(plugin, Plugin)
