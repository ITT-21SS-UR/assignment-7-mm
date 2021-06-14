#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implemented by Michael Meckl.
"""

import sys
import numpy as np
from argparse import ArgumentParser
# import pyqtgraph.examples
from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
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
            'dataIn': {'io': 'in'},
            # TODO specify all input separately!
            # 'accelX': {'io': 'in'},
            'dataOut': {'io': 'out'},
        }
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        print(kwds["dataIn"])
        print(kwds["dataIn"][0])
        return {'dataOut': kwds["dataIn"]}


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
            'rotation': {'io': 'out'},
        }
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        # kwds will have one keyword argument per input terminal.
        accel1 = kwds["accel1"][0]
        accel2 = kwds["accel2"][0]
        vector1 = np.array([accel1, 0])
        vector2 = np.array([0, accel2])
        # vector1_alt = np.array([0, 0], [accel1, 0])
        # vector2_alt = np.array([0, 0], [0, accel2])
        print(vector1)
        print(vector2)
        normal_vector = np.cross(vector1, vector2)
        print("Normal: ", np.array([0, normal_vector]))

        # TODO calculate the rotation! (angle between vector and the respective axis)

        # return {'rotation': [(0, 0), normal_vector]}
        return {'rotation': np.array([-accel1, accel2])}


fclib.registerNodeType(LogNode, [('Logging',)])
fclib.registerNodeType(NormalVectorNode, [('NormalVector',)])


def main():
    # parse command line input and print out some helpful information
    parser = ArgumentParser(description="A small application that generates a PyqtGraph flowchart.")
    parser.add_argument("-p", "--port", help="The port on which the mobile device sends its data via DIPPID", type=int,
                        default=5700, required=False)
    args = parser.parse_args()
    port = args.port  # TODO use the port for the dippid node! (maybe set it automatically?)

    # pyqtgraph.examples.run()

    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('Assignment 7')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    # Create an empty flowchart with a single input and output
    fc = Flowchart(terminals={})
    w = fc.widget()

    # layout.addWidget(fc.widget(), 0, 0, 2, 1)
    layout.addWidget(w, 0, 0, 2, 1)

    pw1 = pg.PlotWidget()
    layout.addWidget(pw1, 0, 1)
    pw1.setYRange(0, 1)
    pw1.setTitle("X-Acceleration")

    pw2 = pg.PlotWidget()
    layout.addWidget(pw2, 1, 1)
    pw2.setYRange(0, 1)
    pw2.setTitle("Y-Acceleration")

    pw3 = pg.PlotWidget()
    layout.addWidget(pw3, 2, 1)
    pw3.setYRange(0, 1)
    pw3.setTitle("Z-Acceleration")

    pw4 = pg.PlotWidget()
    layout.addWidget(pw4, 0, 2, 3, -1)  # make the last plot fill the entire right column
    pw4.setYRange(-1, 1)
    pw4.setTitle("Rotation")

    pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
    pw1Node.setPlot(pw1)
    pw2Node = fc.createNode('PlotWidget', pos=(150, -150))
    pw2Node.setPlot(pw2)
    pw3Node = fc.createNode('PlotWidget', pos=(0, 150))
    pw3Node.setPlot(pw3)
    pw4Node = fc.createNode('PlotWidget', pos=(150, 150))
    pw4Node.setPlot(pw4)

    """
    plotList = {'Top Plot': pw1, 'Bottom Plot': pw2}
    pw1Node.setPlotList(plotList)
    pw2Node.setPlotList(plotList)
    """

    dippidNode = fc.createNode("DIPPID", pos=(0, 0))
    bufferNodeX = fc.createNode('Buffer', pos=(150, -150))
    bufferNodeY = fc.createNode('Buffer', pos=(150, 0))
    bufferNodeZ = fc.createNode('Buffer', pos=(150, 150))
    normalVectorNode = fc.createNode("NormalVectorNode", pos=(250, 0))

    fc.connectTerminals(dippidNode['accelX'], bufferNodeX['dataIn'])
    fc.connectTerminals(dippidNode['accelY'], bufferNodeY['dataIn'])
    fc.connectTerminals(dippidNode['accelZ'], bufferNodeZ['dataIn'])
    fc.connectTerminals(bufferNodeX['dataOut'], pw1Node['In'])
    fc.connectTerminals(bufferNodeY['dataOut'], pw2Node['In'])
    fc.connectTerminals(bufferNodeZ['dataOut'], pw3Node['In'])

    # connect the normal vector node
    fc.connectTerminals(dippidNode['accelX'], normalVectorNode['accel1'])
    fc.connectTerminals(dippidNode['accelZ'], normalVectorNode['accel2'])
    fc.connectTerminals(normalVectorNode['rotation'], pw4Node['In'])

    # TODO create log node and connect it to the 3 buffer node outputs and the normalvector node output!

    # debug nodes with:
    # fc.setInput(nameOfInputTerminal=newValue)
    # output = fc.output()

    win.show()
    # if not running in interactive mode or using PySide instead of PyQt, start the app
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(QtGui.QApplication.instance().exec_())


if __name__ == '__main__':
    main()
