===============================
``migrant`` - Database schema generation and migration to the database
===============================

Installation
------------


`python setup.py install`

Usage
-----
```
Usage:
    migrant [options [--data option]]

Options '-h'
init            to initialize the necessary files and directories 
upgrade         to create migrations of unsaved data 
                important:
                    add to migrations.__main__.py imports model
downgrade       to downgrade schema
status          to get difference between 
migrate         implement migrations story


```

Example 
------
###### model.py
```python
from migrant import Schema, Column, Reference
from migrant import mig_types



class User(Schema):
    __tablename__ = 'users'
    id = Column(mig_types.Int, primary_key=True)
    name = Column(mig_types.Varchar(5))


class UserInfo(Schema):
    address = Column(mig_types.Int)
    ref_user = Column(mig_types.Int, reference=Reference(User,
                                                         ref_to_column_table=User.id,
                                                         on_delete='cascade',
                                                         on_update='SET NULL'))

```

###### main.py
```python

from migrant import Migrate, Connect
from model import *
# to get how got example str
Connect.get_examples()

str_engine = 'postgresql://{user}:{password}@{host}:{port}/{database_name}'

connect = Connect(str_engine)

migrate = Migrate()
migrate.create_and_update()


select = '''
SELECT * 
FROM 
'''
db_instance = connect.get_instance()
db_instance.make_select_request()

```