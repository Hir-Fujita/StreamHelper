#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Union
import os
from Object import GameTitle, Player, Team

class Manager:
    def __init__(self):
        self.gametitle_list = os.listdir("StreamHelper/Gametitle")
        self.gametitle_select(0)

    def gametitle_select(self, num: int):
        self.game = GameTitle(self.gametitle_list[num])

    def player_init_