import asyncio
import json
import time, sys
from collections import OrderedDict

from aiohttp import web

# how many seconds to keep requests counts recorded
RATE_PERIODS = 360
UPDATE_RATE = 5


def record(request):
    # for simple example, we're keeping stats in app object
    # but this could be another service that records
    # these and does rate calculation in another manner
    current_second = int(time.time())
    if current_second not in app.settings['counts']:
        app.settings['counts'][current_second] = 0
    app.settings['counts'][current_second] += 1


def calculate_rate(app, interval):
    count = 0
    # one second back since current second hasn't finished
    current_second = int(time.time()) - 1
    for relative_second in range(interval):
        count += app.settings['counts'].get(current_second - relative_second, 0)
    return int(count / interval)


@web.middleware
async def stats_middleware(request, handler):
    resp = await handler(request)
    record(request)
    return resp


async def ping(request):
    return web.Response(text="pong")


async def rate(request):
    try:
        interval = int(request.query.get('interval'))
    except TypeError:
        # default over 5 seconds seems reasonable
        interval = 5

    return web.Response(text=json.dumps({
        'rate': calculate_rate(request.app, interval)
    }), headers={
        'Content-Type': 'application/json'
    })
    return web.Response(text="pong")


async def management_task(app):
    await asyncio.sleep(1)
    sys.stdout.write('\n\nKeeping stats...\n\n')
    sys.stdout.flush()
    while True:
        while len(app.settings['counts']) > RATE_PERIODS:
            app.settings['counts'].pop(app.settings['counts'].keys()[0])
        sys.stdout.write("\rReq/sec: {}, over last {} seconds".format(
            calculate_rate(app, UPDATE_RATE),
            UPDATE_RATE
        ))
        sys.stdout.flush()
        await asyncio.sleep(UPDATE_RATE)  # how often to update


async def on_startup(app):
    app.settings['management_task'] = asyncio.ensure_future(management_task(app))


async def on_cleanup(app):
    app.settings['management_task'].cancel()


app = web.Application(middlewares=[stats_middleware])
app.settings = {
    # in Python 3.6 dicts are already ordered as well but this is
    # explicitly showing that the code depends on ordered dict keys
    'counts': OrderedDict(),
    'management_task': None
}

if __name__ == '__main__':
    app.add_routes([web.get('/', ping)])
    app.add_routes([web.get('/rate', rate)])
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    web.run_app(app)
