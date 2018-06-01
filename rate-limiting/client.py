import aiohttp, asyncio, time


ENDPOINT = 'http://127.0.0.1:8080'
REQ_PER_SEC = 1250


async def do_request(session):
    async with session.get(ENDPOINT) as resp:
        assert await resp.text() == 'pong'



async def load():
    start = time.time()
    count = 0
    async with aiohttp.ClientSession() as session:
        while True:
            asyncio.ensure_future(do_request(session))
            count += 1
            if count / (time.time() - start) >= REQ_PER_SEC:
                await asyncio.sleep(0.05)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(load())