#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Beyon Lee'

'''
test async web application
thanks for Michael Liao
'''

# 详解--http://www.luameows.wang/2018/03/09/%E5%88%9B%E7%AB%8BORM-%E5%BB%96%E9%9B%AA%E5%B3%B0python%E7%AC%94%E8%AE%B0/
import asyncio, aiomysql
import logging


def log(sql, args=()):
    logging.info('SQL: %s' % sql)


# 创建全局协程连接池
# 每个HTTP请求都可以从连接池中直接获取数据库连接，
# 好处是不必频繁打开关闭数据库连接，能复用就尽量服用
# 连接池由全局变量__pool存储，缺省情况，编码设置为utf-8，自动提交事务
async def create_pool(loop, **kwargs):
    logging.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kwargs.get('host', 'localhost'),
        port=kwargs.get('port', 3306),
        user=kwargs['user'],
        password=kwargs['password'],
        db=kwargs['db'],
        charset=kwargs.get('charset', 'utf8'),
        autocommit=kwargs.get('autocommit', True),
        maxsize=kwargs.get('maxsize', 10),
        minsize=kwargs.get('minsize', 1),
        loop=loop
    )


# 要执行SELECT语句，我们用select函数执行，需要传入SQL语句和SQL参数
async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    async with __pool.get() as conn:  # 从连接池获取一个connect
        async with conn.cursor(aiomysql.DictCursor) as cur:  # 获取游标cursor
            await cur.execute(sql.replace('?', '%s'), args or ())  # 将输入的sql语句中的‘？’替换为具体参数args
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        logging.info('rows returned: %s' % len(rs))
        return rs


# 要执行INSERT、UPDATE、DELETE语句，可以定义一个通用的execute()函数，
# 因为这3种SQL的执行都需要相同的参数，以及返回一个整数表示影响的行数
async def execute(sql, args, autocommit=True):
    log(sql)
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        return affected
