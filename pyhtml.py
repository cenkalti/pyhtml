import unittest
import operator
from cStringIO import StringIO


def render_tag(name, content=None, attributes=None):
    s = StringIO()
    s.write('<%s' % name)
    if attributes:
        for attr in attributes.items():
            s.write(' %s="%s"' % attr)
    if content or content == '':
        s.write('>')
        s.write(content)
        s.write('</%s>' % name)
    else:
        s.write('/>')
    return s.getvalue()

        
class Tag(object):

    def __init__(self, *content, **attributes):
        self.content = None
        self.attributes = None

        if content:
            assert not attributes
            self.content = content
        if attributes:
            assert not content
            self.attributes = attributes

        if not content and not attributes:
            self.content = ''
    
    def __call__(self, *content):
        if content == tuple():
            self.content = ''
        else:
            self.content = content
        return self

    def __str__(self):
        if isinstance(self.content, basestring):
            rendered_content = self.content
        elif isinstance(self.content, tuple) and self.content:
            rendered_content = reduce(operator.add, map(str, self.content))
        else:
            rendered_content = None
        name = self.__class__.__name__
        return render_tag(name, rendered_content, self.attributes) 


class TagType(type):
    def __str__(self):
        return render_tag(self.__name__, None, {})


def create_tag(name):
    return TagType(name, (object, ), dict(Tag.__dict__))


html = create_tag('html')
head = create_tag('head')
title = create_tag('title')
body = create_tag('body')
p = create_tag('p')
hr = create_tag('hr')


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


if __name__ == "__main__":
    unittest.main()
