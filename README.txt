.. contents::

Introduction
============

Terms of use plugin for eduid-actions.

New versions of ToU must be commited as
``src/eduid_action/tou/versions/<lang>/<version>.txt``.

Actions in the eduid_actions MongoDB database for this plugin have the
form::

      {
        '_id': ObjectId('234567890123456789012301'),
        'user_oid': ObjectId('123467890123456789014567'),
        'action': 'tou',
        'preference': 100,
        'params': {
            'version': '<version>'
            }
        }

Install
-------

Install with pip or easy_install in a python environment
where the eduid-actions package is deployed.

Test
----

Once installed with eduid-actions, test it with::

  $ cd eduid_action.tou/src/
  $ source /path/to/eduid-actions/bin/activate
  $ python /path/to/eduid-actions/eduid_actions/setup.py nosetests
