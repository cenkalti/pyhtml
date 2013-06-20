PyHTML
======

PyHTML is a simple HTML generation library for Python.

Inspired by `Flask-HTMLBuilder <http://majorz.github.com/flask-htmlbuilder/>`_
and `this gist <https://gist.github.com/3516334>`_.


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


Installing
----------

    pip install pyhtml

or download pyhtml.py into your project directory. There are no hard dependencies other than the Python standard library. PyHTML is tested with Python 2.7 only.


Documentation
-------------

See the docstring on pyhtml.py.
