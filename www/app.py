#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import asyncio,os,time,logging
from datetime import datetime
from aiohttp import web


logging.basicConfig(level=logging.INFO)
def index(request):
    return web.Response(body=b'Index',content_type='text-html',status=200)


async def init(loop):
    app = web.Application(loop = loop)
    app.router.add_route('GET','/',index)
    server = await loop.create_server(app.make_handler(),'localhost',9000)
    logging.info('server start at http://localhost:9000...')
    return server

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()

    