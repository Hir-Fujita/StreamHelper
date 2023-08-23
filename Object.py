#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, Union
from dataclasses import dataclass, field
import os
import pickle
from PIL import Image, ImageTk, ImageDraw, ImageFont

def save(filepath, data):
    with open(filepath, "wb") as f:
        pickle.dump(data, f)

def load(filepath):
    with open(filepath, "rb") as f:
        return pickle.load(f)

@dataclass
class GameTitle:
    title: str

    def __post_init__(self):
        self._create_character_list(self.title)
        self.player_list = os.listdir(f"StreamHelper/Gametitle/{self.title}/Player")
        self.team_list = os.listdir(f"StreamHelper/Gametitle/{self.title}/Team")

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
    title: str = ""
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

    @classmethod
    def load(cls, filepath: str):
        data = Object.load(filepath)
        team = cls(data.title)
        team.data = data
        return team

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



@dataclass
class LayoutData:
    name: str = ""
    category: str = ""
    id: str = ""
    cls: str = ""
    font: str = ""
    width: Union[int, float] = 0
    height: Union[int, float] = 0
    position: "list[int]" = field(default_factory=list)
    image: Image.Image = None
    image_list: "dict[Image.Image]" = None

def kw_check(dic: dict):
    dic.setdefault("cls", "")
    dic.setdefault("position", [0, 0, 0, 0])
    dic.setdefault("image", None)
    dic.setdefault("font", "")
    dic.setdefault("width", 0)
    dic.setdefault("height", 0)
    dic.setdefault("image_list", None)
    return dic


class LayoutElement:
    def __init__(self, name: str, category: str, id: str, **kwargs):
        self.name: str = name
        self.category: str = category
        self.id: str = id
        kw = kw_check(kwargs)
        self.cls = kw["cls"]
        self.position: "list[int]" = kw["position"]
        self.image: Image.Image = kw["image"]
        self.font = kw["font"]
        self.width = kw["width"]
        self.height = kw["height"]
        self.image_list: "dict[Image.Image]" = None

    def save_cls(self) -> LayoutData:
        datacls = LayoutData(
            name = self.name,
            category = self.category,
            id = self.id,
            cls = self.cls,
            font = self.font,
            width = self.width,
            height = self.height,
            position = self.position,
            image = self.image,
            image_list = self.image_list
        )
        return datacls

    @classmethod
    def load_cls(cls, datacls: LayoutData) -> LayoutData:
        return cls(
            datacls.name,
            datacls.category,
            datacls.id,
            cls = datacls.cls,
            position = datacls.position,
            image = datacls.image,
            font = datacls.font,
            width = datacls.width,
            height = datacls.height,
        )

    def create_layout_image(self, size: Tuple[int], color: str, category: str, name: str):
        canvas_size = (960, 540)
        image = Image.new("RGBA", size, (255, 255, 255, 100))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("StreamHelper\Font\meiryo.ttc", 20)
        draw.rectangle((0, 0, size[0]-1, size[1]-1),
                        width=5,
                        outline=color
                    )
        draw.text((0, 0),
                  category,
                  fill="white",
                  stroke_width=2,
                  stroke_fill='black',
                  font=font)
        fontsize = draw.textsize(name, font)
        draw.text((size[0]/2 -fontsize[0]/2, size[1]/2 -fontsize[1]/2),
                  name,
                  fill="white",
                  stroke_width=2,
                  stroke_fill='black',
                  font=font)
        self.width, self.height = size
        self.position = [
            canvas_size[0] /2 - self.width /2,
            canvas_size[1] /2 - self.height /2,
            canvas_size[0] /2 + self.width /2,
            canvas_size[1] /2 + self.height /2,
        ]
        return image

    def update_size(self, width: int, height: int):
        self.width = width
        self.height = height

    def update_position(self, position: tuple):
        self.position = position

    def resize(self, size: Tuple[int, int]):
        image = self.image.copy()
        image = image.resize(size)
        self.width, self.height = image.size
        self.image_tk = ImageTk.PhotoImage(image)

    @classmethod
    def variable_check(cls) -> bool:
        raise NotImplementedError

    def generate_image(self, path: str) -> Image.Image:
        raise NotImplementedError


class ConstImageLayoutObject(LayoutElement):
    def __init__(self, image_path: str, category: str, id: str, **kwargs):
        super().__init__(os.path.basename(image_path), category, id, **kwargs)
        self.cls = "ConstImageLayoutObject"
        if self.image is None:
            self._create_layout_image(image_path)
            self.image_tk = ImageTk.PhotoImage(self.image)
        else:
            self.resize((self.width, self.height))

    def _create_layout_image(self, filepath):
        self.image = Image.open(filepath)
        self.width, self.height = self.image.size
        canvas_size = (960, 540)
        self.position = [
            canvas_size[0] /2 - self.width /2,
            canvas_size[1] /2 - self.height /2,
            canvas_size[0] /2 + self.width /2,
            canvas_size[1] /2 + self.height /2,
        ]

    @classmethod
    def variable_check(cls) -> bool:
        return False

    def generate_image(self, path: str) -> Image.Image:
        return self.image

class VariableImageLayoutObject(LayoutElement):
    def __init__(self, name: str, category: str, id: str, **kwargs):
        super().__init__(name, category, id, **kwargs)
        self.cls = "VariableImageLayoutObject"
        if self.image is None:
            self.image = self.create_layout_image()
            self.image_tk = ImageTk.PhotoImage(self.image)
        else:
            self.resize((self.width, self.height))

    def create_layout_image(self) -> Image.Image:
        return super().create_layout_image((200, 200), "blue", self.category, self.name)

    @classmethod
    def variable_check(cls) -> bool:
        return True

    def generate_image(self, path: str) -> Image.Image:
        pass

