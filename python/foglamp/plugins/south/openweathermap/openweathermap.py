# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

""" Weather report from OpenWeatherMap async plugin """

import copy
import asyncio
import http.client
import json
import uuid
import logging

from aiohttp import web

from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south.ingest import Ingest
from foglamp.services.south.exceptions import DataRetrievalError



__author__ = "Mark Riddoch, Ashwin Gopalakrishnan"
__copyright__ = "Copyright (c) 2018 Dianomic Systems"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_LOGGER = logger.setup(__name__, level=logging.INFO)


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
        'order': '1',
        'displayName': 'API URL'
    },
    'appid': {
        'description': 'Application ID registered with OpenWeatherMap',
        'type': 'string',
        'default': 'bbafe18fb275ae5b200d094e36c574ff',
        'order': '2',
        'displayName': 'Application ID'
    },
    'city': {
        'description': 'City to obtain weather report for',
        'type': 'string',
        'default': 'London',
        'order': '3',
        'displayName': 'City'
    },
    'assetName': {
        'description': 'Asset Name',
        'type': 'string',
        'default': 'OpenWeatherMap',
        'order': '4',
        'displayName': 'Asset Name'
    },
    'rate': {
        'description': 'Rate at which to fetch weather report in seconds',
        'type': 'integer',
        'default': '10',
        'minimum': '5',
        'order': '5',
        'displayName': 'Request Interval'
    }
}


def plugin_info():
    """ Returns information about the plugin.
    Args:
    Returns:
        dict: plugin information
    Raises:
    """

    return {
        'name': 'OpenWeatherMap plugin',
        'version': '1.0',
        'mode': 'async',
        'type': 'south',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config):
    """ Initialise the plugin with WeatherReport class' object that will periodically fetch weather data
       Args:
           config: JSON configuration document for the South plugin configuration category
       Returns:
           data: JSON object to be used in future calls to the plugin
       Raises:
       """

    _LOGGER.info("Retrieve Weather Configuration %s", config)

    url = config['url']['value']
    city = config['city']['value']
    appid = config['appid']['value']
    rate = config['rate']['value']
    asset_name = config['assetName']['value']

    data = copy.deepcopy(config)
    data['w_report'] = WeatherReport(url, city, appid, rate, asset_name)
    return data


def plugin_start(handle):
    try:
        task = handle['w_report']
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

    if 'appid' in diff or 'city' in diff or 'url' in diff or 'rate' in diff or 'assetName' in diff:
        plugin_shutdown(handle)
        new_handle = plugin_init(new_config)
        new_handle['restart'] = 'yes'
        _LOGGER.info("Restarting OpenWeatherMap plugin due to change in configuration keys [{}]".format(', '.join(diff)))
    else:
        new_handle = copy.deepcopy(new_config)
        new_handle['restart'] = 'no'

    return new_handle


def plugin_shutdown(handle):
    try:
        _LOGGER.info('South OpenWeatherMap plugin shutting down.')
        task = handle['w_report']
        task.stop()
    except Exception as e:
        _LOGGER.exception(str(e))
        raise


class WeatherReport(object):
    """ Handle integration with OpenWeatherMap API """

    __slots__ = ['_interval', '_loop', 'url', 'city', 'appid', 'asset_name', '_handler']

    def __init__(self, url, city, appid, rate, asset_name):
        self._interval = float(rate)
        self._loop = asyncio.get_event_loop()
        self.url = url
        self.city = city
        self.appid = appid
        self.asset_name = asset_name
        self._handler = None

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

            jdoc = json.loads(res)
            reads = {
                    'city': jdoc['name'],
                    'wind_speed': jdoc['wind']['speed'],
                    'clouds': jdoc['clouds']['all'],
                    'temperature': jdoc['main']['temp'],
                    'pressure': jdoc['main']['pressure'],
                    'humidity': jdoc['main']['humidity'],
                    'visibility': jdoc['visibility']
            }
            data = {
                'asset': self.asset_name,
                'timestamp': utils.local_timestamp(),
                'key': str(uuid.uuid4()),
                'readings': reads
            }
            await Ingest.add_readings(asset='{}'.format(data['asset']),
                                      timestamp=data['timestamp'], key=data['key'],
                                      readings=data['readings'])
        else:
            err = "Unable to fetch information from api.openweathermap"
            _LOGGER.exception(err)
            raise DataRetrievalError(err)
