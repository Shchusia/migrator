# -*- coding: utf-8 -*-

import os
import sys

__version__ = '0.0.25'
module_name = (os.path.abspath(os.path.dirname(__file__))).split(os.sep)[-1]

from .commands.commands import CommandsHandler
from .migrate.migrate import Migrate
from .connect.db_adaptation.postgres_util import PostgresUtil
from .connect.connect import Connect
from .model.schema import Schema
from .model.model import Column, Reference
import migrant.model.mi_types as mig_types

import warnings

warnings.filterwarnings("ignore")


def main():
    CommandsHandler(sys.argv,
                    path_to_launcher=os.path.abspath(__file__),
                    is_run=True,
                    path_to_python=sys.executable,
                    path_to_folder=os.path.abspath(os.curdir), )


if __name__ == '__main__':
    main()
