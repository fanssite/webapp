#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import logging;logging.basicConfig(level=logging.INFO)
import asyncio,json,time,os
from aiohttp import web
from jinja2 import Environment,FileSystemLoader
from datetime import datetime
from www.coroweb import add_routes,add_static
# async def index(request):
#     return web.Response(body=b'<h1>Hello world</h1>',content_type='text/html')

def init_jijna2(app,**kw):
    logging.info('init jinja2...')
    options = dict(
        autoescape = kw.get('autoescape',True),
        block_start_string = kw.get('block_start_string','{%'),
        block_end_string = kw.get('block_end_string','%}'),
        variable_start_string = kw.get('variable_start_string','{{'),
        variable_end_string = kw.get('variable_end_string','}}'),
        auto_reload = kw.get('auto_reload',True)
        )
    path = kw.get('path',None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'template')
        logging.info('set jinja2 template path:%s'%path)
        env = Environment(loader=FileSystemLoader(path),**options)
        filters = kw.get('filters',None)
        if filters is not None:
            for name,f in filters.items():
                env.filters[name] = f
        app['__templating__'] = env

def datetime_filter(t):
    delta = int(time.time()-t)
    if delta <60:
        return u'1分钟前'
    if delta <3600:
        return u'%s分钟前' % (delta/60)
    if delta < 86400:
        return u'%s小时前' % (delta/3600)
    if delta < 604800:
        return u'%s天前' % (delta/86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


async def logger_factory(app, handler):
    async def logger(request):
        logging.info('Request: %s %s' % (request.method, request.path))
        # await asyncio.sleep(0.3)
        return (await handler(request))
    return logger

async def response_factory(app, handler):
    async def response(request):
        logging.info('Response handler...')
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r, int) and r >= 100 and r < 600:
            return web.Response(r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                return web.Response(t, str(m))
        # default:
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp
    return response

async def init(loop):
    app = web.Application(loop = loop,middlewares=[logger_factory,response_factory])
    init_jijna2(app,filters=dict(datetime=datetime_filter),path=r"D:\Users\admin\workspace\python3-webapp\www\template")
    add_routes(app,'www.user_test.blog')
    server =await loop.create_server(app.make_handler(),'localhost',9000)
    logging.info('server start at localhost:9000...')
    return server

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()



