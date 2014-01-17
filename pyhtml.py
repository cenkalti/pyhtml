"""

PyHTML
======

Simple HTML generator for Python.


Usage:

Lets create a tag.

>>> t = div()
>>> t
div()


Tags can be rendered by converting to string.

>>> str(t)
'<div></div>'

Printing an object automatically calls str() with that object.
I will keep printing tags in this tutorial for clarity.


You can put a content into tags.
>>> print div('content')
<div>
  content
</div>


Parantheses can be omitted if the tag has no content.
>>> print div
<div></div>


Some tags are self closing.
>>> print hr
<hr/>


You can set attributes of the tag.

>>> print div(lang='tr', id='content', class_="bar", data_value="foo")
<div class="bar" data-value="foo" id="content" lang="tr"></div>


You can set contents of the tag.

>>> print div('content')
<div>
  content
</div>


Or both:

>>> print div(lang='tr')('content')
<div lang="tr">
  content
</div>


Content can be anything which can be converted to string.

If content is a callable, it will be called with a one argument
    that is the context you pass to render() as keyword arguments.

>>> greet = lambda ctx: 'Hello %s' % ctx.get('user', 'guest')
>>> greeting = div(greet)
>>> print greeting
<div>
  Hello guest
</div>
>>> print greeting.render(user='Cenk')
<div>
  Hello Cenk
</div>


You can give list of items as content.

>>> print div(nav(), greet, hr)
<div>
  <nav></nav>
  Hello guest
  <hr/>
</div>


You can give give a callable returning a list as content.

>>> items = lambda ctx: [li('a'), li('b')]
>>> print ul(items)
<ul>
  <li>
    a
  </li>
  <li>
    b
  </li>
</ul>


You can give give a generator as content.

>>> def items(ctx):
...    for i in range(3):
...        yield li(i)
>>> print ul(items)
<ul>
  <li>
    0
  </li>
  <li>
    1
  </li>
  <li>
    2
  </li>
</ul>


You can nest tags.

>>> print div(div(p('a paragraph')))
<div>
  <div>
    <p>
      a paragraph
    </p>
  </div>
</div>


Some tags have sensible defaults.

>>> print form()
<form method="POST"></form>

>>> print html()
<!DOCTYPE html>
<html></html>


Full example:

>>> print html(
...     head(
...         title('Awesome website'),
...         script(src="http://path.to/script.js")
...     ),
...     body(
...         header(
...             img(src='/path/to/logo.png'),
...         ),
...         div(
...             'Content here'
...         ),
...         footer(
...             hr,
...             'Copyright 2012'
...         )
...     )
... )
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
    </header>
    <div>
      Content here
    </div>
    <footer>
      <hr/>
      Copyright 2012
    </footer>
  </body>
</html>

"""

from copy import deepcopy
from cStringIO import StringIO
# Python-based StringIO is needed if we want to work with unicode strings.
# cStringIO only works with byte strings.
from StringIO import StringIO as StringIOUnicode
from types import GeneratorType

__version__ = '0.5.0'

INDENT_SIZE = 2


def escape(text, quote=False):
    for k, v in ('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;'):
        text = text.replace(k, v)

    if quote:
        for k, v in ('"', '&quot;'), ("'", '&#x27;'):
            text = text.replace(k, v)

    return text


class _TagMeta(type):
    """Type of the Tag. (type(Tag) == TagMeta)
    """
    def __str__(cls):
        """Renders as empty tag."""
        if cls.self_closing:
            return '<%s/>' % cls.__name__
        else:
            return '<%s></%s>' % (cls.__name__, cls.__name__)

    def __repr__(cls):
        return cls.__name__


