#!/usr/bin/python3
# this is Python _3_

import os
import re
import shlex
import socket
import subprocess
import sys
import time

import ipaddress
import psutil


from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Device:
    def __init__(self):
        self.data = {
            'hostname': 'unknown',
            'if': {
                'eth0': {
                    'name': '',
                    'addr': '',
                    'state': 'down',
                },
                'wlan0': {
                    'name': '',
                    'addr': '',
                    'state': 'down',
                    'ssid': '',
                    'rssi': 0
                }
            }
        }


    def update(self):
        self.fetchHostname()
        self.fetchInterfaces()


    def fetchHostname(self):
        name = os.uname()[1]
        self.data['hostname'] = name


    def getHostname(self):
        return self.data['hostname']


    def mdnsNameForInterface(self,intf,addr):
        try:
            p = subprocess.run(["/usr/bin/avahi-resolve", "-a", addr], timeout=2, capture_output=True)
            entry = p.stdout.decode('utf-8')
            name = shlex.split(entry)[1]
            return name
        except subprocess.TimeoutExpired:
            return None


    def lookupWifiInfo(self,intf):
        p = subprocess.run(["/usr/sbin/iwconfig", "wlan0"], timeout=1, capture_output=True)
        v = p.stdout.decode('utf-8')

        ssid=""
        rssi=0
        m = re.search('ESSID:\"(.*)\"', v)
        if m is not None:
            ssid = m.group(1)

        m = re.search('Signal level=(.*) dBm', v)
        if m is not None:
            rssi = m.group(1)

        return (ssid,rssi)


    def fetchInterfaces(self):
        interesting_interfaces = [ 'eth0', 'wlan0' ]

        stats = psutil.net_if_stats()
        for intf in stats.keys():
            if not intf in interesting_interfaces:
                continue

            #print("interface {}".format(intf))
            #print(stats[intf])
            #print("  up:{isup} speed:{speed} mtu:{mtu}".format(*stats[intf]))

            self.data['if'][intf]['state'] = "up" if stats[intf].isup else "down"

        addrs = psutil.net_if_addrs()
        for intf in addrs.keys():
            if not intf in interesting_interfaces:
                continue

            #print("interface {}".format(intf))
            for addr in addrs[intf]:
                if addr.family == socket.AF_INET:
                    try:
                        nw = ipaddress.IPv4Network((addr.address, addr.netmask),strict=False)
                        self.data['if'][intf]['addr'] = "{} / {}".format(addr.address, nw.prefixlen)
                        self.data['if'][intf]['name'] = self.mdnsNameForInterface(intf,addr.address)
                        if intf == "wlan0":
                            (ssid,rssi) = self.lookupWifiInfo(intf)
                            self.data['if'][intf]['ssid'] = ssid
                            self.data['if'][intf]['rssi'] = rssi

                    except ValueError:
                        self.data['if'][intf]['state'] = "down"
                        self.data['if'][intf]['addr'] = ""
                        self.data['if'][intf]['name'] = ""


    def getInterfaceInfo(self,intf):
        if intf in self.data['if']:
            return self.data['if'][intf]

        return None






