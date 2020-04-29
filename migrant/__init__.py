# -*- coding: utf-8 -*-

import os



__version__ = '0.0.2'
module_name = (os.path.abspath(os.path.dirname(__file__))).split(os.sep)[-1]

from migrant.commands.commands import CommandsHandler
from migrant.migrate.migrate import Migrate
from migrant.connect.db_adaptation.postgres_util import PostgresUtil
from migrant.connect.connect import Connect
from migrant.model.schema import Schema
from migrant.model.model import Column, Reference
import migrant.model.mi_types as mig_types