#!/usr/bin/env python
#
# Very basic PyADB example
#

try:
    import sys
    from pyadb import ADB
except ImportError,e:
    # should never be reached
    print "[f] Required module missing. %s" % e.args[0]
    sys.exit(-1)

def main():
    # creates the ADB object
    adb = ADB()
    # IMPORTANT: You should supply the absolute path to ADB binary 
    if adb.set_adb_path('/home/chema/.android-sdks/platform-tools/adb') is True:
        print "Version: %s" % adb.get_version()
    else:
        print "Check ADB binary path"
    
    print "Waiting for device..."
    adb.wait_for_device()
    err,dev = adb.get_devices()
    
    if len(dev) == 0:
        print "Unexpected error, may be you're a very fast guy?"
        return
    
    print "Selecting: %s" % dev[0]
    adb.set_target_device(dev[0])
    
    print "Executing 'ls' command"
    adb.shell_command('ls')
    
    print "Output:\n%s" % adb.get_output()
        

if __name__ == "__main__":
    main()
    