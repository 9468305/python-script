#! $ANDROID_HOME/tools/bin monkeyrunner
# -*- coding: utf-8 -*-
'''uiparser'''

import os
import sys
import subprocess
import datetime
import logging
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice, MonkeyImage #pylint: disable=import-error

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger(__name__).addHandler(NullHandler())
logging.basicConfig(level=logging.DEBUG)

SHORT = 1
MIDDLE = 5
LONG = 15

ADB = os.path.join(os.environ['ANDROID_HOME'], 'platform-tools', 'adb')

# Example of Ctrip Android Apk
TARGET_PACKAGE = 'ctrip.android.view'
LAUNCH_ACTIVITY = 'ctrip.business.splash.CtripSplashActivity'
HOME_ACTIVITY = 'ctrip.android.publicproduct.home.view.CtripHomeActivity'
FLIGHT_ACTIVITY = 'ctrip.android.flight.view.inland.FlightInquireActivity'
START_COMPONENT = TARGET_PACKAGE + '/' + LAUNCH_ACTIVITY

DEVICE_DIR = '/sdcard/uiparser/'
HOST_DIR = './'


def capture(device, index):
    ''''''
    _dumpXML = DEVICE_DIR + index + '.xml'
    _localXML = HOST_DIR + index + '.xml'
    _localImage = HOST_DIR + index + '.png'

    _shell = [ADB, 'shell', 'uiautomator', 'dump', _dumpXML]
    logging.debug(datetime.datetime.now())
    subprocess.call(_shell) # Stupid uiautomator, always failed here!
    logging.debug(datetime.datetime.now())
    #MonkeyRunner.sleep(MIDDLE)

    _shell = [ADB, 'pull', _dumpXML, _localXML]
    subprocess.call(_shell)

    _image = device.takeSnapshot()
    _image.writeToFile(_localImage, 'png')


def uiparser():
    '''Main Entry'''
    device = MonkeyRunner.waitForConnection(MIDDLE)

    _shell = [ADB, 'shell', 'rm', '-rf', DEVICE_DIR]
    subprocess.call(_shell)

    _shell = [ADB, 'shell', 'mkdir', '-p', DEVICE_DIR]
    subprocess.call(_shell)

    device.startActivity(component=START_COMPONENT)
    MonkeyRunner.sleep(MIDDLE)

    capture(device, str(0))


if __name__ == "__main__":
    # MonkeyRunner Jython version is 2.5.3 (Outdated!)
    logging.info(sys.version)
    uiparser()
