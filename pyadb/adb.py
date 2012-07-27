# Author: Chema Garcia (aka sch3m4)
# Contact: chema@safetybits.net | http://safetybits.net/contact 
# Homepage: http://safetybits.net
# Project Site: http://github.com/sch3m4/pyadb

try:
    import sys
    from os import popen3 as pipe
except ImportError,e:
    # should never be reached
    print "[f] Required module missing. %s" % e.args[0]
    sys.exit(-1)

class ADB():
    
    PYADB_VERSION = "0.1.1"
    
    __adb_path = None
    __output = None
    __error = None
    __devices = None
    __target = None

    # reboot modes
    REBOOT_RECOVERY = 1
    REBOOT_BOOTLOADER = 2
    
    # default TCP/IP port
    DEFAULT_TCP_PORT = 5555
    # default TCP/IP host
    DEFAULT_TCP_HOST = "localhost"
    
    def pyadb_version(self):
        return self.PYADB_VERSION

    def __init__(self,adb_path=None):
        self.__adb_path = adb_path

    def __clean__(self):
        self.__output = None
        self.__error = None

    def __read_output__(self,fd):
        ret = ''
        while 1:
            line = fd.readline()
            if not line:
                break
            ret += line

        if len(ret) == 0:
            ret = None

        return ret

    def __build_command__(self,cmd):
        if self.__devices is not None and len(self.__devices) > 1 and self.__target is None:
            self.__error = "Must set target device first"
            return None
        return self.__adb_path + ' ' + cmd if self.__target is None else self.__adb_path + ' ' + ' -s ' + self.__target + ' ' + cmd
    
    def get_output(self):
        return self.__output
    
    def get_error(self):
        return self.__error
    
    def lastFailed(self):
        """
        Was failed the last command?
        """
        if self.__output is None and self.__error is not None:
            return True
        return False

    def run_cmd(self,cmd):
        """
        Run a command against adb tool ($ adb <cmd>)
        """
        self.__clean__()

        if self.__adb_path is None:
            self.__error = "ADB path not set"
            return

        try:
            w,r,e = pipe(self.__build_command__(cmd), mode='r')
            self.__output = self.__read_output__(r)
            self.__error = self.__read_output__(e)
            r.close()
            w.close()
            e.close()
        except:
            pass

        return

    def get_version(self):
        """
        Returns ADB tool version
        adb version
        """
        self.run_cmd("version")
        try:
            ret = self.__output.split()[-1:][0]
        except:
            ret = None
        return ret

    def check_path(self):
        """
        Intuitive way to verify the ADB path
        """
        if self.get_version() is None:
            return False
        return True

    def set_adb_path(self,adb_path):
        """
        Set ADB tool path
        """
        self.__adb_path = adb_path

    def get_adb_path(self):
        """
        Returns ADB tool path
        """
        return self.__adb_path

    def start_server(self):
        """
        Starts ADB server
        adb start-server
        """
        self.__clean__()
        self.run_cmd('start-server')
        return self.__output

    def kill_server(self):
        """
        Kills ADB server
        adb kill-server
        """
        self.__clean__()
        self.run_cmd('kill-server')

    def restart_server(self):
        """
        Restarts ADB server
        """
        self.kill_server()
        return self.start_server()

    def restore_file(self,file_name):
        """
        Restore device contents from the <file> backup archive
        adb restore <file>
        """
        self.__clean__()
        self.run_cmd('restore %s' % file_name)
        return self.__output

    def wait_for_device(self):
        """
        Block until device is online
        adb wait-for-device
        """
        self.__clean__()
        self.run_cmd('wait-for-device')
        return self.__output

    def get_help(self):
        """
        Returns ADB help
        adb help
        """
        self.__clean__()
        self.run_cmd('help')
        return self.__output

    def get_devices(self):
        """
        Return a list of connected devices
        adb devices
        """
        error = 0
        self.run_cmd("devices")        
        if self.__error is not None:
            return ''
        try:
            self.__devices = self.__output.partition('\n')[2].replace('device','').split()
            
            if self.__devices[1:] == ['no','permissions']:
                error = 2
                self.__devices = None                
        except:
            self.__devices = None
            error = 1

        return (error,self.__devices)

    def set_target_device(self,device):
        """
        Select the device to work with
        """
        self.__clean__()
        if device is None or not device in self.__devices:
            self.__error = 'Must get device list first'
            return False
        self.__target = device
        return True

    def get_target_device(self):
        """
        Returns the selected device to work with
        """
        return self.__target

    def get_state(self):
        """
        Get ADB state
        adb get-state
        """
        self.__clean__()
        self.run_cmd('get-state')
        return self.__output

    def get_serialno(self):
        """
        Get serialno from target device
        adb get-serialno
        """
        self.__clean__()
        self.run_cmd('get-serialno')
        return self.__output

    def reboot_device(self,mode):
        """
        Reboot the target device
        adb reboot recovery/bootloader
        """
        self.__clean__()
        if not mode in (self.REBOOT_RECOVERY,self.REBOOT_BOOTLOADER):
            self.__error = "mode must be REBOOT_RECOVERY/REBOOT_BOOTLOADER"
            return self.__output
        self.run_cmd("reboot %s" % "recovery" if mode == self.REBOOT_RECOVERY else "bootloader")
        return self.__output

    def set_adb_root(self,mode):
        """
        restarts the adbd daemon with root permissions
        adb root
        """
        self.__clean__()
        self.run_cmd('root')
        return self.__output

    def set_system_rw(self):
        """
        Mounts /system as rw
        adb remount
        """
        self.__clean__()
        self.run_cmd("remount")
        return self.__output

    def get_remote_file(self,remote,local):
        """
        Pulls a remote file
        adb pull remote local
        """
        self.__clean__()
        self.run_cmd('pull \"%s\" \"%s\"' % (remote,local) )
        if "bytes in" in self.__error:
            self.__output = self.__error
            self.__error = None
        return self.__output

    def push_local_file(self,local,remote):
        """
        Push a local file
        adb push local remote
        """
        self.__clean__()
        self.run_cmd('push \"%s\" \"%s\"' % (local,remote) )
        return self.__output

    def shell_command(self,cmd):
        """
        Executes a shell command
        adb shell <cmd>
        """
        self.__clean__()
        self.run_cmd('shell %s' % cmd)
        return self.__output

    def listen_usb(self):
        """
        Restarts the adbd daemon listening on USB
        adb usb
        """
        self.__clean__()
        self.run_cmd("usb")
        return self.__output

    def listen_tcp(self,port=DEFAULT_TCP_PORT):
        """
        Restarts the adbd daemon listening on the specified port
        adb tcpip <port>
        """
        self.__clean__()
        self.run_cmd("tcpip %s" % port)
        return self.__output

    def get_bugreport(self):
        """
        Return all information from the device that should be included in a bug report
        adb bugreport
        """
        self.__clean__()
        self.run_cmd("bugreport")
        return self.__output

    def get_jdwp(self):
        """
        List PIDs of processes hosting a JDWP transport
        adb jdwp
        """
        self.__clean__()
        self.run_cmd("jdwp")
        return self.__output

    def get_logcat(self,lcfilter=""):
        """
        View device log
        adb logcat <filter>
        """
        self.__clean__()
        self.run_cmd("logcat %s" % lcfilter)
        return self.__output

    def run_emulator(self,cmd=""):
        """
        Run emulator console command
        """
        self.__clean__()
        self.run_cmd("emu %s" % cmd)
        return self.__output
    
    def connect_remote (self,host=DEFAULT_TCP_HOST,port=DEFAULT_TCP_PORT):
        """
        Connect to a device via TCP/IP
        adb connect host:port
        """
        self.__clean__()
        self.run_cmd("connect %s:%s" % ( host , port ) )
        return self.__output
    
    def disconnect_remote (self , host=DEFAULT_TCP_HOST , port=DEFAULT_TCP_PORT):
        """
        Disconnect from a TCP/IP device
        adb disconnect host:port
        """
        self.__clean__()
        self.run_cmd("disconnect %s:%s" % ( host , port ) )
        return self.__output
    
    def ppp_over_usb(self,tty=None,params=""):
        """
        Run PPP over USB
        adb ppp <tty> <params>
        """
        self.__clean__()
        if tty is None:
            return self.__output
        
        cmd = "ppp %s" % tty
        if params != "":
            cmd += " %s" % params
            
        self.run_cmd(cmd)
        return self.__output

    def sync_directory(self,directory=""):
        """
        Copy host->device only if changed (-l means list but don't copy)
        adb sync <dir>
        """
        self.__clean__()
        self.run_cmd("sync %s" % directory )
        return self.__output
    
    def forward_socket(self,local=None,remote=None):
        """
        Forward socket connections
        adb forward <local> <remote>
        """
        self.__clean__()
        if local is None or remote is None:
            return self.__output
        self.run_cmd("forward %s %s" % (local,remote) )
        return self.__output


    def uninstall(self,package=None,keepdata=False):
        """
        Remove this app package from the device
        adb uninstall [-k] package
        """
        self.__clean__()
        if package is None:
            return self.__output
        cmd = "uninstall %s" % (package if keepdata is True else "-k %s" % package )
        self.run_cmd(cmd)
        return self.__output

    def install(self,fwdlock=False,reinstall=False,sdcard=False,pkgapp=None):
        """
        Push this package file to the device and install it
        adb install [-l] [-r] [-s] <file>
        -l -> forward-lock the app
        -r -> reinstall the app, keeping its data
        -s -> install on sdcard instead of internal storage
        """

        self.__clean__()
        if pkgapp is None:
            return self.__output
        
        cmd = "install "
        if fwdlock is True:
            cmd += "-l "
        if reinstall is True:
            cmd += "-r "
        if sdcard is True:
            cmd += "-s "
        
        self.run_cmd("%s %s" % (cmd , pkgapp) )
        return self.__output

    def find_binary(self,name=None):
        """
        Look for a binary file on the device
        """
        
        self.shell_command("which %s" % name)
        
        if self.__output is None: # not found
            self.__error = "'%s' was not found" % name
        elif self.__output.strip() == "which: not found": # which binary not available
            self.__output = None
            self.__error = "which binary not found"
        else:
            self.__output = self.__output.strip()

        return self.__output
