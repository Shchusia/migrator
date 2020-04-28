from _migrate import Migrate
from _connect import Connect
from _model import Model, Schema, Column, Reference
from _db_adaptation import (PostgresUtil)
import _types as mig_types
import sys

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")
# -*- coding: utf-8 -*-

__author__ = 'Denis Shchutskiy'
__email__ = 'denisshchutskyi@gmail.com'
__version__ = '0.0.1'

print(__version__)