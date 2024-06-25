import logging
from homeassistant.components.sensor import SensorEntity
from ...iceicedata.data_processing import get_weather_data

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    async_add_entities([IceIceDataSensor(config_entry.data)])

class IceIceDataSensor(SensorEntity):
    def __init__(self, config):
        self._name = config.get("name", "IceIceData Sensor")
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        self._state = get_weather_data()
