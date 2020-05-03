===============================
``migrant`` - Database schema generation and migration to the database
===============================

Installation
------------


`python setup.py install`



Example 
------

```python

from migrant import Migrate, Connect

# to get how got example str
Connect.get_examples()

str_engine = 'postgresql://{user}:{password}@{host}:{port}/{database_name}'

migrate = Migrate(Connect(str_engine))

migrate.create_and_update()

```