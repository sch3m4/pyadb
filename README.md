![build_travis](https://travis-ci.org/sch3m4/pyadb.svg?branch=master)

Simple python module to interact with the ADB tool

### How to install:

Currently there is no Debian package available for PyADB. (Will be fixed soon...)

#### Debian Package:

    $ sudo dpkg -i python-pyadb_0.1.1-1_all.deb 
    Selecting previously unselected package python-pyadb.
    (Leyendo la base de datos ... 322039 ficheros o directorios instalados actualmente.)
    Desempaquetando python-pyadb (de python-pyadb_0.1.1-1_all.deb) ...
    Configurando python-pyadb (0.1.1-1) ...
    $

#### Pip (Not always the latest version)

    $ sudo easy_install pyadb
    Searching for pyadb
    ...
    Processing dependencies for pyadb
    Finished processing dependencies for pyadb
    $

#### From source

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

    $ python
    Python 2.7.6 (default, Mar 22 2014, 22:59:56) 
    [GCC 4.8.2] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from pyadb import ADB
    >>> adb = ADB('/home/chema/.android-sdks/platform-tools/adb')
    >>> adb.pyadb_version()
    '0.1.4'
    >>> adb.get_version()
    '1.0.32'
    >>> 
    >>> quit()
    $
