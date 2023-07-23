#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Union
import os
from Object import GameTitle, Player, Team, LayoutManager

class Manager:
    def __init__(self):
        self.layout = LayoutManager()
        self.gametitle_list = os.listdir("StreamHelper/Gametitle")
        self.gametitle_select(0)

    def gametitle_select(self, num: int):
        self.game = GameTitle(self.gametitle_list[num])


if __name__ == "__main__":
    print(__name__)