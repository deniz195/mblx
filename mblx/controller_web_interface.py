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


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'tolist'):
            return obj.tolist()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


from math import log10, floor
def round_to_sig(x, sig=2):
    return round(x, sig-1-int(floor(log10(abs(x)))))




class BaseControllerWebInterface(Service):

    # action_template = 'action.html'

    # controller_funcs = ["trigger_stop_scan",
    #         "trigger_run_scan",
    #         "trigger_manual_homing",
    #         "trigger_run_bkg",
    #         "trigger_lds_background",
    #         'trigger_motors_off',
    #         'trigger_motors_on']

    # livedata_template = 'livedata.html'

    def __init__(self, port = 8080, template_dir = './templates'):
        super().__init__()
        self.controller = None
        self.port = port
        self.app = None

        self.template_dir = template_dir

    def set_controller(self, controller):
        self.controller = controller

    async def get_all_data(self):
        all_data = {}
        all_data.update(await self.controller.get_data())
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




    # async def action_get(self, request):
    #     all_data = await self.get_all_data()

    #     response = aiohttp_jinja2.render_template(self.action_template,
    #                                               request,
    #                                               all_data)
    #     response.headers['Content-Language'] = 'en'
    #     return response

    # async def livedata_get(self, request):
    #     all_data = await self.get_all_data()

    #     response = aiohttp_jinja2.render_template(self.livedata_template,
    #                                               request,
    #                                               all_data)
    #     response.headers['Content-Language'] = 'en'
    #     return response
        

    # async def action_json(self, request):
    #     func = request.query.get('func', None)
    #     query_params = request.query.keys()

    #     return_data = {}
    #     return_data['result'] = None

    #     self.log.info(f'action.json: search...')

    #     if func in self.controller_funcs:
    #         self.log.info(f'action.json: {func}')
    #         coro = getattr(self.lds_ctrl, func)

    #         coro_argspec = inspect.getargspec(coro)
    #         # print(coro_argspec)

    #         coro_args = coro_argspec[0]
    #         coro_args.remove('self')
    #         # print(coro_args)

    #         # print(query_params)

    #         valid_params = list(set(coro_args) & set(query_params))
    #         # print(valid_params)
    #         coro_kwds = {p: json.loads(request.query[p]) for p in valid_params}
    #         print(repr(coro_kwds))

    #         return_data['result'] = await coro(**coro_kwds)
    #     else:
    #         self.log.warn(f'action.json: {func} not found!')


    #     json_data = json.dumps(return_data, indent=4, cls=NumpyEncoder)

    #     # Wrap in callback function for JSONP
    #     callback_function = request.query.get('callback', None)
    #     if callback_function is not None:
    #         json_data = ''.join([callback_function, '(', json_data, ')'])

    #     resp = web.Response()
    #     resp.text = json_data
    #     resp.content_type = 'application/json'

    #     return resp

    def get_web_app(self):
        return self.app

    async def on_start(self):
        await super().on_start()

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





