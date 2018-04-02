#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Beyon Lee'

'''
test async web application
thanks for Michael Liao
'''

# 详解－－http://www.cnblogs.com/ontheway703/p/4986804.html

# aiohttp，异步 Web 开发框架；jinja2，前端模板引擎；aiomysql，异步 mysql 数据库驱动
# logging，系统日志；asyncio，异步IO；os，系统接口；json，json 编码解码模块；
# time，系统时间模块；datetime，日期模块

import logging;

logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web


def index(request):
    return web.Response(body=b'<h1>Awesome<h1>', headers={'content-type': 'text/html'})


# python3.5之后的新语法，为了简化并更好地标识异步IO
async def init(loop):
    app = web.Application(loop=loop)
    # Application对象有router属性，没有add_route()方法
    app.router.add_route('GET', '/', index)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
