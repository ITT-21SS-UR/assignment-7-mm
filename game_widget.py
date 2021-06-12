#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implemented by Michael Meckl.
"""

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QPaintEvent
from enum import Enum


Direction = Enum("Direction", "UP DOWN")


class GameWindow(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super(GameWindow, self).__init__(*args, **kwargs)
        self.setStyleSheet("border: 1px solid black; background-color: rgb(211, 227, 248);")
        self.setFixedSize(700, 350)  # necessary to set fixed size as otherwise we can't know height and width before the first draw!

        # print("At start:", self.width(), self.height())
        self.__width, self.__height = self.width(), self.height()
        self.inset = 120
        self.road_height = 70
        self.player_width = 20
        self.player_height = self.road_height / 2

        self.player_start_xPos = 5
        self.player_yPos_top_lane = self.inset + self.road_height / 4
        self.player_yPos_bottom_lane = self.inset + self.road_height + self.road_height / 4
        self.player_velocity = 0.0

        self.set_initial_values()

    def set_initial_values(self):
        # TODO draw them instead of giving to main class and setting in ui?
        self.current_level = 1
        self.current_points = 0

        self.current_obstacles = []

        self.at_top_lane = True
        self.player_xPos, self.player_yPos = self.player_start_xPos, self.player_yPos_top_lane

    def start(self):
        print("Game Window started")

    def update_player_pos(self, new_x, new_y):
        self.player_xPos, self.player_yPos = new_x, new_y

    def update_player_velocity(self, new_vel):
        self.player_velocity = new_vel

    def move_character_forward(self):
        self.player_xPos += self.player_width / 2
        if self.player_xPos > self.__width:
            print("Level finished!")
            self.current_level += 1
            self.current_points += 100
            self.load_next_level()

    def load_next_level(self):
        # TODO get obstacle positions for this level! define all at the start in a dict per level!
        self.player_xPos = self.player_start_xPos
        # self.repaint()
        self.update()

    def get_player_bounds(self):
        return self.player_xPos, self.player_yPos, self.player_xPos + self.player_width, self.player_yPos + self.player_height

    def check_obstacle_hit(self):
        pass  # TODO

    def check_collectible_hit(self):
        pass  # TODO

    def switch_lane(self, direction: Direction):
        if direction == Direction.UP and not self.at_top_lane:
            self.at_top_lane = True
            self.player_yPos = self.player_yPos_top_lane
        elif direction == Direction.DOWN and self.at_top_lane:
            self.at_top_lane = False
            self.player_yPos = self.player_yPos_bottom_lane
        else:
            print("Switching lane not working! Already at this lane!")

        # self.repaint()
        self.update()

    def paintEvent(self, event: QPaintEvent):
        # super().paintEvent(event)
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHints(painter.Antialiasing)

        self.draw_roads(painter)
        self.draw_obstacles(painter)
        self.draw_collectibles(painter)
        self.draw_player(painter)

        painter.end()

    def draw_roads(self, painter: QPainter):
        y1, y2, y3 = self.inset, self.inset + self.road_height, self.inset + self.road_height * 2
        sideline_top = (0, y1, self.width(), y1)
        middle_line = (0, y2, self.width(), y2)
        sideline_bottom = (0, y3, self.width(), y3)

        pen = QPen(Qt.black, 3, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(*sideline_top)
        painter.drawLine(*sideline_bottom)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(*middle_line)

    def draw_collectibles(self, painter: QPainter):
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(Qt.yellow, Qt.SolidPattern))
        painter.drawEllipse(self.width() - 300, int(self.inset + self.road_height / 3), 20, 20)

    def draw_obstacles(self, painter: QPainter):
        pen = QPen(Qt.NoPen)  # set to NoPen so no outline will be drawn
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))

        circle_radius = self.road_height / 2 - 5
        painter.drawEllipse(QtCore.QPoint(self.width() - 300, int(self.inset + self.road_height + circle_radius + 5)), circle_radius, circle_radius)

    def draw_player(self, painter: QPainter):
        # body
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(Qt.darkGreen, Qt.SolidPattern))
        painter.drawRect(self.player_xPos, self.player_yPos, self.player_width, self.player_height)
        # eyes and mouth
        painter.setPen(QPen(Qt.black, 4, Qt.SolidLine))
        painter.drawPoint(self.player_xPos + self.player_width - 5, self.player_yPos + 5)
        painter.drawLine(self.player_xPos + self.player_width - 8, self.player_yPos + 10, self.player_xPos + self.player_width, self.player_yPos + 10)
