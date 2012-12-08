import sys
import operator
from cStringIO import StringIO

__all__ = ['render_tag', 'Block']


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
            self.content = list(content)
        if attributes:
            assert not content
            self.attributes = attributes

        if not content and not attributes:
            self.content = ''
    
    def __call__(self, *content):
        if content == tuple():
            self.content = ''
        else:
            self.content = list(content)
        return self

    def __str__(self):
        if isinstance(self.content, basestring):
            rendered_content = self.content
        elif isinstance(self.content, list) and self.content:
            rendered_content = reduce(operator.add, map(str, self.content))
        else:
            rendered_content = None
        name = self.__class__.__name__
        return render_tag(name, rendered_content, self.attributes)

    def fill_blocks(self, **vars):
        assert self.content and isinstance(self.content, list)
        for i, c in enumerate(self.content):
            if isinstance(c, Tag):
                c.fill_blocks(**vars)
            elif isinstance(c, Block):
                if c.name in vars:
                    self.content[i] = vars[c.name]
        return self


def create_tag(name):
    return type(name, (Tag, object), dict(Tag.__dict__))


class Block(object):
    def __init__(self, name):
        self.name = name


# Create Tags for following names
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
