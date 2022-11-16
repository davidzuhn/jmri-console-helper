#!/usr/bin/python3
# this is Python _3_

import os
import sys

import ipaddress
import psutil
import netifaces

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Device:
    def __init__(self):
        self.data = {
            'hostname': 'unknown',
            'if': {
                'eth0': {
                    'name': 'unknown',
                    'addr': '172.29.181.32 / 24',
                    'state': 'down'
                },
                'wlan0': {
                    'name': 'unknown',
                    'addr': '192.168.22.21 / 24',
                    'state': 'down',
                    'ssid': 'Blue Knobby'
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

    def getAddressForInterface(self,ifname):
        addr = netifaces.ifaddresses(ifname)
        for a in addr[netifaces.AF_INET]:
            spec = "{addr}/{netmask}".format(**a)
            try:
                nw = ipaddress.IPv4Network((a['addr'],a['netmask']),strict=False)
                result = "{} / {}".format(a['addr'], nw.prefixlen)

                name = "something.local"

                return (result, name, a['addr'], a['netmask'])
            except ValueError:
                return None


    def fetchInterfaces(self):
        interface = psutil.net_if_stats()
        for i in interface.keys():
            pass
            #print("interface {}".format(i))
            #print(interface[i])
            #print("  up:{isup} speed:{speed} mtu:{mtu}".format(*interface[i]))

        interesting_interfaces = [ 'eth0', 'wlan0' ]

        ifs = netifaces.interfaces()
        for i in ifs:
            if not i in interesting_interfaces:
                continue

            (addr,name,_,_) = self.getAddressForInterface(i)

            if addr is not None:
                self.data['if'][i]['addr'] = addr
                self.data['if'][i]['name'] = name


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

        self.setGeometry(400, 400, 800,400)
        self.setStyleSheet("background-color: #888")

        self.hostnameLabel = QLabel(self)
        self.hostnameLabel.setText(self.device.getHostname())
        self.hostnameLabel.adjustSize()
        #label.move(200, 40)
        #label.resize(100,40)
        self.hostnameLabel.setStyleSheet("color: white; background-color: transparent; border: 1px solid black;")
        self.hostnameLabel.setAlignment(Qt.AlignCenter)
        self.hostnameLabel.setGeometry(0, 0, 800, 40)


        #logo_image = QPixmap('/home/zoo/blueknobby.png')
        #logo = QLabel(self)
        #logo.setPixmap(logo_image)
        #logo.setAlignment(Qt.AlignCenter)
        #logo.adjustSize()
        #logo.setGeometry(225, 25, 350, 50)

        shutdown_button = QPushButton(self)
        shutdown_button.setText("Quit" if self.args["test_only"] else "Shut Down")
        shutdown_button.adjustSize()
        shutdown_button.clicked.connect(self.quit_called if self.args["test_only"] else self.shutdown_called)
        shutdown_button.move(650, 410)
        shutdown_button.setEnabled(True)

        eth0Label = QLabel(self)
        eth0Label.setText("Ethernet:")
        eth0Label.setStyleSheet("color: white; background-color: transparent; border: 1px solid black;")
        eth0Label.setAlignment(Qt.AlignRight)
        eth0Label.setGeometry(0, 90, 130, 40)

        self.eth0Hostname = QLabel(self)
        self.eth0Hostname.setText("eth0Hostname")
        self.eth0Hostname.setStyleSheet("color: white; background-color: transparent; border: 1px solid black;")
        self.eth0Hostname.setAlignment(Qt.AlignLeft)
        self.eth0Hostname.setGeometry(150, 90, 300, 40)

        self.eth0Address = QLabel(self)
        self.eth0Address.setText("172.29.181.35 / 24")
        self.eth0Address.setStyleSheet("color: white; background-color: transparent; border: 1px solid black;")
        self.eth0Address.setAlignment(Qt.AlignLeft)
        self.eth0Address.setGeometry(475, 90, 300, 40)

        wifiLabel = QLabel(self)
        wifiLabel.setText("WiFi:")
        wifiLabel.setStyleSheet("color: white; background-color: transparent; border: 1px solid black;")
        wifiLabel.setAlignment(Qt.AlignRight)
        wifiLabel.setGeometry(0, 135, 130, 40)

        self.wlan0Hostname = QLabel(self)
        self.wlan0Hostname.setText("wlan0Hostname")
        self.wlan0Hostname.setStyleSheet("color: white; background-color: transparent; border: 1px solid black;")
        self.wlan0Hostname.setAlignment(Qt.AlignLeft)
        self.wlan0Hostname.setGeometry(150, 135, 300, 40)

        self.wlan0Address = QLabel(self)
        self.wlan0Address.setText("192.168.22.4 / 24")
        self.wlan0Address.setStyleSheet("color: white; background-color: transparent; border: 1px solid black;")
        self.wlan0Address.setAlignment(Qt.AlignLeft)
        self.wlan0Address.setGeometry(475, 135, 300, 40)

        self.wlan0SSID = QLabel(self)
        self.wlan0SSID.setText("myownlittleidaho")
        self.wlan0SSID.setStyleSheet("color: white; background-color: transparent; border: 1px solid black;")
        self.wlan0SSID.setAlignment(Qt.AlignLeft)
        self.wlan0SSID.setGeometry(150, 180, 300, 40)


        self.counterLabel = QLabel(self)
        self.counterLabel.setText( str(self.counter) )
        self.counterLabel.setStyleSheet("color: white; background-color: transparent; border: 1px solid black;")
        self.counterLabel.setAlignment(Qt.AlignCenter)
        self.counterLabel.setGeometry(0, 45, 800, 40)

        timer = QTimer(self)
        timer.timeout.connect(self.timerTick)
        timer.start(1000)

    def updateUI(self):
        self.hostnameLabel.setText(self.device.getHostname())
        self.counterLabel.setText (str(self.counter))

        eth0 = self.device.getInterfaceInfo('eth0')
        if eth0 is not None:
            print("Update: {}".format(eth0))
            self.eth0Address.setText( str(eth0['addr']) )
            self.eth0Hostname.setText( str(eth0['name']) )



    def shutdown_called(self):
        print("Shutdown called")
        sys.exit(0)
        os.system("sudo /usr/sbin/shutdown -h now")

    def quit_called(self):
        print("Quit called")
        sys.exit(0)

    def timerTick(self):
        self.counter += 1
        self.device.update()
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
