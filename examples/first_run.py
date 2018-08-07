#!/usr/bin/env python
#
# Very basic PyADB example
#

try:
    import sys
    from pyadb import ADB
except ImportError as e:
    # should never be reached
    print ("[f] Required module missing. %s" % e.args[0])
    sys.exit(-1)

def main():
    # creates the ADB object
    adb = ADB()
    # IMPORTANT: You should supply the absolute path to ADB binary 
    if adb.set_adb_path('/usr/bin/adb') is True:
        print ("Version: %s" % adb.get_version())
    else:
        print ("Check ADB binary path")

    apps = adb.shell_command("pm list packages")
    for app in apps:
        path = adb.shell_command("pm path {}".format(app.split(':')[1]))
        print ("{}: {}".format(app,path))

if __name__ == "__main__":
    main()
