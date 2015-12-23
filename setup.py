import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyadb",
    version = "0.1.4",
    author = "Chema Garcia",
    author_email = "chema@safetybits.net",
    description = ("Simple python module to interact with Android Debug Bridge tool"),
    license = "BSD",
    keywords = "python android adb",
    url = "https://github.com/sch3m4/pyadb",
    packages=['pyadb'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
