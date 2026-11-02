"""
Pytest configuration and sandbox environment compatibility fixtures for Rover Slim.
Ensures seamless ASGI / Starlette TestClient execution across sandboxed Windows runtimes.
"""

import sys
import os

if sys.platform == "win32":
    # On Windows under AppContainer or restricted sandbox firewalls,
    # loopback TCP socket connection (127.0.0.1) may be blocked with WinError 10013.
    # Python's asyncio ProactorEventLoop uses socket.socketpair() for its self-pipe,
    # which hangs on accept() if TCP loopback is forbidden.
    # We detect if TCP loopback works with a non-blocking check; if not, we use Windows named pipes.
    import socket
    needs_pipe_self_pipe = False
    lsock = None
    csock = None
    try:
        lsock = socket.socket()
        lsock.bind(('127.0.0.1', 0))
        lsock.listen()
        csock = socket.socket()
        csock.settimeout(0.05)
        csock.connect(lsock.getsockname())
    except Exception:
        needs_pipe_self_pipe = True
    finally:
        if csock:
            try:
                csock.close()
            except Exception:
                pass
        if lsock:
            try:
                lsock.close()
            except Exception:
                pass

    if needs_pipe_self_pipe:
        import asyncio
        import asyncio.windows_events
        import asyncio.windows_utils as wu
        import _winapi

        class WindowsPipeSocket:
            def __init__(self, handle, is_reader=False):
                self._handle = handle
                self._is_reader = is_reader

            def fileno(self):
                return self._handle

            def setblocking(self, b):
                pass

            def send(self, data):
                _winapi.WriteFile(self._handle, data)

            def close(self):
                if self._handle:
                    _winapi.CloseHandle(self._handle)
                    self._handle = None

        def _pipe_make_self_pipe(self):
            r, w = wu.pipe(duplex=False, overlapped=(True, False))
            self._ssock = WindowsPipeSocket(r, is_reader=True)
            self._csock = WindowsPipeSocket(w, is_reader=False)
            self._internal_fds += 1

        def _safe_proactor_init(self, proactor=None):
            if proactor is None:
                proactor = asyncio.windows_events.IocpProactor()
            super(asyncio.windows_events.ProactorEventLoop, self).__init__(proactor)

        asyncio.windows_events.ProactorEventLoop.__init__ = _safe_proactor_init
        asyncio.proactor_events.BaseProactorEventLoop._make_self_pipe = _pipe_make_self_pipe
