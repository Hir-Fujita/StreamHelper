#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Union, Tuple
import os
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageOps
import Object as Obj
import Widget as Wid


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
                        self.add_player_widget(collection.id, data)
                    elif data.category == "Counter":
                        self.add_counter_widget(collection.id, data)
                    elif data.category == "Team":
                        team_list.append(data)
                if len(team_list):
                    self.add_team_widget(collection.id, team_list)

    def add_player_widget(self, id: str, data: Obj.LayoutData):
        self.frame.add_widget("Player", id, data)

    def add_team_widget(self, id: str, data_list: "list[Obj.LayoutData]"):
        data_list = [data for data in data_list if data.name != "チーム名" and data.name != "チーム画像"]
        counter = {}
        for data in data_list:
            if not data.name in counter:
                counter[data.name] = []
            counter[data.name].append(data.id)
        length = [len(count) for count in counter.values()]
        length.sort()
        id_dict = {}
        for count in counter.values():
            for index, _id in enumerate(count):
                id_dict[_id] = index
        self.frame.add_widget("Team", id=id, length=length[-1], id_dict=id_dict)

    def add_counter_widget(self, id: str, data: Obj.LayoutData):
        self.frame.add_widget("Counter", id, data)

    def generate_image(self):
        generator = ImageGenerator(self, self.frame.get(), self.layout.get())
        generator.create_image()


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
                return_dic[id] = {key: value.get(id) for key, value in self.dict[id].items()}
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

    def add_widget(self, widget_category: str, id: str, data: Obj.LayoutData=None, length: int=0, id_dict: "dict[str: str]"=None):
        if widget_category == "Player":
            self.widgets.add(id, data.id, Wid.ManagerPlayerFrame(self.frame_dic[id], self.manager))
        elif widget_category == "Counter":
            if "Image" in data.cls:
                self.widgets.add(id, data.id, Wid.ManagerCounterImageFrame(self.frame_dic[id], self.manager, data))
            if "Text" in data.cls:
                self.widgets.add(id, data.id,  Wid.ManagerCounterTextFrame(self.frame_dic[id], self.manager))
        elif widget_category == "Team":
            self.widgets.add(id, id,  Wid.ManagerTeamFrame(self.frame_dic[id], self.manager, length, id_dict))

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
        return self.layout_dic


class ImageGenerator:
    def __init__(self, manager: Manager, value_dic: "dict", layout_dic: "dict[str: Obj.LayoutCollection]"):
        self.manager = manager
        self.value_dic = value_dic
        self.layout_dic = layout_dic

    def create_image(self):
        image = Image.new("RGBA", (960, 540), (255, 255, 255, 0))
        for _, layouts in self.layout_dic.items():
            img = self.generate_layout(layouts)
            image.paste(img, self.get_box(False, layouts), mask=img)
        image.save("StreamHelper/test.png")

    def get_value(self, object: Obj.LayoutData, dic: dict, master_key: str="") -> Union[str, Image.Image]:
        if "Const" in object.cls:
            return ""
        else:
            if object.category == "Team":
                value = dic[master_key]
                if "チーム" in object.name:
                    value = value[master_key]
                    team = Obj.Team.load(f"StreamHelper/Gametitle/{self.manager.game.title}/Team/{value}.shd")
                    if "名" in object.name:
                        return team.data.name
                    if "画像" in object.name:
                        return team.data.image
                else:
                    value = value[object.id]
                    player = Obj.Player.load(f"StreamHelper/Gametitle/{self.manager.game.title}/Player/{value}.shd")
                    if object.name == "プレイヤー名":
                        return player.data.name
                    if object.name == "プレイヤー画像":
                        return player.data.image
                    if object.name == "キャラクター名":
                        return player.data.character
                    if object.name == "キャラクター画像":
                        return Image.open(f"StreamHelper/Gametitle/{self.manager.game.title}/Character/{player.data.character}/face.png")
            else:
                value = dic[object.id]
                if object.category == "Player":
                    player = Obj.Player.load(f"StreamHelper/Gametitle/{self.manager.game.title}/Player/{value}.shd")
                    if object.name == "プレイヤー名":
                        return player.data.name
                    if object.name == "プレイヤー画像":
                        return player.data.image
                    if object.name == "キャラクター名":
                        return player.data.character
                    if object.name == "キャラクター画像":
                        return Image.open(f"StreamHelper/Gametitle/{self.manager.game.title}/Character/{player.data.character}/face.png")
                if object.category == "Counter":
                    if "Text" in object.cls:
                        return value
                    if "Image" in object.cls:
                        return object.image_list[value]

    def generate_layout(self, collection: Obj.LayoutCollection) -> Image.Image:
        values = self.value_dic[collection.id]
        image = Image.new("RGBA", (960, 540), (255, 255, 255, 0))
        for layout in reversed(collection.list):
            value = self.get_value(layout, values, collection.id)
            element = Obj.layout_element_check(layout).load_cls(layout)
            element_image = element.generate_image(value, collection.mirror)
            if element_image.mode != "RGBA":
                element_image = element_image.convert("RGBA")
            image.paste(element_image, self.get_box(collection.mirror, element),  mask=element_image)
        image = image.resize((collection.width, collection.height))
        return image

    def get_box(self, mirror: bool, element: Union[Obj.LayoutElement, Obj.LayoutCollection]) -> Tuple[int]:
        if mirror:
            x = 960 - element.position[0] - element.width
            y = element.position[1]
            return (x, y)
        else:
            return (element.position[0], element.position[1])



if __name__ == "__main__":
    print(__name__)