This client library has been deprecated.
----------------------------------------
This library will no longer be supported and does not support OAuth2. 
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Please visit our `Python Examples<https://github.com/aweber/public-api-examples/tree/master/python>` as a reference.
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

AWeber API Python Library
------------------------- 
The AWeber API Python Library allows you to quickly get up and running with
integrating access to the AWeber API into your Python applications. This
library requires the python-oauth2 to handle the authentication. 

.. image:: https://secure.travis-ci.org/aweber/AWeber-API-Python-Library.png?branch=master
    :target: https://secure.travis-ci.org/aweber/AWeber-API-Python-Library

.. image:: https://pypip.in/v/aweber_api/badge.png
    :target: https://pypi.python.org/pypi/aweber_api/
    :alt: Latest Version

.. image:: https://pypip.in/license/aweber_api/badge.png
    :target: https://pypi.python.org/pypi/aweber_api/
    :alt: License

Installation
============

The library can be installed by checking out the source::

    $ sudo python setup.py install

Or can be installed using easy_install::

    $ easy_install aweber_api

Or pip::

    $ pip install aweber_api

Compatibility
=============
The client library has been tested as compatible with python versions:

* 2.6
* 2.7

Testing
=======

Place the client library into a virtualenv and execute the test suite by running the following command::

    $ python setup.py nosetests

Also, the project can use tox to run against multiple versions of python.  The tox package is available 
from pypi here::

    https://pypi.python.org/pypi/tox

Instructions for how to use and configure tox can be found here::

    http://tox.readthedocs.org/en/latest/#

Currently, running tox will require that both python 2.6 and python 2.7 are installed.

Additional interpreters may be installed and the tox.ini file must be modified to include the
newly added interpreters.  Once the interpreters are installed, the tests can be run via::

    $ tox


Usage
=====

To connect the AWeber API Python Libray, you simply include the main class,
AWeberAPI in your application, then create an instace of it with your 
application's consumer key and secret.::

    from aweber_api import AWeberAPI
    aweber = AWeberAPI(consumer_key, consumer_secret)
    account = aweber.get_account(access_token, token_secret)

    for list in account.lists:
        print list.name

Handling Errors
+++++++++++++++

Sometimes errors happen and your application should handle them appropriately.
Whenever an API error occurs an AWeberAPIException will be raised with a
detailed error message and documentation link to explain whats wrong.

You should wrap any calls to the API in a try/except block.

Common Errors:
 * Resource not found (404 error)
 * Your application has been rate limited (403 error)
 * Bad request (400 error)
 * API Temporarily unavailable (503 error)

Refer to https://labs.aweber.com/docs/troubleshooting for the complete list::

    from aweber_api import AWeberAPI, APIException
    aweber = AWeberAPI(consumer_key, consumer_secret)
    account = aweber.get_account(access_token, token_secret)


    try:
        invalid_resource = account.load_from_url('/idontexist')
    except APIException, exc:
        print '404! {0}'.format(exc)

    try:
        print len(account.lists)
    except APIException, exc:
        print 'hmm, something unexpected happened!: {0}'.format(exc)


Getting request tokens / access tokens
++++++++++++++++++++++++++++++++++++++

You can also use the AWeberAPI object to handle retrieving request tokens::

    from aweber_api import AWeberAPI
    aweber = AWeberAPI(consumer_key, consumer_secret)
    request_token, request_token_secret = aweber.get_request_token(callback_url)
    print aweber.authorize_url

As well as access tokens::

    from aweber_api import AWeberAPI
    aweber = AWeberAPI(consumer_key, consumer_secret)
    aweber.user.verifier = verifier
    aweber.user.request_token = request_token
    aweber.user.token_secret = request_token_secret
    access_token, access_token_secret = aweber.get_access_token()


Full Pylons example
+++++++++++++++++++

Here is a simple Pylons example that uses the AWeber API Python Library to get
a request token, have it authorized, and then print some basic stats about the
web forms in that user's lists::

    from pylons import session, request, tmpl_context as c
    from pylons.controllers.util import redirect 

    from awebertest.lib.base import BaseController, render

    from aweber_api import AWeberAPI

    url = 'http://localhost:5000'
    consumer_key = "vjckgsr5y4gfOa3PWnf"
    consumer_secret = "u3sQ7vGGJBfds4q5dfgsTESi685c5x2wm6gZuIj"
    class DemoController(BaseController):

        def __before__(self):
            self.aweber = AWeberAPI(consumer_key, consumer_secret)

        def index(self):
            token, secret = self.aweber.get_request_token(url+'/demo/get_access')
            session['request_token_secret'] = secret
            session.save()
            redirect(self.aweber.authorize_url)

        def get_access(self):
            self.aweber.user.request_token = request.params['oauth_token']
            self.aweber.user.token_secret = session['request_token_secret']
            self.aweber.user.verifier = request.params['oauth_verifier']
            session['token'], session['secret'] = self.aweber.get_access_token()
            session.save()
            redirect(url+'/demo/show')

        def show(self):
            c.account = self.aweber.get_account(session['token'], session['secret'])
            return render('data.mako')


In `data.mako`::

    <!DOCTYPE html>
    <html lang="en">
        <body>
            <h1>Web Forms</h1>
            % for list in c.account.lists:
            <b>List Id:</b> ${list.id}, name: ${list.name}<br />
            <b>Currently has:</b> ${len(list.web_forms)} web forms
            <ul>
            % for form in list.web_forms:
                <li>Form Id: ${form.id}, name: ${form.name}</li>
            % endfor
            </ul>
            % endfor
        </body>
    </html>
