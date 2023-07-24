#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Union
import os
import random
from Object import GameTitle, Player, Team, LayoutManager
import Widget as Wid
from pprint import pprint as pp
import collections


class Manager:
    def __init__(self, parent):
        self.frame = Wid.ManagerFrame(parent)
        self.layout = LayoutManager()
        self.gametitle_list = os.listdir("StreamHelper/Gametitle")
        self.gametitle_select(0)

    def gametitle_select(self, num: int):
        self.game = GameTitle(self.gametitle_list[num])

    def random_id(self, n):
        return str(random.randrange(10**(n-1),10**n))

    def frame_update(self):
        # a = [data.list for data in [collection.list for collection in self.layout.layout_dic.values()]]
        # for i in a:
        #     print(i.name)
        name = []
        cls = []
        category = []
        for collection in self.layout.layout_dic.values():
            for data in collection.list:
                print("-----------------")
                print(f"name: {data.name}")
                print(f"cls: {data.cls}")
                print(f"category: {data.category}")
                name.append(data.name)
                cls.append(data.cls)
                category.append(data.category)
        name = collections.Counter(name).most_common()
        cls = collections.Counter(cls).most_common()
        category = collections.Counter(category).most_common()
        print("-----------------")
        print(name)
        print(cls)
        print(category)


if __name__ == "__main__":
    print(__name__)