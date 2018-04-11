import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "ebookpull-api",
    version = "0.0.1",
    author = "Matt Loar",
    author_email = "matt@loar.name",
    description = ("JSON API for the e-Bookpull application."),
    license = "",
    keywords = "",
    url = "",
    packages=['e_bookpull_api'],
    long_description=read('README'),
    classifiers=[
    ],
    install_requires=[
        'Flask-REST-JSONAPI',
        'Flask-MySQLdb'
    ]
)
