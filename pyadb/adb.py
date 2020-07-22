# Author: Chema Garcia (aka sch3m4)
# Contact: chema@safetybits.net | @sch3m4 | http://safetybits.net/contact 
# Homepage: http://safetybits.net
# Project Site: http://github.com/sch3m4/pyadb


import logging
import os
import subprocess
import sys


class ADB:
    PYADB_VERSION = "0.1.5jo"

    LOGGER = logging.getLogger("pyadb")

    _adb_path = None
    _devices = None

    # reboot modes
    REBOOT_RECOVERY = 1
    REBOOT_BOOTLOADER = 2

    # default TCP/IP port
    DEFAULT_TCP_PORT = 5555
    # default TCP/IP host
    DEFAULT_TCP_HOST = "localhost"

    class AdbException(Exception):
        pass

    class BadCall(AdbException):
        """ Client called pyadb incorrectly. """
        pass

    class PermissionsError(BadCall):
        """ Insufficient permissions (to list devices) """

    class InternalError(AdbException):
        """" Unexpected internal error in pyadb. """
        pass

    def pyadb_version(self):
        return self.PYADB_VERSION

    def __init__(self, adb_path=None):
        if adb_path:
            if self._adb_path and self._adb_path != adb_path:
                raise self.BadCall(
                        "Only one adp path can be set for all instances. "
                        "Use set_adp_path to change for all instance.")
            ADB._adb_path = adb_path
        self._target = None

    def _parse_output(self, outstr):
        ret = None

        if len(outstr) > 0:
            ret = outstr.splitlines()

        return ret

    @classmethod
    def _output_if_no_error(cls, cmd_result):
        output, error = cmd_result
        if error:
            raise cls.InternalError(error)
        return output

    COMMANDS_WITHOUT_TARGETS = (
        "devices",
        "kill-server",
        "start-server",
        "version",
        "help"
        )

    @classmethod
    def _check_target(cls, cmd, target):
        if target is None and all(
                safe_commands not in cmd for safe_commands
                in cls.COMMANDS_WITHOUT_TARGETS):
            raise cls.BadCall("Must set target device first")

    @classmethod
    def _build_command_c(cls, cmd, target=None):
        # The _c version can be called from a classmethod.
        cls._check_target(cmd, target)

        # Modified function to directly return command set for Popen
        #
        # Unfortunately, there is something odd going on and the argument
        # list is not being properly converted to a string on the Windows 7
        # test systems.  To accommodate this, this block explicitly detects
        # Windows vs. non-windows and builds the OS-dependent command output
        #
        # Command in 'list' format: Thanks to Gil Rozenberg for reporting
        # the issue
        #
        target_param_part = ["-s", target] if target else []
        cmd_part = [cmd] if not isinstance(cmd, list) else cmd

        full_cmd = [ADB._adb_path] + target_param_part + cmd_part

        if sys.platform.startswith('win'):
            return " ".join(full_cmd)
        else:
            return full_cmd

    def _build_command(self, cmd):
        self._build_command_c(cmd, target=self._target)

    @classmethod
    def run_cmd_c(cls, cmd, target=None):
        """
        Runs a command by using adb tool ($ adb <cmd>)
        """
        if cls._adb_path is None:
            raise cls.BadCall("ADB path not set")

        # For compat of windows
        cmd_list = cls._build_command_c(cmd, target)

        cls.LOGGER.info("Executing command: %s", cmd_list)

        try:
            adb_proc = subprocess.Popen(
                    cmd_list,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=False)
            (output, error) = adb_proc.communicate()
            # return_code = adb_proc.returncode
            output = output.decode('utf-8')
            error = error.decode('utf-8')

            if len(output) == 0:
                output = None
            else:
                output = [x.strip() for x in output.split('\n')
                          if len(x.strip()) > 0]

        except Exception as err:
            cls.LOGGER.exception("Unexpected exception")
            raise cls.InternalError(str(err))

        return output, error

    def run_cmd(self, cmd):
        return self.run_cmd_c(cmd, self._target)

    @classmethod
    def get_version(cls):
        """
        Returns ADB tool version
        adb version
        """
        output = cls._output_if_no_error(cls.run_cmd_c("version"))
        if output is None or len(output) < 1:
            cls.LOGGER.warning(
                    "No version found. Check adb is on path %s.",
                    ADB._adb_path)
            return None

        try:
            ret = output[0].split()[-1:][0]
            return ret
        except Exception as err:
            cls.LOGGER.exception(
                    "Unexpected output %s caused %s", output, err)
            raise cls.InternalError(output)

    @classmethod
    def check_path(cls):
        """
        Intuitive way to verify the ADB path
        """
        return bool(cls.get_version())

    @classmethod
    def set_adb_path(cls, adb_path):
        """
        Sets ADB tool absolute path
        """
        if not os.path.isfile(adb_path):
            raise cls.BadCall("File not found.")
        cls._adb_path = adb_path

    @classmethod
    def get_adb_path(cls):
        """
        Returns ADB tool path
        """
        return cls._adb_path

    @classmethod
    def start_server(cls):
        """
        Starts ADB server
        adb start-server

        """
        return cls.run_cmd_c('start-server')[0]

    @classmethod
    def kill_server(cls):
        """
        Kills ADB server
        adb kill-server

        Ignores errors.
        """
        return cls._output_if_no_error(cls.run_cmd_c('kill-server'))

    @classmethod
    def restart_server(cls):
        """
        Restarts ADB server
        """
        cls.kill_server()
        return cls.start_server()

    def restore_file(self, file_name):
        """
        Restore device contents from the <file> backup archive
        adb restore <file>
        """
        return self._output_if_no_error(self.run_cmd(['restore', file_name]))

    def wait_for_device(self):
        """
        Blocks until device is online
        adb wait-for-device
        """
        return self._output_if_no_error(self.run_cmd('wait-for-device'))

    @classmethod
    def get_help(cls):
        """
        Returns ADB help
        adb help
        """
        return cls._output_if_no_error(cls.run_cmd_c('help'))

    @classmethod
    def get_devices(cls):
        """
        Returns a list of connected devices
        adb devices
        mode serial/usb
        """
        cls._devices = None
        output = cls._output_if_no_error(cls.run_cmd_c("devices"))
        try:
            cls._devices = [x.split()[0] for x in output[1:]]

        except Exception as err:
            # ToDo: Limit this except-clause to the specific exception.
            cls.LOGGER.exception(
                    "Exception being translated to PermissionsError")
            raise cls.PermissionsError(str(err))
        return cls._devices

    def set_target_device(self, device):
        """
        Select the device to work with
        """
        if device is None:
            raise self.BadCall('Must provide device')
        if not self._devices:
            raise self.BadCall('Must call get_devices() first.')
        if device not in self._devices:
            raise self.BadCall('Unknown device')

        self._target = device

    def get_target_device(self):
        """
        Returns the selected device to work with
        """
        return self._target

    def get_state(self):
        """
        Get ADB state
        adb get-state
        """
        return self._output_if_no_error(self.run_cmd('get-state'))

    def get_serialno(self):
        """
        Get serialno from target device
        adb get-serialno
        """
        return self._output_if_no_error(self.run_cmd('get-serialno'))

    def reboot_device(self, mode):
        """
        Reboot the target device
        adb reboot recovery/bootloader
        """

        if mode not in (self.REBOOT_RECOVERY, self.REBOOT_BOOTLOADER):
            raise self.BadCall(
                    "mode must be REBOOT_RECOVERY/REBOOT_BOOTLOADER")
        return self._output_if_no_error(self.run_cmd(
                ["reboot",
                 "%s" % "recovery"
                 if mode == self.REBOOT_RECOVERY
                 else "bootloader"]))

    def set_adb_root(self):
        """
        restarts the adbd daemon with root permissions
        adb root
        """
        return self._output_if_no_error(self.run_cmd('root'))

    def set_system_rw(self):
        """
        Mounts /system as rw
        adb remount
        """
        return self._output_if_no_error(self.run_cmd("remount"))

    def get_remote_file(self, remote, local):
        """
        Pulls a remote file
        adb pull remote local
        """
        output, error = self.run_cmd(['pull', remote, local])

        if error is not None and "bytes in" in error:
            return error

        return output

    def push_local_file(self, local, remote):
        """
        Push a local file
        adb push local remote
        """
        return self._output_if_no_error(self.run_cmd(['push', local, remote]))

    def shell_command(self, cmd):
        """
        Executes a shell command
        adb shell <cmd>

        Returns output and error as tuple.
        """
        return self.run_cmd(['shell', cmd])

    def listen_usb(self):
        """
        Restarts the adbd daemon listening on USB
        adb usb
        """
        return self._output_if_no_error(self.run_cmd("usb"))

    def listen_tcp(self, port=DEFAULT_TCP_PORT):
        """
        Restarts the adbd daemon listening on the specified port
        adb tcpip <port>
        """
        return self._output_if_no_error(self.run_cmd(['tcpip', port]))

    def get_bugreport(self):
        """
        Return all information from the device that should be included in a
        bug report adb bugreport
        """
        return self._output_if_no_error(self.run_cmd("bugreport"))

    def get_jdwp(self):
        """
        List PIDs of processes hosting a JDWP transport
        adb jdwp
        """
        return self._output_if_no_error(self.run_cmd("jdwp"))

    def get_logcat(self, lcfilter=""):
        """
        View device log
        adb logcat <filter>
        """
        return self._output_if_no_error(self.run_cmd(['logcat', lcfilter]))

    def run_emulator(self, cmd=""):
        """
        Run emulator console command
        """
        return self._output_if_no_error(self.run_cmd(['emu', cmd]))

    def connect_remote(self, host=DEFAULT_TCP_HOST, port=DEFAULT_TCP_PORT):
        """
        Connect to a device via TCP/IP
        adb connect host:port
        """
        return self._output_if_no_error(
                self.run_cmd(['connect', "%s:%s" % (host, port)]))

    def disconnect_remote(self, host=DEFAULT_TCP_HOST, port=DEFAULT_TCP_PORT):
        """
        Disconnect from a TCP/IP device
        adb disconnect host:port
        """
        return self._output_if_no_error(
                self.run_cmd(['disconnect', "%s:%s" % (host, port)]))

    def ppp_over_usb(self, tty=None, params=""):
        """
        Run PPP over USB
        adb ppp <tty> <params>
        """
        if tty is None:
            return None

        cmd = ["ppp", tty]
        if params != "":
            cmd += params

        return self._output_if_no_error(self.run_cmd(cmd))

    def sync_directory(self, directory=""):
        """
        Copy host->device only if changed (-l means list but don't copy)
        adb sync <dir>
        """
        return self._output_if_no_error(self.run_cmd(['sync', directory]))

    def forward_socket(self, local=None, remote=None):
        """
        Forward socket connections
        adb forward <local> <remote>
        """
        if local is None or remote is None:
            return None
        return self._output_if_no_error(
                self.run_cmd(['forward', local, remote]))

    def uninstall(self, package=None, keepdata=False):
        """
        Remove this app package from the device
        adb uninstall [-k] package
        """
        if package is None:
            return None

        cmd = 'uninstall '
        if keepdata:
            cmd += '-k '
        cmd += package
        return self._output_if_no_error(
                self.run_cmd(cmd.split()))

    def install(self, fwdlock=False, reinstall=False, sdcard=False,
                pkgapp=None):
        """
        Push this package file to the device and install it
        adb install [-l] [-r] [-s] <file>
        -l -> forward-lock the app
        -r -> reinstall the app, keeping its data
        -s -> install on sdcard instead of internal storage
        """

        if pkgapp is None:
            return None

        cmd = "install "
        if fwdlock:
            cmd += "-l "
        if reinstall:
            cmd += "-r "
        if sdcard:
            cmd += "-s "

        cmd += pkgapp
        return self._output_if_no_error(self.run_cmd(cmd.split()))

    def find_binary(self, name=None):
        """
        Look for a binary file on the device
        """

        output, error = self.run_cmd(['shell', 'which', name])

        if output is None:  # not found
            raise self.BadCall("'%s' was not found" % name)
        elif output[0] == "which: not found":
            # 'which' binary not available
            raise self.InternalError("which binary not found")

        return output
