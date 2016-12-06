PyHTML
======

.. image:: https://travis-ci.org/cenkalti/pyhtml.svg?branch=master
   :target: https://travis-ci.org/cenkalti/pyhtml?branch=master

.. image:: https://coveralls.io/repos/github/cenkalti/pyhtml/badge.svg?branch=master
   :target: https://coveralls.io/github/cenkalti/pyhtml?branch=master

PyHTML is a simple HTML generation library for Python.

Inspired by `Flask-HTMLBuilder <http://majorz.github.com/flask-htmlbuilder/>`_
and `this gist <https://gist.github.com/3516334>`_.


Features
--------

* Compatible with Python 2 and 3
* Outputs beautifully indented code
* Some tags have sensible defaults
* Have Blocks for filling them later


Installing
----------

.. code-block:: bash

    $ pip install pyhtml


Documentation
-------------

See the docstring on pyhtml.py file.


Example
-------

.. code-block:: python

    from pyhtml import *


    def f_links(ctx):
        for title, page in [('Home', '/home.html'),
                            ('Login', '/login.html')]:
            yield li(a(href=page)(title))


    t = html(
        head(
            title('Awesome website'),
            script(src="http://path.to/script.js")
        ),
        body(
            header(
                img(src='/path/to/logo.png'),
                nav(
                    ul(f_links)
                )
            ),
            div(
                lambda ctx: "Hello %s" % ctx.get('user', 'Guest'),
                'Content here'
            ),
            footer(
                hr,
                'Copyright 2013'
            )
        )
    )

    print t.render(user='Cenk')


The above code is rendered as:

.. code-block:: html

    <!DOCTYPE html>
    <html>
      <head>
        <title>
          Awesome website
        </title>
        <script src="http://path.to/script.js" type="text/javascript"></script>
      </head>
      <body>
        <header>
          <img src="/path/to/logo.png"/>
          <nav>
            <ul>
              <li>
                <a href="/home.html">
                  Home
                </a>
              </li>
              <li>
                <a href="/login.html">
                  Login
                </a>
              </li>
            </ul>
          </nav>
        </header>
        <div>
          Hello Cenk
          Content here
        </div>
        <footer>
          <hr/>
          Copyright 2013
        </footer>
      </body>
    </html>
