#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implemented by Michael Meckl.
"""

import sys
from argparse import ArgumentParser
from DIPPID import SensorUDP
from PyQt5 import QtWidgets, QtCore, uic, QtGui
from PyQt5.QtGui import QPainter


class DippidGame(QtWidgets.QWidget):

    ALL_CAPABILITIES = ["accelerometer", "gyroscope", "gravity", "button_1", "button_2", "button_3", "button_4"]

    def __init__(self, port=5700):
        super(DippidGame, self).__init__()
        self.game_started = False
        self.sensor = SensorUDP(port)

        self.ui = uic.loadUi("dippid_game.ui", self)
        self._show_introduction()

    def _show_introduction(self):
        self.ui.stackedWidget.setCurrentIndex(0)

        # TODO would be better to check this in an infinite loop in the background? or at least until connected! maybe don't even allow start game?
        self._check_connected_status()

        # the callbacks need to be registered AFTER checking connected status, otherwise we can't be sure about the
        # connected status as they register themselves as capabilities as well
        # TODO only register them AFTER starting the game?
        self._register_sensor_callbacks()

        self.ui.btn_start_game.setFocusPolicy(QtCore.Qt.NoFocus)  # prevent auto-focus of the start button
        self.ui.btn_start_game.clicked.connect(self._show_game)

    def _register_sensor_callbacks(self):
        self.sensor.register_callback('button_1', self._handle_button_press)  # TODO can button be useful as well?
        self.sensor.register_callback('accelerometer', self._handle_movement)
        self.sensor.register_callback('gravity', self._handle_position_change)

    def _handle_movement(self, data):
        # the mobile device was accelerated in some direction!
        print("the mobile device was accelerated in some direction!")
        print(data)  #TODO

    def _handle_position_change(self, data):
        # the mobile device changed it's position!
        print("the mobile device changed it's position!")
        print(data)  #TODO

    def _handle_button_press(self, data):
        try:
            if int(data) == 0:
                print('button released')
            else:
                print('button pressed')
        except Exception as e:
            sys.stderr.write(f"Something went wrong when trying to cast button data: {e}")

    def _check_connected_status(self):
        if self._is_connected():
            self.ui.connected_status.setStyleSheet("QLabel { font-weight: bold; color : green;}")
            self.ui.connected_status.setText("Connected")
        else:
            self.ui.connected_status.setStyleSheet("QLabel { font-weight: bold; color : red;}")
            self.ui.connected_status.setText("Not connected")

    def _is_connected(self):
        # check if all capabilities have been registered (if all work the sensor is obviously sending data)
        capabilities_ready = all(self.sensor.has_capability(capability) for capability in DippidGame.ALL_CAPABILITIES)
        return True if capabilities_ready else False

    def _show_game(self):
        index = self.ui.stackedWidget.currentIndex() + 1
        # switch widget index to the element in the stack at the given index (i.e. move to this page)
        self.ui.stackedWidget.setCurrentIndex(index)
        # current_widget = self.ui.stackedWidget.currentWidget()

        # TODO press a start button / key or immediately start game when moving device?
        self._start_game()

    def _start_game(self):
        self.game_started = True

        print('capabilities: ', self.sensor.get_capabilities())
        if self.sensor.has_capability("accelerometer"):
            print("accelerometer x-val:", self.sensor.get_value("accelerometer")['x'])

    def onPaintEvent(self, painter: QPainter):
        pass

    # def closeEvent(self, event: QtGui.QCloseEvent):
    #     self.sensor.disconnect()  # stop sensor before closing!
    #     event.accept()


def main():
    # parse command line input and print out some helpful information
    parser = ArgumentParser(description="A small game that can be played with mobile phone movement recognized via the"
                                        "DIPPID protocol.")
    parser.add_argument("-p", "--port", help="The port on which the mobile device sends its data via DIPPID", type=int,
                        default=5700, required=False)
    args = parser.parse_args()
    port = args.port

    app = QtWidgets.QApplication(sys.argv)
    dippid_game = DippidGame(port=port)
    dippid_game.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
