import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

from migrant.__init__ import (__version__,
                              module_name, )

requirements = [
    'psycopg2',
    'dictdiffer',
    'PyYAML',
    'SQLAlchemy',
]


def get_packages():
    ignore = ['__pycache__']

    list_sub_folders_with_paths = [x[0].replace(os.sep, '.')
                                   for x in os.walk(module_name)
                                   if x[0].split(os.sep)[-1] not in ignore]
    return list_sub_folders_with_paths


setup(name=module_name,
      version=__version__,
      url='https://github.com/Shchusia/migrator',
      author='Denis Shchutkiy',
      author_email='denisshchutskyi@gmail.com',
      description='Make migrations',
      packages=get_packages(),
      # package_data={'': ['stdlib','mapping']},
      packages_dir={module_name: module_name},
      license='Apache License',
      long_description=open('README.md').read(),
      zip_safe=False,
      install_requires=requirements,
      include_package_data=False,
      test_suite='tests',
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 3', ],
      python_requires='>=3.6',
      entry_points={
          'console_scripts': [
              '{module_name}={module_name}:main'.format(module_name=module_name),
          ], },
      )

# print(get_packages())
