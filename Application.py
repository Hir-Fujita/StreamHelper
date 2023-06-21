#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, Union
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from Manager import Manager
from Object import Player, Team

NAME = "FightingGameStreamHelper"
VERSION = "0.1"

class Application(tk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        master.geometry("600x200")
        master.title(f"{NAME}.ver.{VERSION}")
        self.manager = Manager()

        self.frame = tk.Frame(master)
        self.frame.pack()
        self._create_menu(master)

    def _create_menu(self, master: tk.Tk):
        self.menu_widget = tk.Menu(master)
        master.config(menu=self.menu_widget)

        menu_gametitle = tk.Menu(self.menu_widget, tearoff=0)
        self.menu_widget.add_cascade(label="GameTitle",
                                     menu=menu_gametitle)
        radio_variable = tk.IntVar(value=0)
        for num, title in enumerate(self.manager.gametitle_list):
            menu_gametitle.add_radiobutton(
                label=title,
                value=num,
                variable=radio_variable,
                command=self.manager.gametitle_select
            )

        self.player_reg_window = PlayerRegisterWidget(self.manager)
        self.menu_widget.add_command(
            label="Player登録",
            command=self.player_reg_window.window_create
        )

        self.team_reg_window = TeamRegisterWidget(self.manager)
        self.menu_widget.add_command(
            label="Team登録",
            command=self.team_reg_window.window_create
        )

        self.layout_object_reg_window = LayoutObjectCreateWidget(self.manager)
        self.menu_widget.add_command(
            label="LayoutObject作成",
            command=self.layout_object_reg_window.window_create
        )

        self.stream_layout_window = StreamLayoutWidget(self.manager)
        self.menu_widget.add_command(
            label="配信Layout設定",
            command=self.stream_layout_window.window_create
        )


class NewWindow:
    def __init__(self, manager: Manager):
        self.window = None
        self.manager = manager

    def window_create(self):
        if self.window is not None:
            self.window.destroy()
        self.window = tk.Toplevel()
        self.window.focus()
        self.window.title(self.get_window_title())
        self.window.geometry(self.get_window_size())

    def get_window_title(self) -> str:
        raise NotImplementedError

    def get_window_size(self) -> str:
        raise NotImplementedError

    def _create_imageTK(self, path: Union[str, Image.Image], resize: Union[Tuple[int, int], bool]=False) -> ImageTk.PhotoImage:
        if type(path) == str:
            image = Image.open(path)
        else:
            image = path
        if resize:
            image = image.resize(resize)
        image_tk = ImageTk.PhotoImage(image)
        return image_tk

    def _save_filedialogwindow(self, save_name: str, title: str, category: str) -> str:
        filepath = filedialog.asksaveasfilename(
            title=title,
            parent=self.window,
            initialfile=save_name,
            defaultextension=".shd",
            filetypes=[("StreamHelper_datafile", ".shd")],
            initialdir=f"./StreamHelper/Gametitle/{self.manager.game.title}/{category}/"
        )
        return filepath

    def destroy(self):
        if self.window is not None:
            self.window.destroy()

    def _open_filedialogwindow(self, title: str, category: str=None) -> str:
        if category is not None:
            initialdir = f"StreamHelper/Gametitle/{self.manager.game.title}/{category}"
            filetypes=[("StreamHelper_datafile", ".shd")]
        else:
            initialdir = "StreamHelper"
            filetypes = [("Image file", ".png .jpg")]
        filepath = filedialog.askopenfilename(
            title=title,
            multiple=False,
            parent=self.window,
            initialdir=initialdir,
            filetypes=filetypes,
        )
        return filepath


class PlayerRegisterWidget(NewWindow):
    def __init__(self, manager: Manager):
        super().__init__(manager)
        self.widget_list = {}

    def get_window_title(self):
        return f"プレイヤー登録画面__{self.manager.game.title}"

    def get_window_size(self):
        return "600x400"

    def window_create(self):
        super().window_create()

    def window_create(self):
        super().window_create()
        self.object = Player(self.manager.game.title)

        left_frame = tk.Frame(self.window)
        left_widget_list = [
            [tk.Entry, {"width":23}, "名前"],
            [ttk.Combobox, {"width":20, "values":[character.name  for character in self.manager.game.character_list]}, "使用キャラ"],
            [ttk.Entry, {"width":23}, "所属チーム"]
        ]
        for index, widget in enumerate(left_widget_list):
            self._create_widget_add_label(index, left_frame, widget[0], widget[1], widget[2], True)
        button_frame = tk.Frame(left_frame)
        save_button = tk.Button(button_frame, text="save", command=self._save_data)
        save_button.grid(row=0, column=0, padx=5)
        load_button = tk.Button(button_frame, text="load", command=self._load_data)
        load_button.grid(row=0, column=1, padx=5)
        button_frame.grid(row=len(left_widget_list), column=0, columnspan=2, pady=10)
        left_frame.pack(side=tk.LEFT)

        self.object_image = self._create_imageTK(self.object.data.image, (200, 200))
        right_widget_list = [
            [tk.Label, {"text":"プレイヤー画像"}, "プレイヤー画像ラベル"],
            [tk.Label, {"image":self.object_image}, "プレイヤー画像"],
            [tk.Button, {"text":"画像読み込み", "command":self._change_player_image}, "画像読み込みボタン"]
        ]
        right_frame = tk.Frame(self.window)
        for index, widget in enumerate(right_widget_list):
            self._create_widget_add_label(index, right_frame, widget[0], widget[1], widget[2], False)
        right_frame.pack(side=tk.LEFT, padx=5)

    def _create_widget_add_label(self, index: int, master, widget_type, params, name: str, add_label=False):
        column_index = 0
        if add_label:
            label = tk.Label(master, text=name)
            label.grid(row=index, column=column_index, padx=2, pady=2)
            column_index = 1
        self.widget_list[name] = widget_type(master, **params)
        self.widget_list[name].grid(row=index, column=column_index, padx=2)

    def _save_data(self):
        player_name = self.widget_list["名前"].get()
        character_name = self.widget_list["使用キャラ"].get()
        filename = f"{player_name}_{character_name}"
        save_path = super()._save_filedialogwindow(filename, "プレイヤーデータ保存", "Player")
        if save_path:
            self.object.update_player_data(self.widget_list)
            self.object.save(save_path)

    def _load_data(self):
        open_path = super()._open_filedialogwindow("プレイヤーデータ読み込み", "Player")
        if open_path:
            self.object.load_player_data(open_path)
            self.widget_list["名前"].delete(0, tk.END)
            self.widget_list["名前"].insert(0, self.object.data.name)
            self.widget_list["使用キャラ"].set(self.object.data.character)
            self.widget_list["所属チーム"].delete(0, tk.END)
            self.widget_list["所属チーム"].insert(0, self.object.data.team)
            self.object_image = self._create_imageTK(self.object.data.image, (200, 200))
            self.widget_list["プレイヤー画像"].config(image=self.object_image)

    def _change_player_image(self):
        image_path = super()._open_filedialogwindow("画像データ読み込み")
        if image_path:
            self.object.change_player_image(image_path)
            self.object_image = self._create_imageTK(image_path, (200, 200))
            self.widget_list["プレイヤー画像"].config(image=self.object_image)


class TeamRegisterWidget(NewWindow):
    def __init__(self, manager: Manager):
        super().__init__(manager)

    def get_window_title(self):
        return f"チーム登録画面__{self.manager.game.title}"

    def get_window_size(self):
        return "600x400"

    def window_create(self):
        super().window_create()
        self.object = Team(self.manager.game.title)

        top_frame = tk.Frame(self.window)
        top_frame.pack()
        team_name_entry_label = tk.Label(top_frame, text="チーム名")
        team_name_entry_label.grid(row=0, column=0, padx=5, pady=2)
        team_name_entry_box = tk.Entry(top_frame, width=23)
        team_name_entry_box.grid(row=0, column=1, padx=5, pady=2)
        self.object_image = self._create_imageTK(self.object.data.image, (100, 100))
        self.team_image_label = tk.Label(top_frame, image=self.object_image)
        self.team_image_label.grid(row=1, column=0, columnspan=2)
        team_image_button = tk.Button(top_frame, text="チームアイコン変更",)
        team_image_button.grid(row=2, column=0, columnspan=2)


class LayoutObjectCreateWidget(NewWindow):
    def __init__(self, manager: Manager):
        super().__init__(manager)

    def get_window_title(self):
        return "レイアウトオブジェクト登録画面"

    def get_window_size(self):
        return "600x400"

    def window_create(self):
        super().window_create()


class StreamLayoutWidget(NewWindow):
    def __init__(self, manager: Manager):
        super().__init__(manager)

    def get_window_title(self):
        return f"配信レイアウト設定画面__{self.manager.game.title}"

    def get_window_size(self):
        return "600x400"

    def window_create(self):
        super().window_create()



def main():
	win = tk.Tk()
	app = Application(master=win)
	app.mainloop()


if __name__ == "__main__":
    main()
