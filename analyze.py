#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implemented by Michael Meckl.
"""

import sys
import numpy as np
import math
from argparse import ArgumentParser
# import pyqtgraph.examples
from pyqtgraph.flowchart import Flowchart, Node
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from DIPPID_pyqtnode import DIPPIDNode, BufferNode


class LogNode(Node):
    """
    Logs the data provided by the input terminal to stdout.
    """
    nodeName = 'LogNode'  # Node type name that will appear to the user.

    def __init__(self, name):
        terminals = {
            'accelX': {'io': 'in'},
            'accelY': {'io': 'in'},
            'accelZ': {'io': 'in'},
            'rotation': {'io': 'in'}
        }
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        print(f"Log:\n"
              f"AccelerationX: {kwds['accelX'][0]}\n"
              f"AccelerationY: {kwds['accelY'][0]}\n"
              f"AccelerationZ: {kwds['accelZ'][0]}\n"
              f"RotationVector: {kwds['rotation']}\n")


class NormalVectorNode(Node):
    """
    Accepts accelerometer values on its two input terminals.
    Calculates the rotation around one axis from the accelerometer values of the other two axes by calculating the
    normal vector of the plane spanned by the two input vectors and outputs a vector.
    """
    nodeName = 'NormalVectorNode'

    def __init__(self, name):
        terminals = {
            'accel1': {'io': 'in'},
            'accel2': {'io': 'in'},
            'rotation_vector': {'io': 'out'},
        }
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        # kwds will have one keyword argument per input terminal.
        accel1 = kwds["accel1"][0]
        accel2 = kwds["accel2"][0]
        # vector1 = np.array([accel1, 0, 0])
        # vector2 = np.array([0, 0, accel2])
        # normal_vector = np.cross(vector1, vector2)

        self.rotation_vector = np.array([(0, 0), (accel1, accel2)])

        # v_3 = accel1 / np.sqrt(accel1**2 + accel2**2)
        # math.degrees(math.acos(v_3))

        # formel based on this post: https://math.stackexchange.com/questions/74204/find-angle-between-two-points-respective-to-horizontal-axis
        self.rotation = np.degrees(np.arctan2([accel2], [accel1]))

        return {'rotation': self.rotation_vector}

    def get_rotation_in_degrees(self):
        return self.rotation


# noinspection PyAttributeOutsideInit
class FlowChart:
    def __init__(self, layout, port=5700):
        self.layout = layout
        self.port = port

        # Create an empty flowchart with a single input and output
        self.fc = Flowchart(terminals={})
        w = self.fc.widget()
        # self.layout.addWidget(fc.widget(), 0, 0, 2, 1)
        self.layout.addWidget(w, 0, 0, 2, 1)
        
        self.create_plot_widgets()
        self.set_plot_widgets()
        self.create_nodes()
        self.connect_node_terminals()

    def create_plot_widgets(self):
        # create one plot widget for each axis below each other in the left column
        self.pw1 = pg.PlotWidget()
        self.layout.addWidget(self.pw1, 0, 1)
        self.pw1.setYRange(0, 1)
        self.pw1.setTitle("X-Acceleration")
    
        self.pw2 = pg.PlotWidget()
        self.layout.addWidget(self.pw2, 1, 1)
        self.pw2.setYRange(0, 1)
        self.pw2.setTitle("Y-Acceleration")
    
        self.pw3 = pg.PlotWidget()
        self.layout.addWidget(self.pw3, 2, 1)
        self.pw3.setYRange(0, 1)
        self.pw3.setTitle("Z-Acceleration")
    
        # create a plot widget for the normalvector node
        self.pw4 = pg.PlotWidget()
        self.layout.addWidget(self.pw4, 0, 2, 3, -1)  # make the last plot fill the entire right column
        self.pw4.setXRange(-1, 1)
        self.pw4.setYRange(-1, 1)
        self.pw4.setTitle("Rotation")
        
    def set_plot_widgets(self):
        self.pw1Node = self.fc.createNode('PlotWidget', pos=(300, -150))
        self.pw1Node.setPlot(self.pw1)
        self.pw2Node = self.fc.createNode('PlotWidget', pos=(300, -50))
        self.pw2Node.setPlot(self.pw2)
        self.pw3Node = self.fc.createNode('PlotWidget', pos=(300, 150))
        self.pw3Node.setPlot(self.pw3)
        self.pw4Node = self.fc.createNode('PlotWidget', pos=(300, 200))
        self.pw4Node.setPlot(self.pw4)
    
    def create_nodes(self):
        # create the dippid node and set the provided port automatically
        self.dippidNode = self.fc.createNode("DIPPID", pos=(0, 0))
        self.dippidNode.set_connection_port(self.port)
        
        # create buffer nodes for each axis
        self.bufferNodeX = self.fc.createNode('Buffer', pos=(150, -150))
        self.bufferNodeY = self.fc.createNode('Buffer', pos=(150, 0))
        self.bufferNodeZ = self.fc.createNode('Buffer', pos=(150, 150))
        
        # create the custom nodes
        self.normalVectorNode = self.fc.createNode("NormalVectorNode", pos=(150, 200))
        self.logNode = self.fc.createNode("LogNode", pos=(300, 50))
    
    def connect_node_terminals(self):
        # connect the acceleration values with the buffer nodes and the buffers with the corresponding plot widgets
        self.fc.connectTerminals(self.dippidNode['accelX'], self.bufferNodeX['dataIn'])
        self.fc.connectTerminals(self.dippidNode['accelY'], self.bufferNodeY['dataIn'])
        self.fc.connectTerminals(self.dippidNode['accelZ'], self.bufferNodeZ['dataIn'])
        self.fc.connectTerminals(self.bufferNodeX['dataOut'], self.pw1Node['In'])
        self.fc.connectTerminals(self.bufferNodeY['dataOut'], self.pw2Node['In'])
        self.fc.connectTerminals(self.bufferNodeZ['dataOut'], self.pw3Node['In'])
    
        # connect the normal vector node with two of the acceleration values and plot it
        self.fc.connectTerminals(self.dippidNode['accelX'], self.normalVectorNode['accel1'])
        self.fc.connectTerminals(self.dippidNode['accelZ'], self.normalVectorNode['accel2'])
        self.fc.connectTerminals(self.normalVectorNode['rotation'], self.pw4Node['In'])

        # connect the log node with the acceleration buffer nodes and the normal vector node
        self.fc.connectTerminals(self.dippidNode['accelX'], self.logNode['accelX'])
        self.fc.connectTerminals(self.dippidNode['accelY'], self.logNode['accelY'])
        self.fc.connectTerminals(self.dippidNode['accelZ'], self.logNode['accelZ'])
        self.fc.connectTerminals(self.normalVectorNode['rotation'], self.logNode['rotation'])


def main():
    # parse command line input and print out some helpful information
    parser = ArgumentParser(description="A small application that generates a PyqtGraph flowchart.")
    parser.add_argument("-p", "--port", help="The port on which the mobile device sends its data via DIPPID", type=int,
                        default=5700, required=False)
    args = parser.parse_args()
    port = args.port

    # register the custom nodes
    fclib.registerNodeType(LogNode, [('Logging',)])
    fclib.registerNodeType(NormalVectorNode, [('NormalVector',)])

    # create the gui
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('Assignment 7')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    # create the flowchart
    flowchart = FlowChart(layout, port)

    win.show()
    # if not running in interactive mode or using PySide instead of PyQt, start the app
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(QtGui.QApplication.instance().exec_())


if __name__ == '__main__':
    main()
