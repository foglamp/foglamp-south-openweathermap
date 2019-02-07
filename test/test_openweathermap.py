# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

from unittest.mock import patch
import pytest

from python.foglamp.plugins.south.openweathermap import openweathermap

__author__ = "Ashish Jabble"
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


def test_plugin_init():
    with patch.object(openweathermap._LOGGER, 'info') as patch_logger_info:
        with patch.dict(config['url'], {'value': config['url']['default']}):
            with patch.dict(config['city'], {'value': config['city']['default']}):
                with patch.dict(config['appid'], {'value': config['appid']['default']}):
                    with patch.dict(config['rate'], {'value': config['rate']['default']}):
                        WeatherReport = openweathermap.plugin_init(config)
                        assert config['url']['value'] == WeatherReport.url
                        assert config['city']['value'] == WeatherReport.city
                        assert config['appid']['value'] == WeatherReport.appid
                        assert config['rate']['value'] == WeatherReport.rate
    patch_logger_info.assert_called_once_with('Retrieve Weather Configuration %s', config)


@pytest.mark.skip(reason="To be implemented")
def test_plugin_start():
    pass


@pytest.mark.skip(reason="To be implemented")
def test_plugin_reconfigure():
    pass


@pytest.mark.skip(reason="To be implemented")
def test_plugin_shutdown():
    pass
