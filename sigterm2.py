import signal
import functools
import asyncio
 
async def looping_task():
    try:
        while True:
            print('internet loop created')
            await asyncio.sleep(5.0)
    except asyncio.CancelledError:
        return "internet loop cancelled"
 
 
async def shutdown(sig, loop):
    print('caught {0}'.format(sig.name))
    tasks = [task for task in asyncio.Task.all_tasks() if task is not
             asyncio.tasks.Task.current_task()]
    list(map(lambda task: task.cancel(), tasks))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print('finished awaiting cancelled tasks, results: {0}'.format(results))
    loop.stop()
 
 
loop = asyncio.get_event_loop()
asyncio.ensure_future(looping_task(), loop=loop)
loop.add_signal_handler(signal.SIGTERM,
                        functools.partial(asyncio.ensure_future,
                                          shutdown(signal.SIGTERM, loop)))
loop.add_signal_handler(signal.SIGINT,
                        functools.partial(asyncio.ensure_future,
                                          shutdown(signal.SIGTERM, loop)))
try:
    loop.run_forever()
finally:
    loop.close()
 