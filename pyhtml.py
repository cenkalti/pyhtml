import sys
import operator
from cStringIO import StringIO

# Filled by export decorator
__all__ = []


def export(obj):
    __all__.append(obj.__name__)
    return obj


@export
def render_tag(name, content=None, attributes=None):
    s = StringIO()
    s.write('<%s' % name)
    if attributes:
        for k, v in attributes.items():
            # Some attribute names such as "class" conflict
            # with reserved keywords in Python. These must
            # be postfixed with underscore by user.
            if k.endswith('_'):
                k = k.rstrip('_')
            s.write(' %s="%s"' % (k, v))
    # If we don't want self closing tag,
    # we must send content as empty string.
    if content or content == '':
        s.write('>')
        s.write(content)
        s.write('</%s>' % name)
    else:
        s.write('/>')
    return s.getvalue()


class TagMeta(type):
    """Type of the Tag. (type(Tag) == TagMeta)
    """
    def __str__(cls):
        """Renders as self closing tag.
        """
        return render_tag(cls.__name__)


@export
class Tag(object):

    __metaclass__ = TagMeta

    def __init__(self, *content, **attributes):
        self.content = None
        self.attributes = None

        # Only content or attributes may be set at a time.
        if content:
            assert not attributes
            self.content = content
        if attributes:
            assert not content
            self.attributes = attributes

        # If __init__ is called with empty arguments,
        # We must set the self.content to empty strint
        # so it won't be rendered as self closing tag.
        if not content and not attributes:
            self.content = ''
    
    def __call__(self, *content):
        """Set content of this tag."""
        if content == tuple():
            self.content = ''
        else:
            self.content = content
        return self

    def __repr__(self):
        return '%r()' % self.__class__.__name__

    def __str__(self, content_only=False):
        """Render this tag with contents.

        If content_only is True, enclosing tags are not visible.
        This is required for rendering Blocks.
        """
        if isinstance(self.content, basestring):
            rendered_content = self.content
        elif isinstance(self.content, tuple) and self.content:
            rendered_content = reduce(operator.add, map(str, self.content))
        else:
            rendered_content = None

        if content_only:
            return rendered_content or ''
        else:
            name = self.__class__.__name__
            return render_tag(name, rendered_content, self.attributes)

    def fill_blocks(self, **vars):
        """Fill the Blocks in this tag recursively.
        """
        blocks = self._find_blocks(vars.keys())
        for b in blocks:
            new_content = vars[b.name]
            b(new_content)
        return self

    def _find_blocks(self, names):
        blocks = []
        for i, c in enumerate(self.content):
            if isinstance(c, Block) and c.name in names:
                blocks.append(c)
            elif isinstance(c, Tag):
                blocks += c._find_blocks(names)
        return blocks


def create_tag(name):
    return type(name, (Tag, object), dict(Tag.__dict__))


@export
class Block(Tag):
    def __init__(self, name):
        self.name = name
        Tag.__init__(self)
    def __repr__(self):
        return 'Block(%r)' % self.name
    def __str__(self):
        return Tag.__str__(self, content_only=True)


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
for tag_name in tags.split():
    tag = create_tag(tag_name)
    setattr(this_module, tag_name, tag)
    export(tag)
