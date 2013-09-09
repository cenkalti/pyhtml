# -*- coding: utf8 -*-
import unittest
from pyhtml import *


class TestPyHTML(unittest.TestCase):

    assertEqualWS = unittest.TestCase.assertEqual

    def assertEqual(self, first, second, msg=None):
        """Overriden for ignoring whitespace."""
        def remove_whitespace(s):
            if isinstance(s, basestring):
                return s.replace(' ', '').replace('\n', '')
            else:
                return s
        first = remove_whitespace(first)
        second = remove_whitespace(second)
        return super(TestPyHTML, self).assertEqual(first, second, msg)

    def test_repr_tag(self):
        self.assertEqualWS(repr(div), 'div')
        self.assertEqualWS(repr(div()), 'div()')
        self.assertEqualWS(repr(div(a=1)), 'div(a=1)')
        self.assertEqualWS(repr(div("asdf")), "div('asdf')")
        self.assertEqualWS(repr(div(a=1)("asdf")), "div(a=1)('asdf')")

    def test_repr_block(self):
        self.assertEqualWS(repr(Block('x')), "Block('x')")
        self.assertEqualWS(repr(Block('x')('asdf')), "Block('x')('asdf')")
        self.assertEqualWS(repr(Block('x')(1, 2)), "Block('x')(1, 2)")

    def test_render_tag(self):
        self.assertEqual(str(hr), '<hr/>')
        self.assertEqual(str(div), '<div></div>')
        self.assertEqual(str(div()), '<div></div>')
        self.assertEqual(str(div('')), '<div></div>')
        self.assertEqual(str(div('content')), '<div>content</div>')
        self.assertEqual(str(div(6)), '<div>6</div>')
        self.assertEqual(str(div(lang='tr')), '<div lang="tr"></div>')

        self.assertEqual(str(div()()), '<div></div>')
        self.assertEqual(str(div()('')), '<div></div>')
        self.assertEqual(str(div()('content')), '<div>content</div>')

        self.assertEqual(str(div(lang='tr')()), '<div lang="tr"></div>')
        self.assertEqual(str(div(lang='tr')('')), '<div lang="tr"></div>')
        self.assertEqual(str(div(lang='tr')('content')), '<div lang="tr">'
                                                         'content</div>')

    def test_render_tag_callable_str(self):
        f = lambda ctx: 'asdf'
        self.assertEqual(str(div(f)), '<div>asdf</div>')

    def test_render_tag_callable_none(self):
        n = lambda ctx: None
        self.assertEqual(str(div(n)), '<div></div>')

    def test_render_tag_callable_generator(self):
        def g(ctx):
            yield 1
            yield 2
        self.assertEqual(str(div(g)), '<div>12</div>')

    def test_render_tag_callable_list(self):
        l = lambda ctx: ['a', 'b']
        self.assertEqual(str(div(l)), '<div>ab</div>')

    def test_render_block(self):
        self.assertEqual(str(Block('b')), '')
        self.assertEqual(str(Block('b')('asdf')), 'asdf')
        self.assertEqual(str(Block('b')(div())), '<div></div>')

    def test_block_fill_str(self):
        h = div(
            head(title('pyhtml is awesome')),
            body(
                p('a paragraph'),
                Block('main')
            )
        )
        h['main'] = 'yess'
        self.assertEqual(str(h), '<div><head><title>pyhtml is awesome'
                                 '</title></head><body><p>a paragraph</p>'
                                 'yess</body></div>')

    def test_block_fill_tag(self):
        h = div(
            head(title('pyhtml is awesome')),
            body(
                p('a paragraph'),
                Block('main')
            )
        )
        h['main'] = hr
        self.assertEqual(str(h), '<div><head><title>pyhtml is awesome'
                                 '</title></head><body><p>a paragraph</p>'
                                 '<hr/></body></div>')

    def test_block_fill_callable(self):
        class V(object):
            def __str__(self):
                return 'asdf'
        v = V()
        h = div(Block('b'))
        h['b'] = v
        self.assertEqual(str(h), '<div>asdf</div>')

    def test_block_placeholder(self):
        h = div(Block('b')('xxx'))
        self.assertEqual(str(h), '<div>xxx</div>')
        h['b'] = 'yyy'
        self.assertEqual(str(h), '<div>yyy</div>')
        h['b'] = 'zzz'
        self.assertEqual(str(h), '<div>zzz</div>')

    def test_find_blocks(self):
        a1 = Block('a')
        a2 = Block('a')
        x = Block('b')
        h = html(
            head(
                title(Block('title'))
            ),
            body(a1, a2, x)
        )
        _a = h._find_blocks('a')
        self.assertEqual(len(_a), 2)
        self.assertTrue(_a[0] is a1)
        self.assertTrue(_a[1] is a2)
        _b = h._find_blocks('b')
        self.assertEqual(_b[0], x)

    def test_reserved_keywords(self):
        t = div(class_='container')
        self.assertEqual(str(t), '<div class="container"></div>')

    def test_copy(self):
        t = div(Block('a'))
        t2 = t.copy()
        t2['a'] = '1'
        self.assertEqual(str(t), '<div></div>')
        self.assertEqual(str(t2), '<div>1</div>')

    def test_escape_tag(self):
        dangerous = '<script>'
        tag = div(dangerous)
        rendered = str(tag)
        self.assertEqual(rendered, '<div>&lt;script&gt;</div>')

    def test_escape_block(self):
        dangerous = '<script>'
        tag = div(Block('b')(dangerous))
        rendered = str(tag)
        self.assertEqual(rendered, '<div>&lt;script&gt;</div>')

    def test_block_safe(self):
        x = div('<script>')
        x.safe = True
        self.assertTrue('<script>' in str(x))

    def test_safe_in_attr(self):
        x = div(_safe=True)('<script>')
        self.assertTrue('<script>' in str(x))

    def test_safe_in_content(self):
        x = div('<script>', _safe=True)
        self.assertTrue('<script>' in str(x))

    def test_safe_wrapper(self):
        x = div(Safe('<script></script>'))
        self.assertEqual('<div><script></script></div>', str(x))

    def test_callable(self):
        tag = div(
            p(
                'a',
                Block('b')('placeholder'),
                'c'
            )
        )
        tag['b'] = lambda ctx: 'content'
        rendered = str(tag)
        self.assertEqual(rendered, '<div><p>acontentc</p></div>')

    def test_context(self):
        def greet_user(ctx):
            name = ctx.get('name', 'user')
            return 'Hello %s' % name
        tag = div(
            greet_user
        )

        rendered = str(tag)
        self.assertEqual(rendered, '<div>Hello user</div>')

        rendered = tag.render(name='Cenk')
        self.assertEqual(rendered, '<div>Hello Cenk</div>')

    def test_context_in_block(self):
        def greet_user(ctx):
            name = ctx.get('name', 'user')
            return 'Hello %s' % name
        tag = div(
            Block('b')
        )
        tag['b'] = greet_user

        rendered = tag.render(name='Cenk')
        self.assertEqual(rendered, '<div>Hello Cenk</div>')

    def test_unicode_content(self):
        t = title(u'Türkçe')
        rendered = t.render()
        expected = u'<title>Türkçe</title>'
        self.assertEqual(rendered.decode('utf-8'), expected)

    def test_unicode_attr_value(self):
        t = title(a=u'Türkçe')
        rendered = t.render()
        expected = u'<title a="Türkçe"></title>'
        self.assertEqual(rendered.decode('utf-8'), expected)

    def test_unicode_conversion(self):
        # calling unicode(tag) on a tag with non-ascii content doesn't result
        # in a UnicodeDecodeError. It directly renders unicode without encoding
        # the string in the process.
        t = title(a=u'Türkçe')(u'Türkçe')
        rendered = unicode(t)
        expected = u'<title a="Türkçe">Türkçe</title>'
        self.assertEqual(rendered, expected)

    def test_self_closing_tag_init(self):
        t = hr(id=3)
        self.assertEqualWS(str(t), '<hr id="3"/>')

    def test_self_closing_tag_call(self):
        t = hr()
        self.assertRaises(Exception, t)

    def test_tag_indent(self):
        f = lambda c: 'text'
        g = lambda c: 'text with\nnewlines'
        t = html(
            head(title('title')),
            body(
                f,
                'some text',
                p('a paragraph'),
                div('div with\nsome\nnewlines'),
                'block start',
                Block('b')(
                    f,
                    'some more text'
                ),
                'block end',
                g,
                div(
                    pre('asdf\nzxcv\nqwerty')
                )
            )
        )
        self.assertEqualWS(str(t), """<!DOCTYPE html>
<html>
  <head>
    <title>
      title
    </title>
  </head>
  <body>
    text
    some text
    <p>
      a paragraph
    </p>
    <div>
      div with
      some
      newlines
    </div>
    block start
    text
    some more text
    block end
    text with
    newlines
    <div>
      <pre>asdf
zxcv
qwerty</pre>
    </div>
  </body>
</html>""")

    def test_block(self):
        f = lambda ctx: 'callable'
        x = div(
            Block('b')(
                'text',
                f,
                div(),
            )
        )
        self.assertEqualWS(str(x), """\
<div>
  text
  callable
  <div></div>
</div>""")

    def test_default_attr(self):
        f = form()
        self.assertEqual(str(f), '<form method="POST"></form>')

    def test_lazy_attr(self):
        f = lambda ctx: 'x'
        d = div(name=f)
        self.assertEqual(str(d), '<div name="x"></div>')

    def test_block_fill_multi(self):
        x = div(
            Block('b')('placeholder')
        )
        x['b'] = 'asdf', 123
        self.assertEqual(str(x), """<div>asdf123</div>""")

    def test_var(self):
        ctx = {'name': 'value'}
        x = div(Var('name'))
        rendered = x.render(**ctx)
        self.assertEqual(rendered, '<div>value</div>')

    def test_var_default(self):
        ctx = {'name': 'value'}
        x = div(Var('notexist', 'default'))
        rendered = x.render(**ctx)
        self.assertEqual(rendered, '<div>default</div>')


if __name__ == "__main__":
    unittest.main()