class Tag(object):

    __metaclass__ = _TagMeta

    safe = False  # do not escape while rendering
    self_closing = False
    whitespace_sensitive = False
    default_attributes = {}
    doctype = None

    def __init__(self, *children, **attributes):
        _safe = attributes.pop('_safe', None)
        if _safe is not None:
            self.safe = _safe

        # Only children or attributes may be set at a time.
        assert ((bool(children) ^ bool(attributes))
                or (not children and not attributes))

        if self.self_closing and children:
            raise Exception("Self closing tag can't have children")

        self.children = children

        self.attributes = self.default_attributes.copy()
        self.attributes.update(attributes)

    def __call__(self, *children, **options):
        if self.self_closing:
            raise Exception("Self closing tag can't have children")

        _safe = options.pop('_safe', None)
        if _safe is not None:
            self.safe = _safe

        self.children = children
        return self

    def __repr__(self):
        if self.attributes and not self.children:
            return "%s(%s)" % (self.name, self._repr_attributes())
        elif self.children and not self.attributes:
            return "%s(%s)" % (self.name, self._repr_children())
        elif self.attributes and self.children:
            return "%s(%s)(%s)" % (self.name,
                                   self._repr_attributes(),
                                   self._repr_children())
        else:
            return "%s()" % self.name

    def _repr_attributes(self):
        return ', '.join("%s=%r" % (key, value) for key, value in self.attributes.iteritems())

    def _repr_children(self):
        return ', '.join(repr(child) for child in self.children)

    def __str__(self):
        return self.render()

    def __unicode__(self):
        return self.render(_out=StringIOUnicode(u''))

    @property
    def name(self):
        return self.__class__.__name__

    def copy(self):
        return deepcopy(self)

    def render(self, _out=None, _indent=0, **context):
        if _out is None:
            _out = StringIO()

        # Write doctype
        if self.doctype:
            _out.write(' ' * _indent)
            _out.write(self.doctype)
            _out.write('\n')

        # Indent opening tag
        _out.write(' ' * _indent)

        # Open tag
        _out.write('<%s' % self.name)

        self._write_attributes(_out, context)

        if self.self_closing:
            _out.write('/>')
        else:
            # Close opening tag
            _out.write('>')

            if self.children:
                # Newline after opening tag
                if not self.whitespace_sensitive:
                    _out.write('\n')

                # Write content
                self._write_list(self.children, _out, context, _indent + 2)

                if not self.whitespace_sensitive:
                    # Newline after content
                    _out.write('\n')
                    # Indent closing tag
                    _out.write(' ' * _indent)

            # Write closing tag
            _out.write('</%s>' % self.name)

        return _out.getvalue()

    def _write_list(self, l, out, context, indent=0):
        for child in l:
            self._write_item(child, out, context, indent)

            # Write newline between items
            if not self.whitespace_sensitive:
                out.write('\n')
        else:
            # Remove the last newline
            if not self.whitespace_sensitive:
                out.seek(-1, 1)
                out.truncate()

    def _write_item(self, item, out, context, indent):
        if isinstance(item, Tag):
            item.render(out, indent, **context)
        elif isinstance(item, _TagMeta):
            self._write_as_string(item, out, indent, escape_=False)
        elif callable(item):
            rv = item(context)
            self._write_item(rv, out, context, indent)
        elif isinstance(item, (GeneratorType, list, tuple)):
            self._write_list(item, out, context, indent)
        else:
            self._write_as_string(item, out, indent)

    def _write_as_string(self, s, out, indent, escape_=True):
        if isinstance(s, unicode) and not isinstance(out, StringIOUnicode):
            s = s.encode('utf-8')
        elif s is None:
            s = ''
        elif not isinstance(s, basestring):
            s = str(s)

        if escape_:
            if not self.safe:
                s = escape(s)

        # Write content
        if not self.whitespace_sensitive:
            lines = s.splitlines(True)
            for line in lines:
                out.write(' ' * indent)
                out.write(line)
        else:
            out.write(s)

    def _write_attributes(self, out, context):
        for key, value in sorted(self.attributes.items()):
            # Some attribute names such as "class" conflict
            # with reserved keywords in Python. These must
            # be postfixed with underscore by user.
            if key.endswith('_'):
                key = key.rstrip('_')

            # Enabling data attributes
            if key.startswith('data_'):
                key = key.replace('_', '-')

            if callable(value):
                value = value(context)

            if isinstance(value, unicode) and not isinstance(out, StringIOUnicode):
                value = value.encode('utf-8')

            if not isinstance(value, basestring):
                value = str(value)

            value = escape(value, quote=True)

            out.write(' %s="%s"' % (key, value))

    def __setitem__(self, block_name, *children):
        """Fill all the Blocks with same block_name
        in this tag recursively.
        """
        blocks = self._find_blocks(block_name)
        for b in blocks:
            b(*children)

    def _find_blocks(self, block_name):
        blocks = []
        for i, c in enumerate(self.children):
            if isinstance(c, Block) and c.block_name == block_name:
                blocks.append(c)
            elif isinstance(c, Tag):
                blocks += c._find_blocks(block_name)
        return blocks


