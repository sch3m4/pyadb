#!/usr/bin/env python
#
# Very basic PyADB example
#

import sys
try:
    from pyadb import ADB
except ImportError as e:
    # should never be reached
    print(("[f] Required module missing. %s" % e.args[0]))
    sys.exit(-1)


def main():
    # creates the ADB object
    adb = ADB()
    # set ADB path, using a couple of popular addresses.
    try:
        adb.set_adb_path('~/android-sdk-linux/platform-tools/adb')
    except FileNotFoundError:
        adb.set_adb_path(r'C:\Android\android-sdk\platform-tools\adb.exe')

    apps = adb.shell_command("pm list packages")
    for app in apps:
        path = adb.shell_command("pm path {}".format(app.split(':')[1]))
        print(("{}: {}".format(app, path)))


if __name__ == "__main__":
    main()
