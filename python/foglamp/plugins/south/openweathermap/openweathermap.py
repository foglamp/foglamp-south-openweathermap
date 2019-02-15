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
from threading import Thread
from aiohttp import web

from foglamp.common import logger
from foglamp.plugins.common import utils
import async_ingest


__author__ = "Mark Riddoch, Ashwin Gopalakrishnan, Amarendra K Sinha"
__copyright__ = "Copyright (c) 2018 Dianomic Systems"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

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
_LOGGER = logger.setup(__name__, level=logging.INFO)
c_callback = None
c_ingest_ref = None
loop = None
t = None
task = None


def plugin_info():
    """ Returns information about the plugin.
    Args:
    Returns:
        dict: plugin information
    Raises:
    """

    return {
        'name': 'OpenWeatherMap plugin',
        'version': '1.5.0',
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
    data = copy.deepcopy(config)
    return data


def plugin_start(handle):
    global loop, t, task
    _LOGGER.info("plugin_start called")

    loop = asyncio.new_event_loop()
    try:
        url = handle['url']['value']
        city = handle['city']['value']
        appid = handle['appid']['value']
        rate = handle['rate']['value']
        asset_name = handle['assetName']['value']
        task = WeatherReport(url, city, appid, rate, asset_name)
        task.start()

        def run():
            global loop
            loop.run_forever()

        t = Thread(target=run)
        t.start()
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

    # plugin_shutdown
    plugin_shutdown(handle)

    # plugin_init
    new_handle = plugin_init(new_config)

    # plugin_start
    plugin_start(new_handle)


def plugin_shutdown(handle):
    try:
        _LOGGER.info('South OpenWeatherMap plugin shutting down.')
        task.stop()
        loop.stop()
    except Exception as e:
        _LOGGER.exception(str(e))
        raise


def plugin_register_ingest(handle, callback, ingest_ref):
    """Required plugin interface component to communicate to South C server

    Args:
        handle: handle returned by the plugin initialisation call
        callback: C opaque object required to passed back to C->ingest method
        ingest_ref: C opaque object required to passed back to C->ingest method
    """
    global c_callback, c_ingest_ref
    c_callback = callback
    c_ingest_ref = ingest_ref


class WeatherReport(object):
    """ Handle integration with OpenWeatherMap API """

    __slots__ = ['_interval', 'url', 'city', 'appid', 'asset_name', '_handler']

    def __init__(self, url, city, appid, rate, asset_name):
        self._interval = float(rate)
        self.url = url
        self.city = city
        self.appid = appid
        self.asset_name = asset_name
        self._handler = None

    def _run(self):
        self.fetch()
        self._handler = loop.call_later(self._interval, self._run)

    def start(self):
        self._handler = loop.call_later(self._interval, self._run)

    def stop(self):
        self._handler.cancel()

    def fetch(self):
        try:
            conn = http.client.HTTPConnection(self.url)
            conn.request('GET', '/data/2.5/weather?q={}&APPID={}'.format(self.city, self.appid))
            r = conn.getresponse()
            res = r.read().decode()
            conn.close()
            if r.status != 200:
                raise ValueError(res)

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
            async_ingest.ingest_callback(c_callback, c_ingest_ref, data)
        except ValueError as ex:
            err = "Unable to fetch information from api.openweathermap: {}".format(str(ex))
            _LOGGER.error(err)
