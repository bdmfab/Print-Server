"""
microdot
--------

The ``microdot`` module defines a few classes that help implement HTTP-based
servers for MicroPython and standard Python.
"""
import asyncio
import io
import re
import time

try:
    import orjson as json
except ImportError:
    import json

try:
    from inspect import iscoroutinefunction, iscoroutine
    from functools import partial

    async def invoke_handler(handler, *args, **kwargs):
        """Invoke a handler and return the result.

        This method runs sync handlers in a thread pool executor.
        """
        if iscoroutinefunction(handler):
            ret = await handler(*args, **kwargs)
        else:
            ret = await asyncio.get_running_loop().run_in_executor(
                None, partial(handler, *args, **kwargs))
        return ret
except ImportError:  # pragma: no cover
    def iscoroutine(coro):
        return hasattr(coro, 'send') and hasattr(coro, 'throw')

    async def invoke_handler(handler, *args, **kwargs):
        """Invoke a handler and return the result.

        This method runs sync handlers in the asyncio thread, which can
        potentially cause blocking and performance issues.
        """
        ret = handler(*args, **kwargs)
        if iscoroutine(ret):
            ret = await ret
        return ret

try:
    from sys import print_exception
except ImportError:  # pragma: no cover
    import traceback

    def print_exception(exc):
        traceback.print_exc()

MUTED_SOCKET_ERRORS = [
    32,  # Broken pipe
    54,  # Connection reset by peer
    104,  # Connection reset by peer
    128,  # Operation on closed socket
]


def urldecode(s):
    if isinstance(s, str):
        s = s.encode()
    s = s.replace(b'+', b' ')
    parts = s.split(b'%')
    if len(parts) == 1:
        return s.decode()
    result = [parts[0]]
    for item in parts[1:]:
        if item == b'':
            result.append(b'%')
        else:
            code = item[:2]
            result.append(bytes([int(code, 16)]))
            result.append(item[2:])
    return b''.jo