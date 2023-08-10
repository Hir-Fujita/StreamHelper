#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Union, Tuple
import os
import random
import tkinter as tk
import Object as Obj
import Widget as Wid
import collections


class Manager:
    def __init__(self, parent):
        self.frame = ManagerFrame(self, parent)
        self.layout = LayoutManager(self)
        self.game = ""
        self.gametitle_list = os.listdir("StreamHelper/Gametitle")
        self.gametitle_select(0)

    def gametitle_select(self, num: int):
        self.game = Obj.GameTitle(self.gametitle_list[num])

    def random_id(self, n):
        return str(random.randrange(10**(n-1),10**n))

    def frame_update(self):
        self.frame.reset()
        for collection in self.layout.layout_dic.values():
            lists = [data for data in collection.list if "Variable" in data.cls or "Counter" in data.cls]
            if len(lists):
                self.frame.create_frame(collection.id)
                team_list = []
                for data in lists:
                    if data.category == "Player":
                        self.add_player_widget(collection.id)
                    elif data.category == "Counter":
                        self.add_counter_widget(collection.id, data)
                    elif data.category == "Team":
                        team_list.append((data.name, data.category, data.cls))
                if len(team_list):
                    team_length_list = [team for team in team_list if team[0] != "チーム名" and team[0] != "チーム画像"]
                    team_count = collections.Counter(team_length_list).most_common()[0][1] if len(team_length_list) else 0
                    self.add_team_widget(collection.id, team_count)

    def add_player_widget(self, id: str):
        self.frame.add_widget("Player", id)

    def add_team_widget(self, id: str, length: int):
        self.frame.add_widget("Team", id, length)
        print(f"チームの出現最大個数{length}")
        if length:
            print("チームWidget追加", length)

    def add_counter_widget(self, id: str, data: Obj.LayoutData):
        self.frame.add_widget("Counter", id, data)

    def generate_image(self):
        val = self.frame.get()
        print(val)


class ManagerFrame(tk.Frame):
    class Widget_dict:
        def __init__(self):
            self.dict: "dict[str, dict[Wid.ManagerChildrenFrame]]" = {}

        def create(self, id: str):
            self.dict[id] = {}

        def add(self, id: str, key: str, values: Wid.ManagerChildrenFrame):
            self.dict[id][key] = values

        def get(self):
            ids = self.dict.keys()
            return_dic = {}
            for id in ids:
                return_dic[id] = {key: value.get() for key, value in self.dict[id].items()}
            return return_dic

        def pack_forget(self, id: str):
            [wid.pack_forget() for wid in self.dict[id].values()]


    def __init__(self, manager, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.manager: Manager = manager
        self.frame_dic: "dict[str: tk.Frame]" = {}
        self.widgets = self.Widget_dict()
        self.pack()
        create_button = tk.Button(self, text="画像生成", width=20, command=self.manager.generate_image)
        create_button.pack()

    def reset(self):
        keys = [key for key in self.frame_dic.keys()]
        for key in keys:
            self.frame_dic[key].pack_forget()
            self.widgets.pack_forget(key)
        self.frame_dic: "dict[str: tk.Frame]" = {}
        self.widgets = self.Widget_dict()

    def create_frame(self, id: str):
        self.frame_dic[id] = tk.Frame(self)
        self.frame_dic[id].pack(side=tk.LEFT, padx=5)
        self.widgets.create(id)

    def add_widget(self, widget_category: str, id: str, data: Union[Obj.LayoutData, int]=None):
        if widget_category == "Player":
            self.widgets.add(id, "ManagerPlayerFrame", Wid.ManagerPlayerFrame(self.frame_dic[id], self.manager))
        elif widget_category == "Counter":
            if "Image" in data.cls:
                self.widgets.add(id, "ManagerCounterImageFrame", Wid.ManagerCounterImageFrame(self.frame_dic[id], self.manager, data))
            if "Text" in data.cls:
                self.widgets.add(id, "ManagerCounterTextFrame",  Wid.ManagerCounterTextFrame(self.frame_dic[id], self.manager))
        elif widget_category == "Team":
            self.widgets.add(id, "ManagerTeamFrame",  Wid.ManagerTeamFrame(self.frame_dic[id], self.manager, data))

    def delete_widget(self, id: str):
        self.frame_dic[id].pack_forget()
        del self.frame_dic[id]

    def get(self) -> "dict[str: str]":
        return self.widgets.get()


class LayoutManager:
    def __init__(self, manager: Manager):
        self.manager = manager
        self.frame = None
        self.layout_dic: "dict[str: Obj.LayoutCollection]" = {}
        self.widgets: "dict[str: Wid.LayoutViewer]" = {}

    def setting_add_widget_frame(self, dataframe):
        self.frame = dataframe

    def delete_widget(self, id: str):
        self.manager.frame.delete_widget(id)

    def add_layout_collection(self, data: Obj.LayoutCollection):
        count = len([d for d in self.layout_dic.values() if data.name in d.name])
        data.name = f"{data.name}_{count}" if count > 0 else data.name
        self.layout_dic[data.id] = data

    def delete_layout_collection(self, id: str):
        del self.layout_dic[id]

    def position_update(self, id: str, position: "list[int]"):
        self.layout_dic[id].position = position

    def size_update(self, id: str, size: Tuple[int]):
        self.layout_dic[id].size_update(size)

    def get(self):
        pass



if __name__ == "__main__":
    print(__name__)