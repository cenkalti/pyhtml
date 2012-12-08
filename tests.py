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

if __name__ == "__main__":
    unittest.main()
