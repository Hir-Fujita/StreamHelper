#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, Union
import os
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
from Manager import Manager
from Object import Player, Team
from Canvas import ScrollFrame, CustomLabelFrame, CustomCanvas

NAME = "FightingGameStreamHelper"
VERSION = "0.1"

# tkinterのCanvasは配置時のサイズと実際のクリックイベントで取得できる座標にズレが有る

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
        self.menu_widget.add_cascade(label="GameTitle", menu=menu_gametitle)
        radio_variable = tk.IntVar(value=0)
        for num, title in enumerate(self.manager.gametitle_list):
            menu_gametitle.add_radiobutton(
                label=title,
                value=num,
                variable=radio_variable,
                command=lambda:self.manager.gametitle_select(radio_variable.get())
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

        self.stream_layout_window = StreamLayoutWidget(self.manager)
        self.menu_widget.add_command(
            label="レイアウトオブジェクト作成",
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
        self.menu = tk.Menu(self.window)
        self.window.config(menu=self.menu)

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
        self.object = Player(self.manager.game.title)
        self.menu.add_command(label="プレイヤー保存", command=self._save_data)
        self.menu.add_command(label="プレイヤー読み込み", command=self._load_data)

        left_frame = tk.Frame(self.window)
        left_widget_list = [
            [tk.Entry, {"width":23}, "名前"],
            [ttk.Combobox, {"width":20, "values":[character.name  for character in self.manager.game.character_list]}, "使用キャラ"],
            [ttk.Entry, {"width":23}, "所属チーム"]
        ]
        for index, widget in enumerate(left_widget_list):
            self._create_widget_add_label(index, left_frame, widget[0], widget[1], widget[2], True)
        left_frame.pack(side=tk.LEFT, padx=5)

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
        filename = self.widget_list["名前"].get()
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
        return "400x800"

    def window_create(self):
        super().window_create()
        self.menu.add_command(label="チーム保存", command=self._save_data)
        self.menu.add_command(label="チーム読み込み", command=self._load_data)
        self.object = Team(self.manager.game.title)

        top_frame = tk.Frame(self.window)
        top_frame.pack()
        team_name_entry_label = tk.Label(top_frame, text="チーム名")
        team_name_entry_label.grid(row=0, column=0, padx=5, pady=2)
        self.team_name_entry_box = tk.Entry(top_frame, width=23)
        self.team_name_entry_box.grid(row=0, column=1, padx=5, pady=2)
        self.object_image = self._create_imageTK(self.object.data.image, (100, 100))
        self.team_image_label = tk.Label(top_frame, image=self.object_image)
        self.team_image_label.grid(row=1, column=0, columnspan=2)
        team_image_button = tk.Button(top_frame, text="チームアイコン変更",
                                      command=self._change_team_image)
        team_image_button.grid(row=2, column=0, columnspan=2)

        team_length_frame = tk.LabelFrame(self.window, text="チーム人数", labelanchor="n",
                                          padx=5, pady=5)
        team_length_frame.pack()
        minus_button = tk.Button(team_length_frame, text="-", width=2,
                                 command=lambda:self.team_length_change(False))
        minus_button.pack(side=tk.LEFT)
        self.length_label = tk.Label(team_length_frame, text=self.object.data.length)
        self.length_label.pack(side=tk.LEFT, padx=5)
        plus_button = tk.Button(team_length_frame, text="+", width=2,
                                command=lambda:self.team_length_change(True))
        plus_button.pack(side=tk.LEFT)
        self.btm_frame = tk.Frame(self.window)
        self.btm_frame.pack()
        self.player_entry_box_update()

    def _change_team_image(self):
        image_path = super()._open_filedialogwindow("画像データ読み込み")
        if image_path:
            self.object.change_team_image(image_path)
            self.object_image = self._create_imageTK(image_path, (100, 100))
            self.team_image_label.config(image=self.object_image)

    def team_length_change(self, plus: bool):
        if plus:
            self.object.update_team_length(self.object.data.length +1)
        else:
            self.object.update_team_length(self.object.data.length -1)
        self.player_entry_box_update()

    def team_player_update(self, index: int):
        name = self.widget_list[index].get()
        self.object.data.player_list[index] = f"{name}.shd"

    def _save_data(self):
        filename = self.team_name_entry_box.get()
        self.object.data.name = filename
        save_path = super()._save_filedialogwindow(filename, "チームデータ保存", "Team")
        if save_path:
            self.object.save(save_path)

    def _load_data(self):
        open_path = super()._open_filedialogwindow("チームデータ読み込み", "Team")
        if open_path:
            self.object.load_team_data(open_path)
            self.team_name_entry_box.delete(0, tk.END)
        self.team_name_entry_box.insert(0, self.object.data.name)
        self.object_image = self._create_imageTK(self.object.data.image, (100, 100))
        self.team_image_label.config(image=self.object_image)
        self.player_entry_box_update()

    def player_entry_box_update(self):
        self.length_label.config(text=self.object.data.length)
        self.widget_list = []
        self.btm_frame.destroy()
        self.btm_frame = tk.Frame(self.window)
        self.btm_frame.pack()
        player_list = [name.replace(".shd", "") for name in self.manager.game.player_list]
        for num, player in enumerate(self.object.data.player_list):
            label = tk.Label(self.btm_frame, text=f"{num+1}人目")
            label.grid(row=num, column=0, padx=2, pady=2)
            entry_box = ttk.Combobox(self.btm_frame, values=player_list, width=40, state="readonly")
            entry_box.bind("<<ComboboxSelected>>", lambda e, num=num:self.team_player_update(num))
            entry_box.set(player.replace(".shd", ""))
            self.widget_list.append(entry_box)
            entry_box.grid(row=num, column=1)


class StreamLayoutWidget(NewWindow):
    def __init__(self, manager: Manager):
        super().__init__(manager)

    def get_window_title(self):
        return f"レイアウトオブジェクト作成画面__{self.manager.game.title}"

    def get_window_size(self):
        return "1500x600"

    def _canvas_create_const_image_object(self):
        filepath = self._open_filedialogwindow("画像読み込み")
        if filepath:
            self.canvas.add_const_image_object(filepath)

    def _canvas_create_variable_image_object(self, frame: CustomLabelFrame, text=False):
        if not text:
            if frame.box.get() == "":
                messagebox.showerror("Error", "Comboboxが選択されていません", parent=self.window)
            else:
                self.canvas.add_image_object(frame.box.get(), frame.parent_label)
        else:
            self.canvas.add_image_object(text, frame.parent_label)

    def _canvas_create_variable_text_object(self, frame: CustomLabelFrame, text=False):
        print(text)
        if not text:
            if frame.box.get() == "":
                messagebox.showerror("Error", "Comboboxが選択されていません", parent=self.window)
            else:
                self.canvas.add_text_object(frame.box.get(), frame.parent_label)
        else:
            self.canvas.add_text_object(text, frame.parent_label)


    def window_create(self):
        super().window_create()
        self.menu.add_command(label="レイアウトオブジェクト保存")
        self.menu.add_command(label="レイアウトオブジェクト読み込み")

        left_frame = ScrollFrame(self.window)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        font_list = os.listdir("StreamHelper/Font")

        image_label_frame = CustomLabelFrame(left_frame.frame, text="画像を追加")
        image_label_frame.pack(fill=tk.X, pady=5)
        image_label_frame.create_button("画像読み込み")
        image_label_frame.widgets["画像読み込み"].config(command=self._canvas_create_const_image_object)

        text_label_frame = CustomLabelFrame(left_frame.frame, text="テキストを追加")
        text_label_frame.pack(fill=tk.X, pady=5)
        text_label_frame.create_font_box(font_list)
        text_label_frame.create_button("テキスト追加")

        player_label_frame = CustomLabelFrame(left_frame.frame, text="プレイヤー")
        player_label_frame.pack(fill=tk.X, pady=5)
        player_image_frame = CustomLabelFrame(player_label_frame, text="画像")
        player_image_frame.pack(padx=5, pady=5)
        player_image_frame.create_commbo_box(["プレイヤー画像", "キャラクター画像", "所属チームアイコン"])
        player_image_frame.create_button("生成")
        player_image_frame.widgets["生成"].config(command=lambda: self._canvas_create_variable_image_object(player_image_frame))
        player_text_frame = CustomLabelFrame(player_label_frame, text="テキスト")
        player_text_frame.pack(padx=5, pady=5)
        player_text_frame.create_commbo_box(["プレイヤー名", "キャラクター名", "所属チーム名"])
        player_text_frame.create_button("生成")
        player_text_frame.widgets["生成"].config(command=lambda: self._canvas_create_variable_text_object(player_text_frame))

        team_label_frame = CustomLabelFrame(left_frame.frame, text="チーム")
        team_label_frame.pack(fill=tk.X, pady=5)
        team_label_frame.create_button("チーム名生成")
        team_label_frame.widgets["チーム名生成"].config(command=lambda: self._canvas_create_variable_text_object(team_label_frame, "チーム名"))
        team_label_frame.create_button("チーム画像生成")
        team_label_frame.widgets["チーム画像生成"].config(command=lambda: self._canvas_create_variable_image_object(team_label_frame, "チーム画像"))
        team_image_frame = CustomLabelFrame(team_label_frame, text="画像")
        team_image_frame.pack(padx=5, pady=5)
        team_image_frame.create_commbo_box(["プレイヤー画像", "キャラクター画像"])
        team_image_frame.create_button("生成")
        team_image_frame.widgets["生成"].config(command=lambda: self._canvas_create_variable_image_object(team_image_frame))
        team_text_frame = CustomLabelFrame(team_label_frame, text="テキスト")
        team_text_frame.pack(padx=5, pady=5)
        team_text_frame.create_commbo_box(["プレイヤー名", "キャラクター名"])
        team_text_frame.create_button("生成")
        team_text_frame.widgets["生成"].config(command=lambda: self._canvas_create_variable_text_object(team_text_frame))

        counter_label_frame = CustomLabelFrame(left_frame.frame, text="カウンター")
        counter_label_frame.pack(fill=tk.X, pady=5)
        counter_label_frame.create_button("数字を追加")
        counter_label_frame.create_button("カウンター用画像を追加")

        right_frame = ScrollFrame(self.window)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=True)
        frame_rock_label = tk.Label(right_frame.frame, width=40)
        frame_rock_label.pack(side=tk.BOTTOM)

        canvas_frame = tk.Frame(self.window)
        canvas_frame.pack(side=tk.LEFT)
        canvas_top_frame = tk.Frame(canvas_frame)
        canvas_top_frame.pack()
        canvas_color_box = tk.Button(canvas_top_frame, text="キャンバスの色変更",
                                     command=self.canvas_color_change)
        canvas_color_box.pack(side=tk.LEFT, padx=10)
        canvas_size_label = tk.Label(canvas_top_frame, text="キャンバスサイズ")
        canvas_size_label.pack(side=tk.LEFT, padx=5)
        canvas_size_box = ttk.Combobox(canvas_top_frame, values=["キャンパスサイズ変更（未実装）","960x540", "1920x1080"])
        canvas_size_box.current(0)
        canvas_size_box.pack(side=tk.LEFT)

        self.canvas = CustomCanvas(canvas_frame, right_frame.frame, width=960, height=540, bg="green", highlightthickness=0)
        self.canvas.pack(padx=5, pady=5)

    def canvas_color_change(self):
        color = colorchooser.askcolor(parent=self.window)
        if color[0] != None:
            self.canvas.config(bg=color[1])





def main():
	win = tk.Tk()
	app = Application(master=win)
	app.mainloop()


if __name__ == "__main__":
    main()
