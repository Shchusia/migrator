# -*- coding: utf-8 -*-

import os



__version__ = '0.0.2'
module_name = (os.path.abspath(os.path.dirname(__file__))).split(os.sep)[-1]

from migrant.commands.commands import CommandsHandler
from migrant.migrate.migrate import Migrate
from migrant.model.schema import Schema