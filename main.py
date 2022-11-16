#!/usr/bin/python3

# this is Python _3_

#cow

import os
import sys

import ipaddress
import psutil
import netifaces

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Device:
    def getHostname(self):
        name = os.uname()[1]
        return name


    def getAddressForInterface(self,ifname):
        addr = netifaces.ifaddresses(ifname)
        for a in addr[netifaces.AF_INET]:
            spec = "{addr}/{netmask}".format(**a)
            try:
                nw = ipaddress.IPv4Network((a['addr'],a['netmask']),strict=False)
                result = "{} / {}".format(a['addr'], nw.prefixlen)

                return result
            except ValueError:
                return None



    def getInterfaces(self):
        interface = psutil.net_if_stats()
        for i in interface.keys():
            print("interface {}".format(i))
            print(interface[i])
            #print("  up:{isup} speed:{speed} mtu:{mtu}".format(*interface[i]))

        interesting_interfaces = [ 'eth0', 'wlan0' ]

        ifs = netifaces.interfaces()
        for i in ifs:
            if not i in interesting_interfaces:
                continue

            addr = self.getAddressForInterface(i)
            if addr is not None:
                print("interface {} => {}".format(i, addr))




class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow,self).__init__()
        self.device = Device()
        self.counter = 0

        self.args = kwargs

        self.setGeometry(400, 400, 800,400)
        self.setStyleSheet("background-color: #888")

        label = QLabel(self)
        label.setText(self.device.getHostname())
        label.adjustSize()
        #label.move(200, 40)
        #label.resize(100,40)
        label.setStyleSheet("color: white; background-color: transparent; border: 1px solid black;")
        label.setAlignment(Qt.AlignCenter)
        label.setGeometry(0, 0, 800, 40)


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
        shutdown_button.move(620, 410)
        shutdown_button.setEnabled(True)
        shutdown_button.setStyleSheet("border: 1px solid black;")

        timer = QTimer(self)
        timer.timeout.connect(self.timerTick)
        timer.start(1000)

        self.counterLabel = QLabel(self)
        self.counterLabel.setText( str(self.counter) )
        self.counterLabel.setStyleSheet("color: white; background-color: transparent; border: 1px solid black;")
        self.counterLabel.setAlignment(Qt.AlignCenter)
        self.counterLabel.setGeometry(0, 45, 800, 40)

        #self.setCentralWidget(label)

    def shutdown_called(self):
        print("Shutdown called")
        sys.exit(0)
        os.system("sudo /usr/sbin/shutdown -h now")

    def quit_called(self):
        print("Quit called")
        sys.exit(0)

    def timerTick(self):
        print("tick")
        self.counter += 1
        self.counterLabel.setText (str(self.counter))






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
        pass
        #os.system("dd if=/dev/zero of=/dev/fb0")


if __name__=="__main__":
    #app = App(sys.argv)
    #app.run()
    #app.closeUpShop()

    d = Device()
    x = d.getInterfaces()
