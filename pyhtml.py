import sys
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


class TagMeta(type):
    def __str__(cls):
        return render_tag(cls.__name__)

        
class Tag(object):

    __metaclass__ = TagMeta

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


def create_tag(name):
    return type(name, (Tag, object), dict(Tag.__dict__))


# Create Tags for following names
# 
__all__ = []
tags = (
    'html head body title ' +  # Main elements
    'div p ' +  # Blocks
    'h1 h2 h3 h4 h5 h6 ' +  # Headers
    'u b i s a em strong span font ' +  # Inline markup
    'del ins ' +  # Annotation
    'ul ol li dd dt dl ' +  # Lists
    'article section nav aside ' +  # HTML5
    'audio video object_ embed param ' +  # Media
    'fieldset legend button textarea label select option ' +  # Forms
    'table thead tbody tr th td caption ' +  # Tables
    'blockquote cite q abbr acronym address ' +  # Citation, quotes etc
    'code samp pre var kbd dfn ' +  # Code
    'meta link br hr input' +  # Empty tags
'')
this_module = sys.modules[__name__]
for tag in tags.split():
    __all__.append(tag)
    setattr(this_module, tag, create_tag(tag))


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
