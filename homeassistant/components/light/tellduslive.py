"""
homeassistant.components.light.tellduslive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Support for Tellduslive lights.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/light.tellduslive/
"""
import logging

from homeassistant.components.light import Light, ATTR_BRIGHTNESS
from homeassistant.const import (STATE_ON, STATE_OFF, EVENT_HOMEASSISTANT_STOP, ATTR_FRIENDLY_NAME)
from homeassistant.components import tellduslive

SIGNAL_REPETITIONS = 1

_LOGGER = logging.getLogger(__name__)
DEPENDENCIES = ['tellduslive']

def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Find and return Tellstick switches. """
    signal_repetitions = config.get('signal_repetitions', SIGNAL_REPETITIONS)
    core_devices = tellduslive.NETWORK.get_lights()

    lights = []
    for device in core_devices:
        lights.append(TelldusLiveLight(device, signal_repetitions))

    add_devices(lights)


class TelldusLiveLight(Light):
    """ Represents a Tellstick light. """

    def __init__(self, tellstick_device, signal_repetitions):
        self.tellstick_device = tellstick_device
        self.state_attr = {ATTR_FRIENDLY_NAME: tellstick_device["name"]}
        self.signal_repetitions = signal_repetitions
        self._brightness = tellstick_device["statevalue"];

    @property
    def name(self):
        """ Returns the name of the switch if any. """
        return self.tellstick_device["name"]

    @property
    def is_on(self):
        """ True if switch is on. """
        return int(self._brightness) > 0

    @property
    def brightness(self):
        """ Brightness of this light between 0..255. """
        return self._brightness

    def turn_off(self, **kwargs):
        """ Turns the switch off. """
        for _ in range(self.signal_repetitions):
            tellduslive.NETWORK.turn_switch_off(self.tellstick_device["id"])
        self._brightness = 0
        self.update_ha_state()

    def turn_on(self, **kwargs):
        """ Turns the switch on. """
        brightness = kwargs.get(ATTR_BRIGHTNESS)

        if brightness is None:
            self._brightness = 255
        else:
            self._brightness = int(brightness)

        for _ in range(self.signal_repetitions):
            tellduslive.NETWORK.dim_light(self.tellstick_device["id"], self._brightness)
        self.update_ha_state()

    @property
    def should_poll(self):
        """ Tells Home Assistant not to poll this entity. """
        return False
