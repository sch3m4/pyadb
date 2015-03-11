#!/usr/bin/env python

"""
Simple pyadb example to retrieve whatsapp
databases from the selected device.

~/pyadb/example$ python whatsapp.py

[+] Using PyADB version 0.1.1
[+] Verifying ADB path... OK
[+] ADB Version: 1.0.29

[+] Restarting ADB server...
[+] Detecting devices... OK
    0: XXXXXXXXXXX

[+] Using "XXXXXXXXXXX" as target device
[+] Looking for 'su' binary:  /system/xbin/su
[+] Checking if 'su' binary can give root access:
    - Yes

[+] Copying Whatsapp data folder
    - Local destination [~/pyadb/example]: 
 
[+] Creating remote tar file: /sdcard/whatsapp_hpBSiSnPYI.tar
    - Command: /system/xbin/su -c 'tar -c /data/data/com.whatsapp -f /sdcard/whatsapp_hpBSiSnPYI.tar'

[+] Retrieving remote file: /sdcard/whatsapp_hpBSiSnPYI.tar
[+] Removing remote file: /sdcard/whatsapp_hpBSiSnPYI.tar

[+] Remote Whatsapp files from device memory are now locally accessible at "~/pyadb/example/databases/whatsapp_hpBSiSnPYI.tar"
[+] Looking for 'tar' binary... /system/xbin/tar

[+] Creating remote tar file: /sdcard/whatsapp_djsAFumAGW.tar
    + Command: /system/xbin/tar -c /sdcard/WhatsApp -f /sdcard/whatsapp_djsAFumAGW.tar

[+] Remote tar file created: /sdcard/whatsapp_djsAFumAGW.tar
    - Local destination [~/pyadb/example]: 
 
[+] Retrieving remote file: /sdcard/whatsapp_djsAFumAGW.tar...

[+] WhatsApp SDcard folder is now available in tar file: ~/pyadb/example/whatsapp_djsAFumAGW.tar

~/pyadb/example$
"""

try:
    import random
    import string
    import errno
    from os import getcwd
    from sys import stdin,exit
    from os.path import basename
    from os import mkdir
    from pyadb import ADB
except ImportError,e:
    print "[f] Required module missing. %s" % e.args[0]
    exit(-1)


def get_whatsapp_root(adb,supath):
    
    tmp = getcwd()
    print "\n[+] Copying Whatsapp data folder"
    print "\t- Local destination [%s]: " % tmp ,
    destination = stdin.readline().strip()
    if destination == '':
        destination = tmp
    
    if not destination[-1:] == '/':
        destination += '/'
    destination += 'databases/' 
    
    try:
        mkdir(destination)
    except OSError,e:
        if e.errno == errno.EEXIST:
            pass
        else:
            return (False,e.args)
    except Exception,e:
        return (False,e.msg)

    tarname = '/sdcard/whatsapp_' + ''.join(random.choice(string.letters) for i in xrange(10)) + '.tar'
    print "\n[+] Creating remote tar file: %s" % tarname
    
    cmd = "%s -c 'tar -c /data/data/com.whatsapp -f %s'" % (supath,tarname)
    print "\t- Command: %s" % cmd
    adb.shell_command(cmd)
    
    print "\n[+] Retrieving remote file: %s" % tarname
    adb.get_remote_file(tarname, destination + '/' + basename(tarname))
    
    print "[+] Removing remote file: %s" % tarname
    cmd = 'su -c \'rm %s\'' % tarname    
    adb.shell_command(cmd)

    print "\n[+] Remote Whatsapp files from device memory are now locally accessible at \"%s%s\"\n" % (destination,basename(tarname))
    
    get_whatsapp_nonroot(adb)
    return (True,"")

def get_sdcard_iter ( adb , rpath = None , lpath = None ):
    """
    When 'tar' binary is not available, this method get the whole content of the remote WhastApp directory from the sdcard
    """
    
    if lpath is None:
        return (False,"Local path not provided")
    
    maindir = "/sdcard/WhatsApp/"
    
    if rpath is None:
        rdir = maindir
    else:
        rdir = rpath
    
    res = adb.shell_command("ls -1 \"%s\"" % rdir )
    if res == "ls: %s: No such file or directory" % rdir:
        return (False,"WhatsApp directory does not exists!")
    
    try:
        res = res.split('\n')
    except:
        return (False,"Directory empty")
    
    for item in res:
        
        try:
            item = item.strip()
            if item == "":
                continue
        except:
            continue
        
        ftype = adb.shell_command("ls -ld \"%s\"" % (rdir + item))[:1]
        # if it is a directory
        if ftype == "d":
            try:
                mkdir(lpath + item)
            except Exception,e:
                pass
            get_sdcard_iter(adb,rdir + item + '/' , lpath + item + '/' )
        else: # item is a file
            print "\t- Retrieving remote file: %s" % (rdir + item)
            adb.get_remote_file(rdir + item , lpath + item )
    
    return (True,"")

