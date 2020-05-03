### migrator


# make requirements
pipreqs C:\Users\denis\PycharmProjects\mig --encoding=utf8


```python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from migrant import (__version__,
                     module_name, )
# from setuptools import find_packages

requirements = [
    'psycopg2',
    'dictdiffer',
    'PyYAML',
    'SQLAlchemy',
]
def get_packages():
    ignore = ['__pycache__']
    list_subfolders_with_paths = [module_name+'.'+f.name for f in os.scandir(module_name) if f.is_dir() and f.name not in ignore]
    list_subfolders_with_paths.append(module_name)
    # print(list_subfolders_with_paths)
    return list_subfolders_with_paths
    
setup(name=module_name,
      version=__version__,
      url='https://github.com/Shchusia/migrator',
      author='Denis Shchutkiy',
      author_email='denisshchutskyi@gmail.com',
      description='Make migrations',
      license='MIT',
      # packages=[module_name],
      # long_description=open('README.md').read(),
      zip_safe=False,
      install_requires=requirements,
      include_package_data=True,
      # package_dir={module_name: module_name},
      entry_points={
        'console_scripts': [
            '{module_name}={module_name}:main'.format(module_name=module_name),
        ],},
      )

```