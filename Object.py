#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, Union
from dataclasses import dataclass, field
import os
import pickle
from PIL import Image, ImageTk, ImageDraw, ImageFont

@dataclass
class GameTitle:
    title: str

    def __post_init__(self):
        self._create_character_list(self.title)
        self.player_list = os.listdir(f"StreamHelper/Gametitle/{self.title}/Player")

    def _create_character_list(self, title: str):
        character_list = os.listdir(f"StreamHelper/Gametitle/{title}/character/")
        self.character_list = [Character(character_txt, title) for character_txt in character_list]


@dataclass
class Character:
    name: str
    title: str

    def __post_init__(self):
        self.body = self._create_image_asset(f"StreamHelper/Gametitle/{self.title}/character/{self.name}/body.png")
        self.face = self._create_image_asset(f"StreamHelper/Gametitle/{self.title}/character/{self.name}/face.png")

    def _create_image_asset(self, path: str) -> Tuple[Image.Image, None]:
        if os.path.exists(path):
            return Image.open(path)
        else:
            return None


class Object:
    def save(self, filepath: str):
        with open(filepath, "wb") as f:
            pickle.dump(self.data, f)

    @classmethod
    def load(self, filepath: str) -> dataclass:
        with open(filepath, "rb") as f:
            return pickle.load(f)


@dataclass
class PlayerData:
    name: str = ""
    title: str = ""
    character: str = ""
    team: str = ""
    image: Image = None

class Player(Object):
    def __init__(self, title:str):
        self.data = PlayerData()
        self.title = title
        self.change_player_image("StreamHelper/image/face.png")

    def __repr__(self):
        return repr(repr(self.data))

    @classmethod
    def load(cls, filepath: str):
        data = Object.load(filepath)
        player = cls(data.title)
        player.data = data
        return player

    def load_player_data(self, filepath):
        self.data = super().load(filepath)

    def change_player_image(self, image_path: str):
        self.data.image = Image.open(image_path)

    def update_player_data(self, master_data: dict):
        self.data.name = master_data["名前"].get()
        self.data.title = self.title
        self.data.character = master_data["使用キャラ"].get()
        self.data.team = master_data["所属チーム"].get()


@dataclass
class TeamData:
    name: str = ""
    length: int = 1
    player_list: list = field(default_factory=list)
    image: Image = None

class Team(Object):
    def __init__(self, title: str):
        self.title = title
        self.data = TeamData()
        self.data.player_list.append("")
        self.change_team_image("StreamHelper/image/team.png")

    def change_team_image(self, image_path: str):
        self.data.image = Image.open(image_path)

    def load_team_data(self, filepath: str):
        self.data = super().load(filepath)

    def update_team_length(self, new_length: int):
        self.data.length = new_length
        if self.data.length < 1:
            self.data.length = 1
        if self.data.length > len(self.data.player_list):
            self.data.player_list.append("")
        elif self.data.length < len(self.data.player_list):
            self.data.player_list.pop(-1)


def layout_image_create(object):
    if "Image" in object.cls:
        size = (200, 200)
        color = "blue"
    elif "Text" in object.cls:
        size = (300, 60)
        color = "red"
    if "Counter" in object.cls:
        size = (100, 100)
        color = "yellow"
    image = Image.new("RGBA", size, (255, 255, 255, 100))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("StreamHelper\Font\meiryo.ttc", 20)
    draw.rectangle((0, 0, size[0]-1, size[1]-1),
                   width=5,
                   outline=color
                   )
    draw.text((0, 0),
              object.category,
              fill="white",
              stroke_width=2,
              stroke_fill='black',
              font=font)
    fontsize = draw.textsize(object.name, font)
    draw.text((size[0]/2 -fontsize[0]/2, size[1]/2 -fontsize[1]/2),
              object.name,
              fill="white",
              stroke_width=2,
              stroke_fill='black',
              font=font)
    return image



class LayoutObject:
    image: Image.Image

    def update_size(self, width: int, height: int):
        self.width = width
        self.height = height

    def update_position(self, position: tuple):
        self.position = position

    def update_image(self):
        image = self.image.copy()
        # 画像処理
        self.width, self.height = image.size
        self.image_tk = ImageTk.PhotoImage(image)

    def resize(self, size: Tuple[int, int]):
        image = self.image.copy().resize(size)
        self.width, self.height = image.size
        self.image_tk = ImageTk.PhotoImage(image)


