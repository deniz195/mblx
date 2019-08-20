# using aiohttp for video streaming
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

import inspect
 
from mode import Service, Signal
from .common import NumpyEncoder, round_to_sig
from .basic_web_interface import BasicWebInterface


class BaseControllerWebInterface(BasicWebInterface):

    def __init__(self, port = 8080, template_dir = './templates'):
        super().__init__(port=port, template_dir=template_dir)
        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    async def get_all_data(self):
        all_data = await super().get_all_data()
        all_data.update(await self.controller.get_data())

        return all_data

    async def setup_server(self):
        await super().setup_server()

        self.log.info('Registering sensors.json...')

        app.router.add_route('GET', '/current_data.json', self.data_jsonp)
        app.router.add_route('GET', '/sensors.json', self.data_jsonp)
        app.router.add_route('GET', '/data.json', self.data_jsonp)