def create_sdcard_tar (adb,tarpath):
    """
    Returns the remote path of the tar file containing the whole WhatsApp directory from the SDcard
    """
    tarname = '/sdcard/whatsapp_' + ''.join(random.choice(string.letters) for i in xrange(10)) + '.tar'
    print "\n[+] Creating remote tar file: %s" % tarname
    cmd = "%s -c /sdcard/WhatsApp -f %s" % (tarpath , tarname)
    print "\t+ Command: %s" % cmd
    adb.shell_command(cmd).strip()
    res = adb.shell_command("ls %s" % tarname).strip()
    if res == "ls: %s: No such file or directory" % tarname:
        return None
    else:
        return tarname

def get_destination_path():
    """
    Creates and returns the path provided by the user
    """
    tmp = getcwd()
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
            return None
    except Exception,e:
        print "\t- ERROR!: " , e.mgs
        return None
    
    return destination
    
def get_whatsapp_nonroot(adb):
    """
    Method to get the whole WhatsApp directory from the SD card
    """

    # look for 'tar' binary
    print "[+] Looking for 'tar' binary...",
    tarpath = adb.find_binary("tar")
    
    if tarpath is None:
        print "Error: %s" % adb.get_error()
    else:
        print "%s" % tarpath
    
    if tarpath is not None:
        wapath = create_sdcard_tar(adb,tarpath)
        print "\n[+] Remote tar file created: %s" % wapath
        destination = get_destination_path()
        if destination is not None:
            print "\n[+] Retrieving remote file: %s..." % wapath
            adb.get_remote_file(wapath, destination + basename(wapath))
            adb.shell_command("rm %s" % wapath)
            print "\n[+] WhatsApp SDcard folder is now available in tar file: %s\n" % (destination + basename(wapath))
            return
        else:
            adb.shell_command("rm %s" % wapath)
            
    # get the remote WhatsApp folder from the SDcard (the iterative way)
    path = get_destination_path()
    if path is None:
        print "\n[!] Error while retrieving remote WhatsApp SDcard folder: Used has provided an invalid path"
        return
    
    print "\n[+] Retrieving remote WhatsApp SDcard folder..."
    ret,error = get_sdcard_iter(adb , None , path )
    if ret is True:
        print "\n[+] Remote WhatsApp SDcard folder is now available at: %s" % path
    else:
        print "\n[!] Error while retrieving remote WhastsApp SDcard folder: %s" % error

    return

def main():
    
    adb = ADB()
    
    # set ADB path
    adb.set_adb_path('~/android-sdk-linux/platform-tools/adb')
    
    print "[+] Using PyADB version %s" % adb.pyadb_version()
    
    # verity ADB path
    print "[+] Verifying ADB path...",
    if adb.check_path() is False:
        print "ERROR"
        exit(-2)
    print "OK"
    
    # print ADB Version
    print "[+] ADB Version: %s" % adb.get_version()
    
    print ""
    
    # restart server (may be other instances running)
    print "[+] Restarting ADB server..."
    adb.restart_server()
    if adb.lastFailed():
        print "\t- ERROR\n"
        exit(-3)
    
    # get detected devices
    dev = 0
    while dev is 0:
        print "[+] Detecting devices..." ,
        error,devices = adb.get_devices()
    
        if error is 1:
            # no devices connected
            print "No devices connected"
            print "[+] Waiting for devices..."
            adb.wait_for_device()
            continue
        elif error is 2:
            print "You haven't enought permissions!"
            exit(-3)
            
        print "OK"
        dev = 1

    # this should never be reached
    if len(devices) == 0:
        print "[+] No devices detected!"
        exit(-4)

    # show detected devices
    i = 0
    for dev in devices:
        print "\t%d: %s" % (i,dev)
        i += 1
    
    # if there are more than one devices, ask to the user to choose one of them
    if i > 1:
        dev = i + 1
        while dev < 0 or dev > int(i - 1):
            print "\n[+] Select target device [0-%d]: " % int(i - 1) ,
            dev = int(stdin.readline())
    else:
        dev = 0
    
    # set target device
    try:
        adb.set_target_device(devices[dev])
    except Exception,e:
        print "\n[!] Error:\t- ADB: %s\t - Python: %s" % (adb.get_error(),e.args)
        exit(-5)

    print "\n[+] Using \"%s\" as target device" % devices[dev]
    
    # check if 'su' binary is available
    print "[+] Looking for 'su' binary: ",
    supath = adb.find_binary("su")

    if supath is not None:
        print "%s" % supath
    else:
        print "Error: %s" % adb.get_error()

    # 'su' binary has been found
    if supath is not None:
        print "[+] Checking if 'su' binary can give root access:"
        rootid = adb.shell_command('%s -c id' % supath)
        if adb.lastFailed() is False and 'root' in rootid.replace('(',')').split(')'): # it can provide root privileges
            print "\t- Yes"
            get_whatsapp_root(adb,supath)
        else: # only have normal-user 
            print "\t- No: %s" % adb.get_error()
            get_whatsapp_nonroot(adb)
    else:
        get_whatsapp_nonroot(adb)

    exit(0)

if __name__ == "__main__":
    main()
