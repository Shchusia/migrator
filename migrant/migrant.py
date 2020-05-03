import os
import sys
import warnings

from .commands.commands import CommandsHandler

warnings.filterwarnings("ignore")


def _main():
    CommandsHandler(sys.argv, is_run=True,
                    path_to_python=sys.executable,
                    path_to_folder=os.path.abspath(os.curdir),
                    path_to_launcher=os.path.abspath(__file__))


main = _main

if __name__ == '__main__':
    main()
