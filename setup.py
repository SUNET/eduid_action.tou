from setuptools import setup, find_packages
import os
import sys

try:
    from babel.messages import frontend as babel
except ImportError:
    print "Babel is not installed, you can't localize this package"
    cmdclass = {}
else:
    cmdclass = {
        'compile_catalog': babel.compile_catalog,
        'extract_messages': babel.extract_messages,
        'init_catalog': babel.init_catalog,
        'update_catalog': babel.update_catalog
    }


version = '0.1.2b1'

requires = []

if sys.version_info[0] < 3:
    # Babel does not work with Python 3
    requires.append('Babel==1.3')
    requires.append('lingua==1.5')

idp_extras = [
]

am_extras = [
    'eduid_userdb>=0.0.4',
]

actions_extras = [
    'eduid_actions>=0.0.1',
    'setuptools>=2.2',
]

test_requires = [
    'eduid_actions>=0.0.1',
    'eduid_userdb>=0.0.4',
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
      packages=['eduid_action.tou'],
      package_dir = {'': 'src'},
      namespace_packages=['eduid_action'],
      include_package_data=True,
      zip_safe=False,
      cmdclass=cmdclass,
      install_requires=requires,
      extras_require={
          'idp': idp_extras,
          'am': am_extras,
          'actions': actions_extras,
          'testing': testing_extras,
          },
      entry_points={
          'eduid_actions.action':
                    ['tou = eduid_action.tou.action:ToUPlugin'],
          'eduid_actions.add_actions':
                    ['tou = eduid_action.tou.idp:add_tou_actions'],
          'eduid_am.attribute_fetcher':
                    ['tou = eduid_action.tou.am:attribute_fetcher'],
          'eduid_am.plugin_init':
                    ['tou = eduid_action.tou.am:plugin_init'],
          },
      )
