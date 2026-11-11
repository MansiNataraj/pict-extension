"""All API routers. `ALL_ROUTERS` is what main.py mounts.

crt          - select-to-translate with CRT questions (the browser extension uses only this)
speech, chat_reply, coach, analyse, reply - legacy web-app endpoints
"""
from . import analyse, chat_reply, coach, crt, reply, speech

ALL_ROUTERS = [crt.router, speech.router, chat_reply.router, coach.router, analyse.router, reply.router]
