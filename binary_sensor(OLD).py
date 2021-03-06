"""Component for interacting with the Yale Smart Alarm System API Binary Sensors"""
import logging

import voluptuous as vol
from yalesmartalarmclient.client import (
    AuthenticationError,
    YaleSmartAlarmClient,
)


from homeassistant.const import (
    CONF_NAME,
    CONF_PASSWORD,
    CONF_USERNAME,
)

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from datetime import timedelta

CONF_AREA_ID = "area_id"

DEFAULT_NAME = "Yale Smart Alarm"

DEFAULT_AREA_ID = "1"

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

YALE_DOOR_CONTACT_STATE_CLOSED = "closed"
YALE_DOOR_CONTACT_STATE_OPEN = "open"
YALE_DOOR_CONTACT_STATE_UNKNOWN = "unknown"

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_AREA_ID, default=DEFAULT_AREA_ID): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the alarm platform."""
    name = config[CONF_NAME]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    area_id = config[CONF_AREA_ID]

    try:
        client = YaleSmartAlarmClient(username, password, area_id)
    except AuthenticationError:
        _LOGGER.error
        ("Authentication failed. Check credentials")
        return
    
    doors = client.get_doors_status()
    
    status = client._get_authenticated("/api/panel/device_status/");

    for door in doors:
        add_entities([YaleBinarySensor(hass, client, door, doors)], True)

class YaleBinarySensor(Entity):
    """Implementation of a Yale binary sensor."""
    
    def __init__(self, hass, client, device_name, yale_object):
        """Initialize the sensor."""
        self.device_name = device_name
        self.client = client
        self.yale_object = yale_object
        
    @property
    def icon(self):
        return self._icon
        
    @property
    def name(self):
        """Return the name of the sensor."""
        return self.device_name
        
    @property
    def state(self):
        """Return the state of the sensor."""
        if self.device_name in self.yale_object.keys():
            if self.yale_object[self.device_name] == YALE_DOOR_CONTACT_STATE_OPEN:
                self._icon = 'mdi:door-open'
            else:
                self._icon = 'mdi:door-closed'
            return self.yale_object[self.device_name]
        else:
            self._icon = 'mdi:error'
            return YALE_DOOR_CONTACT_STATE_UNKNOWN

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update sensor data."""
        self.yale_object = self.client.get_doors_status()
    
