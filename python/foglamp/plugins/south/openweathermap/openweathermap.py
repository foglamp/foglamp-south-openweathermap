

"""HTTP Listener handler for sensor phone application readings"""
import sys
import asyncio
import http.client
import json
from foglamp.common import logger
from foglamp.services.south.ingest import Ingest
from datetime import datetime, timezone
import uuid

__author__ = "Mark Riddoch, Ashwin Gopalakrishnan"
__copyright__ = "Copyright (c) 2018 Dianomic Systems"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_LOGGER = logger.setup(__name__, level=20)

_CONFIG_CATEGORY_NAME = 'openweathermap'
_CONFIG_CATEGORY_DESCRIPTION = 'Weather Report from OpenWeatherMap'
_DEFAULT_CONFIG = {
    'plugin': {
         'description': 'Weather Report from OpenWeatherMap',
         'type': 'string',
         'default': 'openweathermap'
    },
    'url': {
        'description': 'Port to listen on',
        'type': 'string',
        'default': 'api.openweathermap.org'
    },
    'city': {
        'description': 'City to obtain weather report for',
        'type': 'string',
        'default': 'London'
    },
    'appid': {
        'description': 'Application ID registered with OpenWeatherMap',
        'type': 'string',
        'default': 'bbafe18fb275ae5b200d094e36c574ff'
    },
    'rate': {
        'description': 'Rate at which to fetch weather report in seconds',
        'type': 'integer',
        'default': '10'
    }
}


def plugin_info():
    return {'name': 'openweathermap', 'version': '1.0', 'mode': 'async', 'type': 'south',
            'interface': '1.0', 'config': _DEFAULT_CONFIG}


def plugin_init(config):
    """Create the WeatherReport class that will periodically fetch weather data"""

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
        _LOGGER.exception(str(e))
        sys.exit(1)


def plugin_reconfigure(config):
    pass


def plugin_shutdown(task):
    try:
        task.stop()
    except Exception as e:
        _LOGGER.exception(str(e))
        raise


class WeatherReport(object):


        """Handle interation with OpenWeatherMap API

        """


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
                    increment_discarded_counter = True
                    message = {'busy': True}
                 else:
                    asset = 'OpenWeatherMap'
                    timestamp = str(datetime.now(tz=timezone.utc))
                    data = json.loads(res)
                    readings = {'wind_deg': data['wind']['deg'], 'wind_speed': data['wind']['speed'], 
                                'temperature' : data['main']['temp'],
                                'pressure': data['main']['pressure'], 
                                'visibility': data['visibility']}
                    key = str(uuid.uuid4())
                    await Ingest.add_readings(asset=asset, timestamp=timestamp, key=key, readings=readings)

