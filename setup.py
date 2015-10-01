from setuptools import setup, find_packages
import os
import sys

version = '0.1.0b1'

requires = [
    'pymongo>=2.8,<3',
    'jinja2>=2.8',
    'eduid_actions>=0.0.1b0',
    'eduid_signup_amp>=0.2.9b1',
    'setuptools>=2.2',
] 

if sys.version_info[0] < 3:
    # Babel does not work with Python 3
    requires.append('Babel==1.3')
    requires.append('lingua==1.5')


test_requires = [ 
    'WebTest==2.0.15',
    'mock==1.0.1',
]


testing_extras = test_requires + [
    'nose==1.3.3',
    'coverage==3.7.1',
    'nosexcover==1.0.10',
]

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
      install_requires=requires,
      extras_require={
          'testing': testing_extras,
          },
      entry_points={
          'eduid_actions.action': ['tou = eduid_action.tou:ToUPlugin'],
          'eduid_actions.add_actions': ['tou = eduid_action.tou:add_tou_actions'],
          },
      )
