
import os
import sys
from docopt import docopt
from migrant.__init__ import __version__



from .commands.commands import CommandsHandler
from .migrate.migrate import Migrate
from .connect.db_adaptation.postgres_util import PostgresUtil
from .connect.connect import Connect
from .model.schema import Schema
from .model.model import Column, Reference
import migrant.model.mi_types as mig_types


def _main():
    CommandsHandler(sys.argv,
                    path_to_launcher=os.path.abspath(__file__))

main = _main

if __name__ == '__main__':
    main()