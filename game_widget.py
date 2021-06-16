#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implemented by Michael Meckl.
"""

import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QPaintEvent, QColor
from enum import Enum


Direction = Enum("Direction", "UP DOWN")
Velocity = Enum("Velocity", "NORMAL FAST")


# noinspection PyAttributeOutsideInit
class GameWindow(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super(GameWindow, self).__init__(*args, **kwargs)
        # set game window background color and border
        self.setStyleSheet("border: 1px solid black; background-color: rgb(227, 219, 155);")
        # necessary to set fixed size as otherwise we can't know the window dimensions before the first draw!
        self.setFixedSize(700, 350)

        # calculate static positions and values
        self.__width, self.__height = self.width(), self.height()
        self.inset = 120
        self.road_height = 70
        self.player_width = 20
        self.player_height = self.road_height / 2

        self.player_start_xPos = 5
        self.player_yPos_top_lane = self.inset + self.road_height / 4
        self.player_yPos_bottom_lane = self.inset + self.road_height + self.road_height / 4

        self._setup_roads()
        self._setup_levels()

    def _setup_roads(self):
        y_middle, y_bottom = self.inset + self.road_height, self.inset + self.road_height * 2
        self.sideline_top = (0, self.inset, self.__width, self.inset)
        self.middle_line = (0, y_middle, self.__width, y_middle)
        self.sideline_bottom = (0, y_bottom, self.__width, y_bottom)

    def _setup_levels(self):
        self.obstacle_radius = self.road_height / 2 - 5
        self.obstacle_top_row_y = int(self.inset + self.obstacle_radius + 5)
        self.obstacle_bottom_row_y = int(self.obstacle_top_row_y + self.road_height)

        self.collectible_radius = 10
        self.collectible_top_row_y = int(self.inset + self.road_height / 2)
        self.collectible_bottom_row_y = int(self.collectible_top_row_y + self.road_height)

        # this dict defines the x-/y-positions of all collectibles and obstacles for each level
        self.levels = {
            1: {
                "obstacles": [(self.__width - 300, self.obstacle_top_row_y)],
                "collectibles": [(self.__width - 300, self.collectible_bottom_row_y),
                                 (self.__width - 130, self.collectible_top_row_y),
                                 (self.__width - 500, self.collectible_top_row_y),
                                 (self.__width - 450, self.collectible_bottom_row_y)]
            },
            2: {
                "obstacles": [(self.__width - 480, self.obstacle_top_row_y),
                              (self.__width - 270, self.obstacle_bottom_row_y)],
                "collectibles": [(self.__width - 560, self.collectible_top_row_y),
                                 (self.__width - 430, self.collectible_top_row_y),
                                 (self.__width - 180, self.collectible_bottom_row_y)]
            },
            3: {
                "obstacles": [(self.__width - 520, self.obstacle_top_row_y),
                              (self.__width - 385, self.obstacle_bottom_row_y),
                              (self.__width - 250, self.obstacle_top_row_y),
                              (self.__width - 145, self.obstacle_bottom_row_y)],
                "collectibles": [(self.__width - 390, self.collectible_top_row_y),
                                 (self.__width - 205, self.collectible_top_row_y),
                                 (self.__width - 430, self.collectible_bottom_row_y),
                                 (self.__width - 75, self.collectible_bottom_row_y)]
            }
        }

    def start(self, level_finished_callback, points_changed_callback):
        # set callbacks to notify the ui outside the game window
        self.__level_callback = level_finished_callback
        self.__points_callback = points_changed_callback

        # init the first level
        self._set_initial_values()
        self._init_first_level()

    def _set_initial_values(self):
        self.current_level = 1
        self.current_points = 0

        self.at_top_lane = True
        self.player_xPos, self.player_yPos = self.player_start_xPos, self.player_yPos_top_lane

    def _init_first_level(self):
        self.current_obstacles = []
        self.current_collectibles = []
        self._set_values_for_level(level_index=1)

    def _set_values_for_level(self, level_index: int):
        # set the obstacles and collectibles for the level with the given index
        try:
            level = self.levels[level_index]
        except IndexError:
            sys.stderr.write(f"Tried to access level that doesn't exist (index={level_index}!")
            return
        self.current_obstacles = level.get("obstacles")
        self.current_collectibles = level.get("collectibles")

    def move_character_forward(self, velocity: Velocity):
        if velocity == Velocity.NORMAL:
            self.player_xPos += self.player_width / 2
        elif velocity == Velocity.FAST:
            self.player_xPos += self.player_width

        self.repaint()  # update is not enough, the repaint has to happen immediately!

        if self.player_xPos > self.__width:
            print("Level finished!")
            self._level_up()
        else:
            # check if player collided with an obstacle or a collectible
            self._check_player_collision()

    def switch_lane(self, direction: Direction):
        if direction == Direction.UP and not self.at_top_lane:
            # move to the top lane
            self.at_top_lane = True
            self.player_yPos = self.player_yPos_top_lane

            self._check_player_collision()
        elif direction == Direction.DOWN and self.at_top_lane:
            # move to the bottom lane
            self.at_top_lane = False
            self.player_yPos = self.player_yPos_bottom_lane

            self._check_player_collision()
        else:
            print("Switching lane did not work! Player is already at this lane!")

        self.repaint()

    def _level_up(self):
        self.current_level += 1
        self.current_points += 100

        # load next level if there is one
        self._load_next_level()
        # and notify callbacks
        self.__level_callback(self.current_level)
        self.__points_callback(self.current_points)

    def _load_next_level(self):
        if self.current_level > len(self.levels):
            # start at the first level again when no others left
            self.current_level = 1

        self._set_values_for_level(level_index=self.current_level)
        self.player_xPos = self.player_start_xPos

    def __check_overlap(self, object_x, object_y, object_radius):
        # calculate the interesting x and y position of the player and the other object
        player_right_edge = self.player_xPos + self.player_width/2
        player_left_edge = self.player_xPos - self.player_width/2
        object_right = object_x + object_radius
        object_left = object_x - object_radius
        player_lane = "top" if self.at_top_lane else "bottom"
        object_lane = "top" if object_y == self.collectible_top_row_y else "bottom"

        # check if the the player left and right edges are between the leftmost and rightmost x-pos of the other object
        # and if they are on the same lane
        if player_right_edge > object_left and player_left_edge <= object_right and player_lane == object_lane:
            return True
        else:
            return False

    def _check_player_collision(self):
        self.__check_collectible_hit()
        self.__check_obstacle_hit()

    def __check_obstacle_hit(self):
        for obstacle in self.current_obstacles:
            if self.__check_overlap(obstacle[0], obstacle[1], self.obstacle_radius):
                # if the player and this obstacle overlap, remove points and update ui via callback;
                # also reset the x-pos of the player to the start of level
                new_points = self.current_points - 50
                self.current_points = new_points if new_points >= 0 else 0  # make sure we don't have negative points
                self.__points_callback(self.current_points)

                self.player_xPos = self.player_start_xPos
                break  # if one hit occurred we don't need to check the rest anymore

    def __check_collectible_hit(self):
        for collectible in self.current_collectibles:
            if self.__check_overlap(collectible[0], collectible[1], self.collectible_radius):
                # if the player and this collectible overlap, add points and update ui via callback;
                # also remove this collectible from the current collectibles so it won't be drawn on next paintEvent
                self.current_points += 20
                self.__points_callback(self.current_points)

                self.current_collectibles.remove(collectible)
                break  # the player can only collect one at a time, so checking the others too would be useless

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter()
        painter.begin(self)
        # painter.setRenderHints(painter.Antialiasing)

        # draw all parts of the game; order does matter!
        self._draw_roads(painter)
        self._draw_obstacles(painter)
        self._draw_collectibles(painter)
        self._draw_player(painter)

        painter.end()

    def _draw_roads(self, painter: QPainter):
        # fill background of road first
        painter.setBrush(QBrush(QColor(186, 186, 186), Qt.SolidPattern))
        painter.drawRect(0, self.inset, self.__width, self.road_height * 2)

        # draw road lines
        pen = QPen(Qt.black, 3, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(*self.sideline_top)
        painter.drawLine(*self.sideline_bottom)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(*self.middle_line)

    def _draw_collectibles(self, painter: QPainter):
        painter.setPen(QPen(Qt.NoPen))  # set to NoPen so no outline will be drawn
        painter.setBrush(QBrush(Qt.yellow, Qt.SolidPattern))
        for collectible_pos in self.current_collectibles:
            painter.drawEllipse(QtCore.QPoint(*collectible_pos), self.collectible_radius, self.collectible_radius)

    def _draw_obstacles(self, painter: QPainter):
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))
        for obstacle_pos in self.current_obstacles:
            painter.drawEllipse(QtCore.QPoint(*obstacle_pos), self.obstacle_radius, self.obstacle_radius)

    def _draw_player(self, painter: QPainter):
        # draw body
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(Qt.darkGreen, Qt.SolidPattern))
        painter.drawRect(self.player_xPos, self.player_yPos, self.player_width, self.player_height)

        # draw eyes and mouth afterwards
        painter.setPen(QPen(Qt.black, 4, Qt.SolidLine))
        painter.drawPoint(self.player_xPos + self.player_width - 5, self.player_yPos + 5)
        painter.drawLine(self.player_xPos + self.player_width - 8, self.player_yPos + 10,
                         self.player_xPos + self.player_width, self.player_yPos + 10)
