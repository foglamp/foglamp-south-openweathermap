# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

from unittest.mock import patch
import pytest

from python.foglamp.plugins.south.openweathermap import openweathermap

__author__ = "Ashish Jabble, Amarendra K Sinha"
__copyright__ = "Copyright (c) 2018 Dianomic Systems"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

config = openweathermap._DEFAULT_CONFIG


def test_plugin_contract():
    # Evaluates if the plugin has all the required methods
    assert callable(getattr(openweathermap, 'plugin_info'))
    assert callable(getattr(openweathermap, 'plugin_init'))
    assert callable(getattr(openweathermap, 'plugin_start'))
    assert callable(getattr(openweathermap, 'plugin_shutdown'))
    assert callable(getattr(openweathermap, 'plugin_reconfigure'))


def test_plugin_info():
    assert openweathermap.plugin_info() == {
        'name': 'OpenWeatherMap plugin',
        'version': '1.5.0',
        'mode': 'async',
        'type': 'south',
        'interface': '1.0',
        'config': config
    }


@pytest.mark.skip(reason="To be implemented")
def test_plugin_init():
    pass


def test_plugin_start():
    with patch.object(openweathermap._LOGGER, 'info') as patch_logger_info:
        with patch.dict(config['url'], {'value': config['url']['default']}):
            with patch.dict(config['city'], {'value': config['city']['default']}):
                with patch.dict(config['appid'], {'value': config['appid']['default']}):
                    with patch.dict(config['rate'], {'value': config['rate']['default']}):
                        with patch.dict(config['assetName'],
                                        {'value': config['assetName']['default']}):
                            openweathermap.plugin_start(config)
                            Weather_Report = openweathermap.task
                            with patch.object(openweathermap.loop, 'call_later', lambda: print(1)):
                                assert config['url']['value'] == Weather_Report.url
                                assert config['city']['value'] == Weather_Report.city
                                assert config['appid']['value'] == Weather_Report.appid
                                assert float(config['rate']['value']) == Weather_Report._interval
    patch_logger_info.assert_called_once_with('plugin_start called')
    openweathermap.plugin_shutdown(config)


@pytest.mark.skip(reason="To be implemented")
def test_plugin_reconfigure():
    pass


@pytest.mark.skip(reason="To be implemented")
def test_plugin_shutdown():
    pass
