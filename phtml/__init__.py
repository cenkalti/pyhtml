import sys
import copy
import operator
from functools import partial
from cStringIO import StringIO

try:
    # Not available before Python 3.2.
    from html import escape
except ImportError:
    def escape(text, quote=True):
        for k, v in ('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;'):
            text = text.replace(k, v)

        if quote:
            for k, v in ('"', '&quot;'), ("'", '&#x27;'):
                text = text.replace(k, v)

        return text


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

            if isinstance(v, unicode):
                v = v.encode('utf-8')
            s.write(' %s="%s"' % (k, v))
    # If we don't want self closing tag,
    # we must send content as empty string.
    if content or content == '':
        s.write('>')
        if isinstance(content, unicode):
            content = content.encode('utf-8')
        s.write(content)
        s.write('</%s>' % name)
    else:
        s.write('/>')
    return s.getvalue()


class TagMeta(type):
    """Type of the Tag. (type(Tag) == TagMeta)
    """
    def __str__(cls):
        """Renders as empty tag.
        """
        return render_tag(cls.__name__, '')


@export
class Tag(object):

    __metaclass__ = TagMeta

    def __init__(self, *content, **attributes):
        self.content = None
        self.attributes = {}

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

    def __str__(self, content_only=False, **context):
        """Render this tag with it's contents.

        If content_only is True, enclosing tags are not visible.
        This is required for rendering Blocks.

        """
        if self.content == '':
            rendered_content = ''
        elif isinstance(self.content, tuple) and self.content:
            f_render = partial(Tag._render_single, context=context)
            rendered_content = map(f_render, self.content)
            rendered_content = reduce(operator.add, rendered_content)
        else:
            rendered_content = None

        if content_only:
            return rendered_content or ''
        else:
            name = self.__class__.__name__
            return render_tag(name, rendered_content, self.attributes)

    def copy(self):
        return copy.deepcopy(self)

    @staticmethod
    def _render_single(x, context=None):
        if context is None:
            context = {}

        if isinstance(x, basestring):
            return escape(x)
        elif isinstance(x, Tag):
            return x.__str__(**context)
        elif isinstance(x, TagMeta):
            return str(x)
        elif callable(x):
            context = context
            return escape(str(x(context)))
        else:
            return escape(str(x))

    def render(self, **context):
        return self.__str__(**context)

    def __setitem__(self, block_name, *content):
        """Fill all the Blocks with same block_name
        in this tag recursively.
        """
        blocks = self._find_blocks(block_name)
        for b in blocks:
            b(*content)

    def _find_blocks(self, name):
        blocks = []
        for i, c in enumerate(self.content):
            if isinstance(c, Block) and c.name == name:
                blocks.append(c)
            elif isinstance(c, Tag):
                blocks += c._find_blocks(name)
        return blocks


class SelfClosingTagMeta(TagMeta):
    def __str__(cls):
        """Renders as self closing tag.
        """
        return render_tag(cls.__name__)


class SelfClosingTag(Tag):

    __metaclass__ = SelfClosingTagMeta

    def __init__(self, **attributes):
        self.content = None
        self.attributes = attributes

    def __call__(self, *args, **kwargs):
        raise Exception("Self closing tag can't have content")


class WhitespaceSensitiveTag(Tag):
    pass


@export
class Block(Tag):
    def __init__(self, name):
        """name must be valid Python identifier."""
        self.name = name
        Tag.__init__(self)
    def __repr__(self):
        return 'Block(%r)' % self.name
    def __str__(self, **context):
        return Tag.__str__(self, content_only=True, **context)


tags = (
    'html head body title ' +  # Main elements
    'div p ' +  # Blocks
    'h1 h2 h3 h4 h5 h6 ' +  # Headers
    'u b i s a em strong span font ' +  # Inline markup
    'del ins ' +  # Annotation
    'ul ol li dd dt dl ' +  # Lists
    'article section nav aside header footer ' +  # HTML5
    'audio video object_ embed param ' +  # Media
    'fieldset legend button textarea label select option ' +  # Forms
    'table thead tbody tr th td caption ' +  # Tables
    'blockquote cite q abbr acronym address ' +  # Citation, quotes etc
'').split()

self_closing_tags = 'meta link br hr input'.split()

whitespace_sensitive_tags = 'code samp pre var kbd dfn'.split()

def register(tags, cls):
    """Create tags and add to this module's namespace."""
    this_module = sys.modules[__name__]
    for tag_name in tags:
        tag = create_tag(tag_name, cls)
        setattr(this_module, tag_name, tag)
        export(tag)

def create_tag(name, cls):
    return type(name, (cls, object), dict(cls.__dict__))

register(tags, Tag)
register(self_closing_tags, SelfClosingTag)
register(whitespace_sensitive_tags, WhitespaceSensitiveTag)
