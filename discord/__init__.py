# -*- coding: utf-8 -*-

"""
Discord API Wrapper
~~~~~~~~~~~~~~~~~~~

A basic wrapper for the Discord API.

:copyright: (c) 2015 Rapptz
:license: MIT, see LICENSE for more details.

"""

__title__ = 'discord'
__author__ = 'Rapptz'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Rapptz'
__version__ = '0.10.0-alpha'

from .client import Client
from .user import User
from .channel import Channel, PrivateChannel
from .server import Server
from .member import Member
from .message import Message
from .errors import *
from .permissions import Permissions
from .role import Role
from .colour import Color, Colour
from .invite import Invite
from .object import Object
from . import utils
from . import opus
from .voice_client import VoiceClient
from .enums import ChannelType, ServerRegion, Status
from collections import namedtuple

import logging

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=0, minor=10, micro=0, releaselevel='alpha', serial=0)

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
