import os
from distutils.core import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyadb",
    version = "0.0.4",
    author = "Chema Garcia",
    author_email = "sch3m4@opensec.es",
    description = ("Simple python module to access ADB tool"),
    license = "BSD",
    keywords = "python android adb",
    url = "https://github.com/sch3m4/pyadb",
    packages=['pyadb'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)