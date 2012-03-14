"""
Simple pyadb example to retrieve whatsapp
databases from the selected device.

~/pyadb/example$ python whatsapp.py 

[+] ADB Version:  1.0.29
[+] Detected devices:
    0: XXXXXXXXXXXX
    1: YYYYYYYYYYYY

+ Select target device [0-1]: 0
 
+ Using "XXXXXXXXXXXX" as device target
+ Looking for 'su' binary:  Found at '/system/xbin/su'
+ Checking if 'su' binary can give root access:  YES ->  uid=0(root) gid=0(root)

+ Copying Whatsapp data folder
    - Local destination [~/pyadb/example]: 
 
[1/3] Creating tar file: /mnt/sdcard/whatsapp_xQqoJVeXjY.tar
    - Command: su -c 'tar -c /data/data/com.whatsapp -f /mnt/sdcard/whatsapp_xQqoJVeXjY.tar'

[2/3] Getting remote file: /mnt/sdcard/whatsapp_xQqoJVeXjY.tar
    2139 KB/s (498176 bytes in 0.227s)

[3/3] Removing remote file: /mnt/sdcard/whatsapp_xQqoJVeXjY.tar
    - Command: su -c 'rm /mnt/sdcard/whatsapp_xQqoJVeXjY.tar'

+ ;-) Success!! Remote Whatsapp files are now locally accessible at "~/pyadb/example/whatsapp_xQqoJVeXjY.tar"

~/pyadb/example$
"""

import random
import string
import errno
from os import getcwd
from sys import stdin,exit
from os.path import basename
from os import mkdir
from pyadb.adb import ADB

def main():
    adb = ADB()
    adb.set_adb_path('~/android-sdk-linux_x86/platform-tools/adb')
    
    print "\n[+] ADB Version: " , adb.get_version()
    
    adb.restart_server()
    
    print "[+] Detected devices:"
    devices = adb.get_devices()
    
    if devices[1:] == ['no','permissions']:
        print "\t- Not enought permissions!\n"
        exit(-1)
    
    i = 0
    for dev in devices:
        print "\t%d: %s" % (i,dev)
        i += 1
        
    if len(devices) == 0:
        print "\t- No devices found!\n"
        exit(0)
    
    if i > 1:
        dev = i + 1
        while dev < 0 or dev > int(i - 1):
            print "\n+ Select target device [0-%d]: " % int(i - 1) ,
            dev = int(stdin.readline())
    else:
        dev = 0
    
    try:
        adb.set_target_device(devices[dev])
    except Exception,e:
        print "\n+ Error:\t- ADB: %s\t - Python: %s" % (adb.get_error(),e.args)
        exit(-1)

    print "\n+ Using \"%s\" as device target" % devices[dev]
    
    print "+ Looking for 'su' binary: " ,
    supath = adb.shell_command('which su').strip()
    err = adb.get_error()
    if err is None:
        print "Found at '%s'" % supath
    else:
        print "Error: %s" % err
        exit(-2)
        
    print "+ Checking if 'su' binary can give root access: " ,
    id = adb.shell_command('su -c id')
    err = adb.get_error()
    if err is None and 'root' in id.replace('(',')').split(')'):
        print "YES -> " , id
    else:
        print "Error: %s" % err
        exit(-3)

    tmp = getcwd()
    print "+ Copying Whatsapp data folder"
    print "\t- Local destination [%s]: " % tmp ,
    destination = stdin.readline().strip()
    if destination == '':
        destination = tmp
    
    if not destination[-1:] == '/':
        destination += '/' 
    
    try:
        mkdir(destination)
    except OSError,e:
        if e.errno == errno.EEXIST:
            pass
        else:
            print "\t- ERROR!: " , e.args
            exit(-4)
    except Exception,e:
        print "\t- ERROR!: " , e.mgs
        exit(-5)

    tarname = '/mnt/sdcard/whatsapp_' + ''.join(random.choice(string.letters) for i in xrange(10)) + '.tar'
    print "\n[1/3] Creating tar file: %s" % tarname
    
    cmd = 'su -c \'tar -c /data/data/com.whatsapp -f %s\'' % tarname
    print "\t- Command: %s" % cmd
    
    try:
        adb.shell_command(cmd)
    except Exception,e:
        print "\n+ Error:\t- ADB: %s\t - Python: %s" % (adb.get_error(),e.msg)
        exit(-1)
    
    print "\n[2/3] Getting remote file: %s" % tarname
    adb.get_remote_file(tarname, destination + '/' + basename(tarname))
    
    output = adb.get_output()
    if output is None:
        print "\t- Error getting file!\n"
        exit(-2)
    print "\t%s" % adb.get_output()
    
    print "[3/3] Removing remote file: %s" % tarname
    cmd = 'su -c \'rm %s\'' % tarname
    print "\t- Command: %s" % cmd
    
    try:
        adb.shell_command(cmd)
    except Exception,e:
        print "\n+ Error:\t- ADB: %s\t - Python: %s" % (adb.get_error(),e.msg)
        exit(-1)

    print "\n+ ;-) Success!! Remote Whatsapp files are now locally accessible at \"%s%s\"\n" % (destination,basename(tarname))

if __name__ == "__main__":
    main()