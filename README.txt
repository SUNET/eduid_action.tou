.. contents::

Introduction
============

Terms of use plugin for eduid-actions.

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
in the user db, as attributes of the user records. To learn the details
of the stored objects, please see the docs in eduid-userdb.

Install
-------

This plugin has to be installed in 3 different environments:
in the IdP, in the actions app, and in the attribute manager.

IdP
...

It adds an entry point that the IdP uses once the user is authenticated
and before it checks whether there are pending actions, and that can
add a new ToU action.

Install it with::

    pip install eduid_action.tou[idp]

Actions App
...........

The main functionality of the plugin, where it presents the user with the
new terms of use and records its acceptance.

Install it with::

    pip install eduid_action.tou[actions]

Attribute manager
.................

Once the ToU acceptance has been recorded in the db local to the actions app,
it needs to be propagated to the central user db by the AM. Installing the
package here instructs the am what to do in this regard.

Install it with::

    pip install eduid_action.tou[am]

Configure
---------

in the ini configuration of the eduid-actions app, add a setting
with the uri of the mongodb database that holds records for the
users' acceptance of terms of use::

    tou_mongo_uri = mongodb://localhost:27017/eduid_tou

In the other apps the only thing that needs configuring are the ToU versions.

Adding a new ToU version
------------------------

When adding a new ToU, it has to be configured in the following places::

 * In the actions apps, in the eduid_action.tou package there are
   ``eduid_action/tou/versions/<lang>`` directories. Each translation of the 
   terms of use agreement should be placed in the corresponding directory;
   the filename (the same for all translations) should be the string
   identifying the version with the 'txt' extension, e.g.: ``en/version1.txt``.

 * In the signup app, there is a setting in the INI config file,
   ``tou_version``, that should be set to the string identifying the version.

 * Also in the signup app, there are templates
   ``acceptable_use_policy-<lang>.jinja2`` that must be updated with the
   corresponding texts.

 * Finally, in the IdP, there is a setting ``tou_version`` that has to be
   set to the  string identifying the version.

Test
----

Once installed with eduid-actions, test it with::

  $ cd eduid_action.tou/src/
  $ source /path/to/eduid-actions/bin/activate
  $ python /path/to/eduid-actions/eduid_actions/setup.py nosetests
