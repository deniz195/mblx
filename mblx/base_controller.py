#!/usr/local/bin/python3.6
import asyncio
from aiohttp import web  

import aiohttp_jinja2
import jinja2
import json

import logging
import subprocess
import time
import datetime
import socket

from mode import Service

##################################################
# general useful module components
def _reload_module():
    import sys
    import importlib
    current_module = sys.modules[__name__]
    module_logger.info('Reloading module %s' % __name__)
    importlib.reload(current_module)
##################################################
# create logger
import logging
module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.DEBUG)
##################################################



class BaseControllerService(Service):
    def __init__(self):
        super().__init__()

    async def get_data(self):
        return {}



    # # async def on_first_start(self):
    # #     await super().on_first_start()
    # #     self.coater_axes = self.add_dependency(self.coater_axes)

    # async def trigger_motors_off(self):
    #     self.log.info('Trigger motors off')
    #     return await self.get_axes().turn_off()

    # async def trigger_motors_on(self):
    #     self.log.info('Trigger motors on')
    #     return await self.get_axes().turn_on()

    # async def trigger_stop_scan(self):
    #     # this should be improved to wait for finish
    #     self.log.info('Trigger stop scan')
    #     self.get_axes().stop_read_continuously()

    # async def trigger_run_scan(self):
    #     self.log.info('Trigger run scan')
    #     self.get_axes().trigger_read_continuously()

    # async def trigger_lds_background(self, t=3):
    #     self.log.info('trigger_lds_background')
    #     return await self.get_axes().trigger_background(t=t)


    # # async def trigger_run_bkg(self):
    # #     self.log.info('Trigger bkg scan')
    # #     self.coater_axes.trigger_read_continuously()
    # #     self.bkg_done.clear()
    # #     self.bkg_datas = []
        
    # #     await self.bkg_done.wait()
    # #     self.log.info('Bkg scan done!')

    # # async def trigger_manual_homing(self):
    # #     self.log.info('Trigger manual homing')
    # #     return await self.coater_axes.do_manual_homing()


    # async def trigger_point_measurement(self, t=3, do_zero = False):
    #     self.log.info('Trigger point measurement')
    #     if do_zero:
    #         self.log.info('Doing auto offset.')
    #         await self.get_axes().trigger_background(t=t)

    #     result = await self.get_axes().read_lds_data(t=t)
    #     return result

