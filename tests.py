import unittest
from pyhtml import *


class TestPytml(unittest.TestCase):

    def test_render(self):
        self.assertEqual(render_tag('a'), '<a/>')
        self.assertEqual(render_tag('a', '1'), '<a>1</a>')
        self.assertEqual(render_tag('a', None, {'b': 2}), '<a b="2"/>')
        self.assertEqual(render_tag('a', '', {'b': 2}), '<a b="2"></a>')
        self.assertEqual(render_tag('a', 'c', {'b': 2}), '<a b="2">c</a>')

    def test_tag(self):
        self.assertEqual(str(html), '<html/>')
        self.assertEqual(str(html()), '<html></html>')
        self.assertEqual(str(html('')), '<html></html>')
        self.assertEqual(str(html('content')), '<html>content</html>')
        self.assertEqual(str(html(lang='tr')), '<html lang="tr"/>')

        self.assertEqual(str(html()()), '<html></html>')
        self.assertEqual(str(html()('')), '<html></html>')
        self.assertEqual(str(html()('content')), '<html>content</html>')

        self.assertEqual(str(html(lang='tr')()), '<html lang="tr"></html>')
        self.assertEqual(str(html(lang='tr')('')), '<html lang="tr"></html>')
        self.assertEqual(str(html(lang='tr')('content')), '<html lang="tr">content</html>')

    def test_block_fill_str(self):
        h = html(
            head(title('pyhtml is awesome')),
            body(
                p('a paragraph'),
                Block('main')
            )
        ).fill_blocks(main='yess')
        self.assertEqual(str(h), '<html><head><title>pyhtml is awesome'\
                                 '</title></head><body><p>a paragraph</p>'\
                                 'yess</body></html>')

    def test_block_fill_tag(self):
        h = html(
            head(title('pyhtml is awesome')),
            body(
                p('a paragraph'),
                Block('main')
            )
        ).fill_blocks(main=hr)
        self.assertEqual(str(h), '<html><head><title>pyhtml is awesome'\
                                 '</title></head><body><p>a paragraph</p>'\
                                 '<hr/></body></html>')

    def test_block_fill_lazy(self):
        class V(object):
            def __str__(self):
                return 'asdf'
        v = V()
        h = html(Block('b'))
        h.fill_blocks(b=v)
        self.assertEqual(str(h), '<html>asdf</html>')

    def test_block_placeholder(self):
        h = html(Block('b')('xxx'))
        self.assertEqual(str(h), '<html>xxx</html>')
        h.fill_blocks(b='yyy')
        self.assertEqual(str(h), '<html>yyy</html>')
        h.fill_blocks(b='zzz')
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
        print _a
        self.assertEqual(len(_a), 2)
        self.assertIs(_a[0], a1)
        self.assertIs(_a[1], a2)
        _b = h._find_blocks('b')
        self.assertEqual(_b[0], b)

if __name__ == "__main__":
    unittest.main()
