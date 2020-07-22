![build_travis](https://travis-ci.org/sch3m4/pyadb.svg?branch=master)

Python module to interact with the ADB tool

#### Install from source

    $ python setup.py build
    running build
    running build_py
    creating build
    creating build/lib.linux-i686-2.7
    creating build/lib.linux-i686-2.7/pyadb
    copying pyadb/adb.py -> build/lib.linux-i686-2.7/pyadb
    copying pyadb/__init__.py -> build/lib.linux-i686-2.7/pyadb
    $ sudo python setup.py install
    running install
    running build
    running build_py
    running install_lib
    running install_egg_info
    Removing /usr/local/lib/python2.7/dist-packages/pyadb-0.1.4.egg-info
    Writing /usr/local/lib/python2.7/dist-packages/pyadb-0.1.4.egg-info
    $

More instructions: http://wiki.python.org/moin/CheeseShopTutorial

#### Usage:

    ➜  pyadb git:(master) ✗ python3
    Python 3.6.9 (default, Apr 18 2020, 01:56:04) 
    [GCC 8.4.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from pyadb import ADB
    >>> adb = ADB("/usr/bin/adb")
    >>> adb.pyadb_version()
    '0.1.5jo'
    >>> adb.get_version()
    '1.0.39'
    >>> quit()
    ➜  pyadb git:(master) ✗ 
