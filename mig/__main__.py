import sys
import os
from _commands.commands import CommandsHandler

# commands_handler = CommandsHandler(sys.argv,)
#                                        # path_to_launcher=os.path.abspath(__file__))
# commands_handler.process()

# print('123')

if __name__ == '__main__':
    print(os.path.abspath(__file__))
    commands_handler = CommandsHandler(sys.argv,
                                       path_to_launcher=os.path.abspath(__file__))
    commands_handler.process()
