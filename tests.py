# -*- coding: utf8 -*-

import unittest
from phtml import *


class TestPhtml(unittest.TestCase):

    def test_render(self):
        self.assertEqual(render_tag('a'), '<a/>')
        self.assertEqual(render_tag('a', '1'), '<a>1</a>')
        self.assertEqual(render_tag('a', None, {'b': 2}), '<a b="2"/>')
        self.assertEqual(render_tag('a', '', {'b': 2}), '<a b="2"></a>')
        self.assertEqual(render_tag('a', 'c', {'b': 2}), '<a b="2">c</a>')

    def test_tag(self):
        self.assertEqual(str(hr), '<hr/>')
        self.assertEqual(str(html), '<html></html>')
        self.assertEqual(str(html()), '<html></html>')
        self.assertEqual(str(html('')), '<html></html>')
        self.assertEqual(str(html('content')), '<html>content</html>')
        self.assertEqual(str(html(6)), '<html>6</html>')
        self.assertEqual(str(html(lang='tr')), '<html lang="tr"/>')

        self.assertEqual(str(html()()), '<html></html>')
        self.assertEqual(str(html()('')), '<html></html>')
        self.assertEqual(str(html()('content')), '<html>content</html>')

        self.assertEqual(str(html(lang='tr')()), '<html lang="tr"></html>')
        self.assertEqual(str(html(lang='tr')('')), '<html lang="tr"></html>')
        self.assertEqual(str(html(lang='tr')('content')), '<html lang="tr">content</html>')

    def test_block_fill_str(self):
        h = html(
            head(title('phtml is awesome')),
            body(
                p('a paragraph'),
                Block('main')
            )
        )
        h['main'] = 'yess'
        self.assertEqual(str(h), '<html><head><title>phtml is awesome'\
                                 '</title></head><body><p>a paragraph</p>'\
                                 'yess</body></html>')

    def test_block_fill_tag(self):
        h = html(
            head(title('phtml is awesome')),
            body(
                p('a paragraph'),
                Block('main')
            )
        )
        h['main'] = hr
        self.assertEqual(str(h), '<html><head><title>phtml is awesome'\
                                 '</title></head><body><p>a paragraph</p>'\
                                 '<hr/></body></html>')

    def test_block_fill_lazy(self):
        class V(object):
            def __str__(self):
                return 'asdf'
        v = V()
        h = html(Block('b'))
        h['b'] = v
        self.assertEqual(str(h), '<html>asdf</html>')

    def test_block_placeholder(self):
        h = html(Block('b')('xxx'))
        self.assertEqual(str(h), '<html>xxx</html>')
        h['b'] = 'yyy'
        self.assertEqual(str(h), '<html>yyy</html>')
        h['b'] = 'zzz'
        self.assertEqual(str(h), '<html>zzz</html>')

    def test_find_blocks(self):
        a1 = Block('a')
        a2 = Block('a')
        b = Block('b')
        h = html(
                head(
                    title(Block('title'))
                ),
                body(a1, a2, b)
            )
        _a = h._find_blocks('a')
        self.assertEqual(len(_a), 2)
        self.assertIs(_a[0], a1)
        self.assertIs(_a[1], a2)
        _b = h._find_blocks('b')
        self.assertEqual(_b[0], b)

    def test_reserved_keywords(self):
        t = div(class_='container')
        self.assertEqual(str(t), '<div class="container"/>')

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

    def test_callable(self):
        tag = html(
            body(
                'a',
                Block('b')('placeholder'),
                'c'
            )
        )
        tag['b'] = lambda ctx:'content'
        rendered = str(tag)
        self.assertEqual(rendered, '<html><body>acontentc</body></html>')

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
        expected = u'<title a="Türkçe"/>'
        self.assertEqual(rendered.decode('utf-8'), expected)


if __name__ == "__main__":
    unittest.main()
