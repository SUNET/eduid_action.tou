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

This plugin records the acceptance by users of new versions of ToU
in a MongoDB database that has a ``tous_accepted`` collection, with
records with the form::

      {
        '_id': ObjectId('234567890123456789012301'),
        'user_oid': ObjectId('123467890123456789014567'),
        'versions': [
            {
                'version': '<version>',
                'ts': <datetime>
                },
            {
                'version': '<version2>',
                'ts': <datetime2>
                }
            ]
        }

Install
-------

Install with pip or easy_install in a python environment
where the eduid-actions app is deployed.

Configure
---------

in the ini configuration of the eduid-actions app, add a setting
with the uri of the mongodb database that holds records for the
users' acceptance of terms of use::

    tou_mongo_uri = mongodb://localhost:27017/eduid_tou

Test
----

Once installed with eduid-actions, test it with::

  $ cd eduid_action.tou/src/
  $ source /path/to/eduid-actions/bin/activate
  $ python /path/to/eduid-actions/eduid_actions/setup.py nosetests

Adding a new ToU version
------------------------

When adding a new ToU, it has to be configured in the following places::

 * In the actions apps, in the eduid_action.tou package there are
   ``eduid_action/tou/versions/<lang>`` directories. Each translation of the 
   terms of use agreement should be placed in the corresponding directory;
   the fileme (the same for all translations) should be the string
   identifying the version with the 'txt' extension, e.g.: ``en/version1.txt``.

 * In the signup app, there is a setting in the INI config file,
   ``tou_version``, that should be set to the string identifying the version.

 * Also in the signup app, there are templates
   ``acceptable_use_policy-<lang>.jinja2`` that must be updated with the
   corresponding texts.

 * Finally, in the IdP, there is a setting ``tou_version`` that has to be
   set to the  string identifying the version.
