from setuptools import setup, find_packages
import os

version = '0.1'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

test_requires = [
    'WebTest==2.0.18',
    'mock==1.0.1',
]

testing_extras = test_requires + [
    'nose==1.2.1',
    'coverage==3.6',
    'nosexcover==1.0.8',
]

setup(name='eduid_action.tou',
      version=version,
      description="Terms of use plugin for eduid-actions",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Enrique Perez Arnaud',
      author_email='enrique@cazalla.net',
      url='https://github.com/SUNET/',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['eduid_action'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'eduid_actions',
          'jinja2',
          'pymongo>=2.8,<3',
      ],
      extras_require={
          'testing': testing_extras,
      },
      entry_points={
          'eduid_actions.action': ['tou = eduid_action.tou:ToUPlugin'],
          'eduid_actions.add_actions': ['tou = eduid_action.tou:add_tou_actions'],
      },
      )