class ConstTextLayoutObject(LayoutElement):
    def __init__(self, name: str, category: str, id: str, **kwargs):
        super().__init__(name, category, id, **kwargs)
        self.cls = "ConstTextLayoutObject"
        if self.image is None:
            self.image = self.create_layout_image()
            self.image_tk = ImageTk.PhotoImage(self.image)
        else:
            self.resize((self.width, self.height))

    def create_layout_image(self):
        # テキストエレメント用のレイアウトイメージを作成します。
        pass

    @classmethod
    def variable_check(cls) -> bool:
        return False

class VariableTextLayoutObject(LayoutElement):
    def __init__(self, name: str, category: str, id: str, **kwargs):
        super().__init__(name, category, id, **kwargs)
        self.cls = "VariableTextLayoutObject"
        if self.image is None:
            self.image = self.create_layout_image()
            self.image_tk = ImageTk.PhotoImage(self.image)
        else:
            self.resize((self.width, self.height))

    def create_layout_image(self):
        return super().create_layout_image((300, 60), "red", self.category, self.name)

    @classmethod
    def variable_check(cls) -> bool:
        return True

class CounterTextLayoutObject(LayoutElement):
    def __init__(self, name: str, category: str, id: str, **kwargs):
        super().__init__(name, category, id, **kwargs)
        self.cls = "CounterTextLayoutObject"
        if self.image is None:
            self.image = self.create_layout_image()
            self.image_tk = ImageTk.PhotoImage(self.image)
        else:
            self.resize((self.width, self.height))

    def create_layout_image(self):
        return super().create_layout_image((100, 100), "yellow", self.category, self.name)

    @classmethod
    def variable_check(cls) -> bool:
        return True

class CounterImageLayoutObject(LayoutElement):
    def __init__(self, name: str, category: str, id: str, folder_path: str="", **kwargs):
        super().__init__(name, category, id, **kwargs)
        self.cls = "CounterImageLayoutObject"
        if self.image is None:
            self.image = self.create_layout_image()
            self.image_tk = ImageTk.PhotoImage(self.image)
        else:
            self.resize((self.width, self.height))
        if folder_path:
            self.image_list = {os.path.splitext(path)[0]: Image.open(f"{folder_path}/{path}") for path in os.listdir(folder_path)}

    def create_layout_image(self):
        return super().create_layout_image((100, 100), "yellow", self.category, self.name)

    def save_cls(self) -> LayoutData:
        save_data = super().save_cls()
        save_data.image_list = self.image_list
        return save_data

    @classmethod
    def load_cls(cls, datacls: LayoutData):
        load_data = super().load_cls(datacls)
        load_data.image_list = datacls.image_list
        return load_data

    @classmethod
    def variable_check(cls) -> bool:
        return True

UNION_OBJECT = Union[
    ConstTextLayoutObject,
    ConstImageLayoutObject,
    VariableImageLayoutObject,
    VariableTextLayoutObject,
    CounterTextLayoutObject,
    CounterImageLayoutObject
    ]



def layout_element_check(element: Union[LayoutData, str]) -> UNION_OBJECT:
    OBJECT_DICT = {
    "ConstTextLayoutObject": ConstTextLayoutObject,
    "ConstImageLayoutObject": ConstImageLayoutObject,
    "VariableImageLayoutObject": VariableImageLayoutObject,
    "VariableTextLayoutObject": VariableTextLayoutObject,
    "CounterTextLayoutObject": CounterTextLayoutObject,
    "CounterImageLayoutObject": CounterImageLayoutObject
    }
    if isinstance(element, str):
        return OBJECT_DICT[element]
    else:
        return OBJECT_DICT[element.cls]



class LayoutCollection:
    def __init__(self, init_list: "list[LayoutData]", id: str, name: str):
        self.name = name
        self.list: "list[LayoutData]" = init_list
        self.mirror = False
        self.image = self.create_image()
        self.width, self.height = self.image.size
        canvas_size = (960, 540)
        self.position: "list[int]" = [
            canvas_size[0] /2 - self.width /2,
            canvas_size[1] /2 - self.height /2,
            canvas_size[0] /2 + self.width /2,
            canvas_size[1] /2 + self.height /2,
        ]
        self.id = id
        self.image_tk = ImageTk.PhotoImage(self.image)

    def debug_list_print(self) -> str:
        return_list = [data.__repr__() for data in self.list]
        return "\n".join(return_list)

    def debug_print(self) -> str:
        return_list = [
            f"LayoutCollection_Name: {self.name}",
            f"List_Length: {len(self.list)}",
            f"Width: {self.width}"
            f"Height: {self.height}",
            f"Position: {self.position}"
        ]
        return "\n".join(return_list)

    def create_image(self):
        max_x = max([obj.position[2] for obj in self.list])
        image = Image.new("RGBA", (960, 540), (255, 255, 255, 0))
        for data in reversed(self.list):
            data.image = data.image.resize((data.width, data.height))
            x = max_x - (data.position[0]+data.width) if self.mirror else data.position[0]
            y = data.position[1]
            image.paste(data.image, (x, y), mask=data.image)
        return image.crop(image.getbbox())

    def size_update(self, size: Tuple[int]):
        self.width, self.height = size
        image = self.image.copy().resize((self.width, self.height))
        self.image_tk = ImageTk.PhotoImage(image)

    def mirror_update(self):
        self.mirror = not self.mirror
        self.image = self.create_image()
        image = self.image.copy().resize((self.width, self.height))
        self.image_tk = ImageTk.PhotoImage(image)


if __name__ == "__main__":
    print(__name__)