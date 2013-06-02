# coding=utf-8
import os
import re
from setuptools import setup


def read(*fname):
    with open(os.path.join(os.path.dirname(__file__), *fname)) as f:
        return f.read()


def get_version():
    for line in read('pyhtml.py').splitlines():
        m = re.match(r"__version__\s*=\s'(.*)'", line)
        if m:
            return m.groups()[0].strip()
    raise Exception('Cannot find version')


setup(
    name='PyHTML',
    version=get_version(),
    author=u'Cenk Altı',
    author_email='cenkalti@gmail.com',
    keywords='html template markup',
    url='http://github.com/cenkalti/pyhtml',
    py_modules=['pyhtml'],
    zip_safe=False,
    include_package_data=True,
    test_suite='tests',
    description='Simple HTML generator for Python',
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
