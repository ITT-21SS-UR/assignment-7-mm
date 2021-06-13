#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implemented by Michael Meckl.
"""

from argparse import ArgumentParser


def main():
    # parse command line input and print out some helpful information
    parser = ArgumentParser(description="A small application that generates a PyqtGraph flowchart.")
    parser.add_argument("-p", "--port", help="The port on which the mobile device sends its data via DIPPID", type=int,
                        default=5700, required=False)
    args = parser.parse_args()
    port = args.port


if __name__ == '__main__':
    main()
