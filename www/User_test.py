#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#import functools
# from www import orm
# from www.models import User,Blog,Comment
# import asyncio
# async def test():
#     u = User(id='001',name='test1', email='test1@example.com', password='123456', image='about:blank')
#     await orm.create_pool(loop=loop,user='root',password='admin123',db='awesome') 
#     await u.save()
# 
# loop=asyncio.get_event_loop()
# loop.run_until_complete(test())

#处理request


# def Handler_decrator(*,path,method):
#     def decrator(func):
#         @functools.wraps(func)
#         def wrapper(*args,**kw):
#             return func(*args,**kw)
#         wrapper.__route__=path
#         wrapper.__method__=method
#         return wrapper
#     return decrator
# 
# get = functools.partial(Handler_decrator,method='GET')
# post = functools.partial(Handler_decrator,method='POST')



import asyncio
from www.coroweb import get,post

@get('/')
async def blog(request):
    return r'<h1>Awesome</h1>'
@get('/greeting')
async def greeting(*,name,request):
    body=('<h1>Awesome: /greeting %s</h1>'%name)
    return body