class Block(Tag):
    """List of renderable items."""

    def __init__(self, name):
        self.block_name = name
        self.children = ()

    def __repr__(self):
        if not self.children:
            return 'Block(%r)' % self.block_name
        else:
            return 'Block(%r)(%s)' % (self.block_name, self._repr_children())

    def render(self, _out=None, _indent=0, **context):
        if _out is None:
            _out = StringIO()

        self._write_list(self.children, _out, context, _indent)
        return _out.getvalue()


class Safe(Block):
    """Helper for wrapping content that do not need escaping."""

    safe = True

    def __init__(self, *children, **options):
        super(Safe, self).__init__(None)
        super(Safe, self).__call__(*children, **options)


def Var(var, default=None):
    """Helper function for printing a variable from context."""
    return lambda ctx: ctx.get(var, default)


# These tags below are declared explicitly one by one to allow code
# completion tools to analyze the code staticly.
class head(Tag): pass
class body(Tag): pass
class title(Tag): pass
class div(Tag): pass
class p(Tag): pass
class h1(Tag): pass
class h2(Tag): pass
class h3(Tag): pass
class h4(Tag): pass
class h5(Tag): pass
class h6(Tag): pass
class u(Tag): pass
class b(Tag): pass
class i(Tag): pass
class s(Tag): pass
class a(Tag): pass
class em(Tag): pass
class strong(Tag): pass
class span(Tag): pass
class font(Tag): pass
class del_(Tag): pass
class ins(Tag): pass
class ul(Tag): pass
class ol(Tag): pass
class li(Tag): pass
class dd(Tag): pass
class dt(Tag): pass
class dl(Tag): pass
class article(Tag): pass
class section(Tag): pass
class nav(Tag): pass
class aside(Tag): pass
class header(Tag): pass
class footer(Tag): pass
class audio(Tag): pass
class video(Tag): pass
class object_(Tag): pass
class embed(Tag): pass
class param(Tag): pass
class fieldset(Tag): pass
class legend(Tag): pass
class button(Tag): pass
class textarea(Tag): pass
class label(Tag): pass
class select(Tag): pass
class option(Tag): pass
class table(Tag): pass
class thead(Tag): pass
class tbody(Tag): pass
class tr(Tag): pass
class th(Tag): pass
class td(Tag): pass
class caption(Tag): pass
class blockquote(Tag): pass
class cite(Tag): pass
class q(Tag): pass
class abbr(Tag): pass
class acronym(Tag): pass
class address(Tag): pass


class SelfClosingTag(Tag):
    self_closing = True

class meta(SelfClosingTag): pass
class link(SelfClosingTag): pass
class br(SelfClosingTag): pass
class hr(SelfClosingTag): pass
class input(SelfClosingTag): pass
class img(SelfClosingTag): pass


class WhitespaceSensitiveTag(Tag):
    whitespace_sensitive = True

class code(WhitespaceSensitiveTag): pass
class samp(WhitespaceSensitiveTag): pass
class pre(WhitespaceSensitiveTag): pass
class var(WhitespaceSensitiveTag): pass
class kbd(WhitespaceSensitiveTag): pass
class dfn(WhitespaceSensitiveTag): pass


class html(Tag):
    doctype = '<!DOCTYPE html>'


class script(Tag):
    safe = True
    default_attributes = {'type': 'text/javascript'}


class style(Tag):
    default_attributes = {'type': 'text/css'}


class form(Tag):
    default_attributes = {'method': 'POST'}


if __name__ == "__main__":
    import doctest
    doctest.testmod()
