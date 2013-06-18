"""\
    This benchmark compares some python templating engines with Jinja 2 so
    that we get a picture of how fast Jinja 2 is for a semi real world
    template.  If a template engine is not installed the test is skipped.\
"""
import sys
from timeit import Timer
from jinja2 import Environment as JinjaEnvironment

context = {
    'page_title': 'mitsuhiko\'s benchmark',
    'table': [dict(a=1,b=2,c=3,d=4,e=5,f=6,g=7,h=8,i=9,j=10) for x in range(100)]
}

jinja_template = JinjaEnvironment(
    line_statement_prefix='%',
    variable_start_string="${",
    variable_end_string="}"
).from_string("""\
<!doctype html>
<html>
  <head>
    <title>${page_title|e}</title>
  </head>
  <body>
    <div class="header">
      <h1>${page_title|e}</h1>
    </div>
    <ul class="navigation">
    % for href, caption in [
        ('index.html', 'Index'),
        ('downloads.html', 'Downloads'),
        ('products.html', 'Products')
      ]
      <li><a href="${href|e}">${caption|e}</a></li>
    % endfor
    </ul>
    <div class="table">
      <table>
      % for row in table
        <tr>
        % for cell in row
          <td>${cell}</td>
        % endfor
        </tr>
      % endfor
      </table>
    </div>
  </body>
</html>\
""")

def test_jinja():
    jinja_template.render(context)


def f_navigation(ctx):
    items = []
    for href, caption in [
            ('index.html', 'Index'),
            ('downloads.html', 'Downloads'),
            ('products.html', 'Products')]:
        item = li(a(href=href)(caption))
        items.append(item)
    return Block('_')(*items)

def f_table(ctx):
    return Block('_')(*f_rows(ctx['table']))

def f_rows(rows):
    for row in rows:
        yield tr(*f_cells(row))

def f_cells(row):
    for cell in row:
        yield td(cell)

from pyhtml import *
pyhtml_template = html(
    head(
        title(Block('page_title'))
    ),
    body(
        div(class_="header")(
            h1(Block('page_title'))
        ),
        ul(class_="navigation")(f_navigation),
        div(class_="table")(
            table(f_table)
        )
    )
)

def test_pyhtml():
    pyhtml_template.render(**context)


sys.stdout.write('\r' + '\n'.join((
    '=' * 80,
    'Template Engine BigTable Benchmark'.center(80),
    '=' * 80,
    __doc__,
    '-' * 80
)) + '\n')


for test in 'jinja', 'pyhtml':
    if locals()['test_' + test] is None:
        sys.stdout.write('    %-20s*not installed*\n' % test)
        continue
    t = Timer(setup='from __main__ import test_%s as bench' % test,
              stmt='bench()')
    sys.stdout.write(' >> %-20s<running>' % test)
    sys.stdout.flush()
    sys.stdout.write('\r    %-20s%.4f seconds\n' % (test, t.timeit(number=50) / 50))
sys.stdout.write('-' * 80 + '\n')
sys.stdout.write('''\
    WARNING: The results of this benchmark are useless to compare the
    performance of template engines and should not be taken seriously in any
    way.  It's testing the performance of simple loops and has no real-world
    usefulnes.  It only used to check if changes on the Jinja code affect
    performance in a good or bad way and how it roughly compares to others.
''' + '=' * 80 + '\n')