class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow,self).__init__()
        self.device = Device()
        self.counter = 0

        self.args = kwargs

        self.normalButtonStyle = "color: white; background-color: transparent;"
        self.errorButtonStyle = "color: red; background-color: transparent;"

        self.setGeometry(400, 400, 800,400)
        self.setStyleSheet("background-color: #888")

        self.hostnameLabel = QLabel(self)
        self.hostnameLabel.adjustSize()
        self.hostnameLabel.setStyleSheet(self.normalButtonStyle)
        self.hostnameLabel.setAlignment(Qt.AlignCenter)
        self.hostnameLabel.setGeometry(0, 0, 800, 40)

        self.timeLabel = QLabel(self)
        self.timeLabel.setStyleSheet(self.normalButtonStyle)
        self.timeLabel.setAlignment(Qt.AlignLeft)
        self.timeLabel.setGeometry(0, 45, 400, 40)

        self.uptimeLabel = QLabel(self)
        self.uptimeLabel.setStyleSheet(self.normalButtonStyle)
        self.uptimeLabel.setAlignment(Qt.AlignRight)
        self.uptimeLabel.setGeometry(400, 45, 400, 40)

        shutdown_button = QPushButton(self)
        shutdown_button.setText("Quit" if self.args["test_only"] else "Shut Down")
        shutdown_button.adjustSize()
        shutdown_button.clicked.connect(self.quit_called if self.args["test_only"] else self.shutdown_called)
        shutdown_button.move(650, 410)
        shutdown_button.setEnabled(True)

        self.eth0Label = QLabel(self)
        self.eth0Label.setText("Ethernet:")
        self.eth0Label.setStyleSheet("color: white; background-color: transparent;")
        self.eth0Label.setAlignment(Qt.AlignRight)
        self.eth0Label.setGeometry(0, 90, 130, 40)

        self.eth0Hostname = QLabel(self)
        self.eth0Hostname.setStyleSheet(self.normalButtonStyle)
        self.eth0Hostname.setAlignment(Qt.AlignLeft)
        self.eth0Hostname.setGeometry(150, 90, 300, 40)

        self.eth0Address = QLabel(self)
        self.eth0Address.setStyleSheet(self.normalButtonStyle)
        self.eth0Address.setAlignment(Qt.AlignLeft)
        self.eth0Address.setGeometry(475, 90, 300, 40)

        self.wifiLabel = QLabel(self)
        self.wifiLabel.setText("WiFi:")
        self.wifiLabel.setStyleSheet("color: white; background-color: transparent;")
        self.wifiLabel.setAlignment(Qt.AlignRight)
        self.wifiLabel.setGeometry(0, 135, 130, 40)

        self.wlan0Hostname = QLabel(self)
        self.wlan0Hostname.setStyleSheet(self.normalButtonStyle)
        self.wlan0Hostname.setAlignment(Qt.AlignLeft)
        self.wlan0Hostname.setGeometry(150, 135, 300, 40)

        self.wlan0Address = QLabel(self)
        self.wlan0Address.setStyleSheet(self.normalButtonStyle)
        self.wlan0Address.setAlignment(Qt.AlignLeft)
        self.wlan0Address.setGeometry(475, 135, 300, 40)

        self.wlan0SSID = QLabel(self)
        self.wlan0SSID.setStyleSheet(self.normalButtonStyle)
        self.wlan0SSID.setAlignment(Qt.AlignLeft)
        self.wlan0SSID.setGeometry(150, 180, 300, 40)

        timer = QTimer(self)
        timer.timeout.connect(self.timerTick)
        timer.start(1000)


    def updateUI(self):
        self.hostnameLabel.setText(self.device.getHostname())
        self.timeLabel.setText( time.asctime() )
        self.uptimeLabel.setText( str(self.counter) )

        eth0 = self.device.getInterfaceInfo('eth0')
        if eth0 is not None:
            #print("Update: {}".format(eth0))
            if eth0['state'] == "up":
                self.eth0Label.setStyleSheet(self.normalButtonStyle)
                self.eth0Address.setText( str(eth0['addr']) )
                self.eth0Hostname.setText( str(eth0['name']) )
                self.eth0Address.setVisible(True)
                self.eth0Hostname.setVisible(True)
            else:
                self.eth0Label.setStyleSheet(self.errorButtonStyle)
                self.eth0Address.setVisible(False)
                self.eth0Hostname.setVisible(False)

        wlan0 = self.device.getInterfaceInfo('wlan0')
        if wlan0 is not None:
            #print("Update: {}".format(wlan0))
            if wlan0['state'] == "up":
                self.wifiLabel.setStyleSheet(self.normalButtonStyle)
                self.wlan0Address.setVisible(True)
                self.wlan0Hostname.setVisible(True)
                self.wlan0SSID.setVisible(True)
                self.wlan0Address.setText( str(wlan0['addr']) )
                self.wlan0Hostname.setText( str(wlan0['name']) )
                self.wlan0SSID.setText( wlan0['ssid'] )
            else:
                self.wifiLabel.setStyleSheet(self.errorButtonStyle)
                self.wlan0Address.setVisible(False)
                self.wlan0Hostname.setVisible(False)
                self.wlan0SSID.setVisible(False)






    def shutdown_called(self):
        print("Shutdown called")
        sys.exit(0)
        os.system("sudo /usr/sbin/shutdown -h now")

    def quit_called(self):
        print("Quit called")
        sys.exit(0)

    def timerTick(self):
        if self.counter % 5 == 0:
            self.device.update()

        self.counter += 1
        self.updateUI()






class App(object):
    def __init__(self, args):
        self.test = False
        self.args = args
        self.test_only = False

        skip_fb_init = False

        for arg in args:
            if arg == "-nofb":
                skip_fb_init = True
            if arg == "-test":
                self.test_only = True

        if not skip_fb_init:
            self.set_for_framebuffer()


    def set_for_framebuffer(self):
        os.environ['QT_QPA_PLATFORM'] = "linuxfb:size=800x480:mmsize=155x86"
        os.environ['QT_QPA_FB_HIDECURSOR'] = "1"

    def run(self):
        app = QApplication(sys.argv)

        window = MainWindow( test_only=self.test_only )
        window.show()

        app.exec_()

    def closeUpShop(self):
        os.system("dd if=/dev/zero of=/dev/fb0")


if __name__=="__main__":
    app = App(sys.argv)
    app.run()
    app.closeUpShop()

    #d = Device()
    #x = d.getInterfaces()
