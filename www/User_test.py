#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from www import orm
from www.models import User,Blog,Comment
import asyncio
async def test():
    u = User(id='001',name='test1', email='test1@example.com', password='123456', image='about:blank')
    await orm.create_pool(loop=loop,user='root',password='admin123',db='awesome') 
    await u.save()

loop=asyncio.get_event_loop()
loop.run_until_complete(test())