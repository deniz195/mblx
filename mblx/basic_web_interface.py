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



class BasicWebInterface(Service):

    def __init__(self, port = 8080, template_dir = './templates'):
        super().__init__()
        self.port = port
        self.app = None

        self.template_dir = template_dir


    async def get_all_data(self):
        all_data = {}
        all_data['host_name'] = socket.gethostname()
        all_data['request_time'] = time.time()
        
        return all_data

    async def data_jsonp(self, request):

        all_data = await self.get_all_data()

        json_data = json.dumps(all_data, indent=4, cls=NumpyEncoder)

        # Wrap in callback function for JSONP
        callback_function = request.query.get('callback', None)
        if callback_function is not None:
            json_data = ''.join([callback_function, '(', json_data, ')'])

        resp = web.Response()
        resp.text = json_data
        resp.content_type = 'application/json'

        return resp



    def get_web_app(self):
        return self.app

    async def setup_server(self):
        self.log.info('WebInterface starting...')

        logging.getLogger('aiohttp').setLevel(logging.WARN)

        # setup application
        app = web.Application() 
        self.app = app

        # app.router.add_static('/data', './data', show_index=True)
        # app.router.add_static('/code', './templates', show_index=True)
        # app.router.add_route('GET', '/action', self.action_get)
        # app.router.add_route('POST', '/action', self.action_post)
        # app.router.add_route('GET', '/point', self.point_get)
        # app.router.add_route('GET', '/livedata', self.livedata_get)

        app.router.add_route('GET', '/current_data.json', self.data_jsonp)
        app.router.add_route('GET', '/sensors.json', self.data_jsonp)
        app.router.add_route('GET', '/data.json', self.data_jsonp)
        # app.router.add_route('GET', '/action.json', self.action_json)

        aiohttp_jinja2.setup(app,
            loader=jinja2.FileSystemLoader(self.template_dir))

        jinja_env = aiohttp_jinja2.get_env(app)

        def format_datetime(value, format='medium'):
            if format == 'full':
                format="'%Y-%m-%d %H:%M:%S'"
            elif format == 'medium':
                format="'%Y-%m-%d %H:%M:%S'"

            return datetime.datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')    

        jinja_env.filters['datetime'] = format_datetime

        # setup setup app
        self.log.info('setup aiohttp app')
        self.handler = app.make_handler()


    async def on_start(self):
        await super().on_start()
        await self.setup_server()

        self.srv = await self.loop.create_server(self.handler, '0.0.0.0', self.port)
        self.log.info('serving on' + str(self.srv.sockets[0].getsockname()))


    async def on_stop(self):
        try:
            self.log.info('Shutdown aiohttp server')        
            self.srv.close()
            await self.srv.wait_closed()
            await self.handler.finish_connections(1.0)
            await self.app.finish()
        except AttributeError as e:
            pass

        await super().on_stop()





