#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, Union
from dataclasses import dataclass
import os
import pickle
from PIL import Image

@dataclass
class GameTitle:
    title: str

    def __post_init__(self):
        self._create_character_list(self.title)

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
    image: Image = None

class Team(Object):
    def __init__(self, title: str):
        self.title = title
        self.data = TeamData()
        self.list = []
        self.change_team_image("StreamHelper/image/team.png")

    def change_team_image(self, image_path: str):
        self.data.image = Image.open(image_path)