@dataclass
class ConstImageLayoutObject(LayoutObject):
    image: Image.Image
    name: str
    id: str
    width: Union[int, float] = 0
    height: Union[int, float] = 0
    position: "list[int]" = field(default_factory=list)
    cls: str = "ConstImageLayoutObject"

    def __init__(self, image_path: str, id: str):
        self.image = Image.open(image_path)
        self.name = os.path.basename(image_path)
        self.id = id
        self.width = self.image.size[0]
        self.height = self.image.size[1]

@dataclass
class VariableImageLayoutObject(LayoutObject):
    image: Image.Image = None
    name: str = ""
    id: str = ""
    category: str = ""
    width: Union[int, float] = 0
    height: Union[int, float] = 0
    position: "list[int]" = field(default_factory=list)
    cls: str = "VariableImageLayoutObject"

    def __init__(self, name: str, category: str, id: str):
        self.name = name
        self.category = category
        self.id = id
        self.image = layout_image_create(self)
        self.width = self.image.size[0]
        self.height = self.image.size[1]


@dataclass
class ConstTextLayoutObject(LayoutObject):
    image: Image.Image
    name: str
    font: str
    cls: str = "ConstTextLayoutObject"


@dataclass
class VariableTextLayoutObject(LayoutObject):
    image: Image.Image = None
    name: str = ""
    id: str = ""
    category: str = ""
    width: Union[int, float] = 0
    height: Union[int, float] = 0
    position: "list[int]" = field(default_factory=list)
    font: str = "meiryo.ttc"
    cls: str = "VariableTextLayoutObject"

    def  __init__(self, name: str, category: str, id: str):
        self.name = name
        self.category = category
        self.id = id
        self.image = layout_image_create(self)
        self.width = self.image.size[0]
        self.height = self.image.size[1]

@dataclass
class CounterTextLayoutObject(LayoutObject):
    image: Image.Image
    name: str
    id: str
    width: Union[int, float] = 0
    height: Union[int, float] = 0
    position: "list[int]" = field(default_factory=list)
    font: str = "meiryo.ttc"
    cls: str = "CounterTextLayoutObject"

    def  __init__(self, name: str, category: str, id: str):
        self.name = name
        self.category = category
        self.id = id
        self.image = layout_image_create(self)
        self.width = self.image.size[0]
        self.height = self.image.size[1]

@dataclass
class CounterImageLayoutObject(LayoutObject):
    image: Image.Image
    image_list: "dict[str, Image.Image]" = field(default_factory=dict)
    name: str = ""
    id: str = ""
    category: str = ""
    width: Union[int, float] = 0
    height: Union[int, float] = 0
    position: "list[int]" = field(default_factory=list)
    length: int = 0
    cls: str = "CounterImageLayoutObject"

    def __init__(self, name: str, category: str, id: str, folder_path: str):
        self.name = name
        self.category = category
        self.id = id
        self.image = layout_image_create(self)
        self.image_list = {os.path.splitext(path)[0]: Image.open(f"{folder_path}/{path}") for path in os.listdir(folder_path)}

UNION_OBJECT = Union[
    ConstTextLayoutObject,
    ConstImageLayoutObject,
    VariableImageLayoutObject,
    VariableTextLayoutObject,
    CounterTextLayoutObject,
    CounterImageLayoutObject
    ]

import Canvas
@dataclass
class LayoutCollection:
    list: "list[UNION_OBJECT]" = field(default_factory=list)
    width: int = 0
    height: int = 0
    position: "list[int]" = field(default_factory=list)
    def __init__(self, list: Canvas.LayoutObjectCustomList):
        self.list = list.dict.values()
        self.width = max([obj.object.position[1] for obj in self.list])
        self.height = max([obj.object.position[3] for obj in self.list])
        print(self.width, self.height)
        [print(obj.object) for obj in self.list]

    def save(self, filepath):
        with open(filepath, "wb") as f:
            pickle.dump(self, f)


if __name__ == "__main__":
    print(__name__)