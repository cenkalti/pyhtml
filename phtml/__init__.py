import sys
from copy import deepcopy
from cStringIO import StringIO


# Filled by export decorator
__all__ = []


def export(obj):
    __all__.append(obj.__name__)
    return obj


INDENT_SIZE = 2


def escape(text, quote=True):
    for k, v in ('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;'):
        text = text.replace(k, v)

    if quote:
        for k, v in ('"', '&quot;'), ("'", '&#x27;'):
            text = text.replace(k, v)

    return text


@export
class Block(object):
    """List of renderable items."""

    whitespace_sensitive = False
    safe = False

    def __init__(self, name):
        self.name = name
        self.children = ()

    def __repr__(self):
        return 'Block(%r)' % self.name

    def __call__(self, *children):
        self.children = children
        return self

    def __str__(self, out=None, indent=0, **context):
        if out is None:
            out = StringIO()

        is_last_item = lambda: i == len(self.children) - 1

        for i, child in enumerate(self.children):
            self._write_single(out, child, indent, context)

            if not self.whitespace_sensitive and not is_last_item():
                out.write('\n')

        return out.getvalue()

    def _write_single(self, out, child, indent, context):
        if isinstance(child, Block):
            child.__str__(out, indent, **context)
        else:
            if callable(child) and not isinstance(child, TagMeta):
                s = child(context)
            else:
                s = child

            # Convert to string
            if isinstance(s, unicode):
                s = s.encode('utf-8')
            else:
                s = str(s)

            if not isinstance(child, TagMeta):
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

    def copy(self):
        return deepcopy(self)

    def render(self, **context):
        return self.__str__(**context)

    def __setitem__(self, block_name, *children):
        """Fill all the Blocks with same block_name
        in this tag recursively.
        """
        blocks = self._find_blocks(block_name)
        for b in blocks:
            b(*children)

    def _find_blocks(self, name):
        blocks = []
        for i, c in enumerate(self.children):
            if isinstance(c, Block) and c.name == name:
                blocks.append(c)
            elif isinstance(c, Tag):
                blocks += c._find_blocks(name)
        return blocks


class TagMeta(type):
    """Type of the Tag. (type(Tag) == TagMeta)
    """
    def __str__(cls):
        """Renders as empty tag."""
        return '<%s></%s>' % (cls.__name__, cls.__name__)


@export
class Tag(Block):

    __metaclass__ = TagMeta

    doctype = None

    def __init__(self, *children, **attributes):
        # Only children or attributes may be set at a time.
        assert ((bool(children) ^ bool(attributes))
                or (not children and not attributes))

        self.children = children
        self.attributes = attributes

    def __call__(self, *children):
        """Set children of this tag."""
        self.children = children
        return self

    def __repr__(self):
        return '%s()' % self.name

    def __str__(self, out=None, indent=0, **context):
        if out is None:
            out = StringIO()

        # Write doctype
        if self.doctype:
            out.write(' ' * indent)
            out.write(self.doctype)
            out.write('\n')

        # Indent opening tag
        out.write(' ' * indent)

        # Open tag
        out.write('<%s' % self.name)

        self._write_attributes(out)

        # Close opening tag
        out.write('>')

        if self.children:
            # Newline after opening tag
            if not self.whitespace_sensitive:
                out.write('\n')

            # Write content
            super(Tag, self).__str__(out, indent + INDENT_SIZE, **context)

            if not self.whitespace_sensitive:
                # Newline after content
                out.write('\n')
                # Indent closing tag
                out.write(' ' * indent)

        # Write closing tag
        out.write('</%s>' % self.name)

        return out.getvalue()

    def _write_attributes(self, out):
        for k, v in self.attributes.items():
            # Some attribute names such as "class" conflict
            # with reserved keywords in Python. These must
            # be postfixed with underscore by user.
            if k.endswith('_'):
                k = k.rstrip('_')

            if isinstance(v, unicode):
                v = v.encode('utf-8')

            out.write(' %s="%s"' % (k, v))

    @property
    def name(self):
        return self.__class__.__name__


class SelfClosingTagMeta(TagMeta):
    def __str__(cls):
        """Renders as self closing tag."""
        return '<%s/>' % cls.__name__


class SelfClosingTag(Tag):

    __metaclass__ = SelfClosingTagMeta

    def __init__(self, **attributes):
        super(SelfClosingTag, self).__init__(**attributes)

    def __call__(self, *args, **kwargs):
        raise Exception("Self closing tag can't have children")

    def __str__(self, out=None, indent=0, **context):
        if out is None:
            out = StringIO()

        # Indent
        out.write(' ' * indent)

        # Open tag
        out.write('<%s' % self.name)

        self._write_attributes(out)

        # Close tag
        out.write('/>')

        return out.getvalue()


class WhitespaceSensitiveTag(Tag):
    whitespace_sensitive = True


tags = (
    'head body title ' +  # Main elements
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


@export
class html(Tag):
    doctype = '<!DOCTYPE html>'
