# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

""" Weather report from OpenWeatherMap async plugin """

import copy
import sys
import asyncio
import http.client
import json
from datetime import datetime, timezone
import uuid
import logging

from aiohttp import web

from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south.ingest import Ingest


__author__ = "Mark Riddoch, Ashwin Gopalakrishnan"
__copyright__ = "Copyright (c) 2018 Dianomic Systems"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_LOGGER = logger.setup(__name__, level=logging.INFO)

_CONFIG_CATEGORY_NAME = 'openweathermap'
_CONFIG_CATEGORY_DESCRIPTION = 'Weather Report from OpenWeatherMap'
_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'Weather Report from OpenWeatherMap',
        'type': 'string',
        'default': 'openweathermap',
        'readonly': 'true'
    },
    'url': {
        'description': 'API URL to fetch information',
        'type': 'string',
        'default': 'api.openweathermap.org',
        'order': '1'
    },
    'city': {
        'description': 'City to obtain weather report for',
        'type': 'string',
        'default': 'London',
        'order': '3'
    },
    'appid': {
        'description': 'Application ID registered with OpenWeatherMap',
        'type': 'string',
        'default': 'bbafe18fb275ae5b200d094e36c574ff',
        'order': '2'
    },
    'rate': {
        'description': 'Rate at which to fetch weather report in seconds',
        'type': 'integer',
        'default': '10',
        'minimum': '5',
        'order': '4'
    }
}


def plugin_info():
    return {
        'name': 'OpenWeatherMap plugin',
        'version': '1.0',
        'mode': 'async',
        'type': 'south',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config):
    """ Create the WeatherReport class that will periodically fetch weather data """

    _LOGGER.info("Retrieve Weather Configuration %s", config)

    url = config['url']['value']
    city = config['city']['value']
    appid = config['appid']['value']
    rate = config['rate']['value']

    return WeatherReport(url, city, appid, rate)


def plugin_start(task):
    try:
        task.start()
    except Exception as e:
        _LOGGER.exception("OpenWeatherMap plugin failed to start. Details %s", str(e))
        raise


def plugin_reconfigure(handle, new_config):
    """ Reconfigures the plugin

    it should be called when the configuration of the plugin is changed during the operation of the south service.
    The new configuration category should be passed.

    Args:
        handle: handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    Raises:
    """

    _LOGGER.info("Old config for OpenWeatherMap plugin {} \n new config {}".format(handle, new_config))

    diff = utils.get_diff(handle, new_config)

    if 'appid' in diff or 'city' in diff or 'url' in diff or 'rate' in diff:
        plugin_shutdown(handle)
        new_handle = plugin_init(new_config)
        new_handle['restart'] = 'yes'
        _LOGGER.info("Restarting OpenWeatherMap plugin due to change in configuration keys [{}]".format(', '.join(diff)))
    else:
        new_handle = copy.deepcopy(new_config)
        new_handle['restart'] = 'no'

    return new_handle


def plugin_shutdown(task):
    try:
        _LOGGER.info('South openweathermap plugin shutting down.')
        task.stop()
    except Exception as e:
        _LOGGER.exception(str(e))
        raise


class WeatherReport(object):
    """ Handle interation with OpenWeatherMap API """

    def __init__(self, url, city, appid, rate):
        self._interval = float(rate)
        self._loop = asyncio.get_event_loop()
        self.url = url
        self.city = city
        self.appid = appid
        self.rate = rate

    def _run(self):
        asyncio.ensure_future(self.fetch())
        self._handler = self._loop.call_later(self._interval, self._run)

    def start(self):
        self._handler = self._loop.call_later(self._interval, self._run)

    def stop(self):
        self._handler.cancel()

    async def fetch(self):
        conn = http.client.HTTPConnection(self.url)

        conn.request('GET', '/data/2.5/weather?q={}&APPID={}'.format(self.city, self.appid))

        r = conn.getresponse()
        if r.status == 200:
            res = r.read().decode()
            conn.close()

            if not Ingest.is_available():
                message = {'busy': True}
                raise web.HTTPServiceUnavailable(reason=message)
            else:
                asset = 'OpenWeatherMap'
                timestamp = str(datetime.now(tz=timezone.utc))
                data = json.loads(res)
                readings = {'wind_deg': data['wind']['deg'], 'wind_speed': data['wind']['speed'],
                            'temperature': data['main']['temp'],
                            'pressure': data['main']['pressure'],
                            'visibility': data['visibility']}
                key = str(uuid.uuid4())
                await Ingest.add_readings(asset=asset, timestamp=timestamp, key=key, readings=readings)
