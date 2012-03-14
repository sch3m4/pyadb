from os import popen3 as pipe

class ADB():
    __adb_path = None
    __output = None
    __error = None
    __devices = None
    __target = None
    
    # reboot modes
    REBOOT_RECOVERY = 1
    REBOOT_BOOTLOADER = 2
        
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
        """
        self.run_cmd("version")
        try:
            ret = self.__output.split()[-1:][0]
        except:
            ret = None
        return ret
    
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
        """
        self.__clean__()
        self.run_cmd('start-server')
        return self.__output
    
    def kill_server(self):
        """
        Kills ADB server
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
        Restore device contents from de <file> backup archive
        """
        self.__clean__()
        self.run_cmd('restore %s' % file_name)
        return self.__output
    
    def wait_for_device(self):
        """
        Block until device is online
        """
        self.__clean__()
        self.run_cmd('wait-for-device')
        return self.__output
        
    def get_help(self):
        """
        Returns ADB help
        """
        self.__clean__()
        self.run_cmd('help')
        return self.__output
    
    def get_devices(self):
        """
        Return a list of connected devices
        """
        self.run_cmd("devices")        
        if self.__error is not None:
            return ''
        try:
            self.__devices = self.__output.partition('\n')[2].replace('device','').split()
        except:
            self.__devices = None
            
        return self.__devices
    
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
        self.__clean__()
        self.run_cmd('get-state')
        return self.__output

    def get_serialno(self):
        """
        Get serialno from target device
        """
        self.__clean__()
        self.run_cmd('get-serialno')
        return self.__output
    
    def reboot_device(self,mode):
        """
        Reboot the target device
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
        """
        self.__clean__()
        self.run_cmd('root')
        return self.__output

    def set_system_rw(self):
        """
        Mounts /system as rw
        """
        self.__clean__()
        self.run_cmd("remount")
        return self.__output

    def get_remote_file(self,remote,local):
        """
        Pulls a remote file
        """
        self.__clean__()
        self.run_cmd('pull \"%s\" \"%s\"' % (remote,local) )
        if "bytes in" in self.__error:
            self.__output = self.__error
            self.__error = None
        return self.__output
    
    def set_remote_file(self,local,remote):
        """
        Push a local file
        """
        self.__clean__()
        self.run_cmd('push \"%s\" \"%s\"' % (local,remote) )
        return self.__output
    
    def shell_command(self,cmd):
        """
        Executes a shell command
        """
        self.__clean__()
        self.run_cmd('shell %s' % cmd)
        return self.__output