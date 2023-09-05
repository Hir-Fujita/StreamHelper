#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from tkinter import ttk, colorchooser
from typing import Union, Callable
import random
import Object as Obj

def get_filename(path: str):
    filename = os.path.splitext(os.path.basename(path))[0]
    return filename

def random_id(n):
    return str(random.randrange(10**(n-1),10**n))

class ScrollFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        scrollbar = ttk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas = tk.Canvas(self, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        scrollbar.config(command=self.canvas.yview)
        self.frame = ttk.Frame(self.canvas, borderwidth=0)
        self.frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        # self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.configure(width=event.width)

class ManagerChildrenFrame(tk.Frame):
    def __init__(self, parent, manager, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.manager = manager
        self.pack()

    def get(self, id:str="") -> str:
        val = self.box.get()
        return val

class ManagerPlayerFrame(ManagerChildrenFrame):
    def __init__(self, parent, manager, *args, **kwargs):
        ManagerChildrenFrame.__init__(self, parent, manager, text="Player", *args, **kwargs)
        self.cls = "ManagerPlayerFrame"
        player_list = [get_filename(player) for player in self.manager.game.player_list]
        self.box = ttk.Combobox(self, values=player_list)
        self.box.pack(padx=5, pady=2)

class ManagerTeamFrame(ManagerChildrenFrame):
    def __init__(self, parent, manager, length: int, id_dict: "dict[str: str]", *args, **kwargs):
        ManagerChildrenFrame.__init__(self, parent, manager, text="Team", *args, **kwargs)
        self.cls = "ManagerTeamFrame"
        self.id_dict = id_dict
        self.player_list = []
        self.team_name_box_frame = tk.LabelFrame(self, text="チーム選択")
        self.team_name_box_frame.pack(padx=2)
        team_list = [get_filename(team) for team in self.manager.game.team_list]
        self.team_name_box = ttk.Combobox(self.team_name_box_frame, values=team_list)
        self.team_name_box.bind("<<ComboboxSelected>>", lambda e:self.team_name_select())
        self.team_name_box.pack(padx=5, pady=2)
        self.player_frame = tk.LabelFrame(self, text="プレイヤー選択")
        self.player_frame.pack(padx=2)
        self.box_list = [ttk.Combobox(self.player_frame) for i in range(length)]
        [box.pack(padx=5, pady=2) for box in self.box_list]
        [box.bind("<Button-1>", lambda e:self.box_select()) for box in self.box_list]

    def team_name_select(self):
        name = f"{self.team_name_box.get()}.shd"
        self.player_list = [get_filename(player) for player in Obj.Team.load(f"StreamHelper/Gametitle/{self.manager.game.title}/team/{name}").data.player_list]
        [box.config(values=self.player_list) for box in self.box_list]

    def box_select(self):
        new_player_list = self.player_list.copy()
        current_list = [box.get() for box in self.box_list if box.get()]
        [new_player_list.remove(current) for current in current_list if current in new_player_list]
        [box.config(values=new_player_list) for box in self.box_list]

    def get(self, id: str) -> "dict[str: str]":
        return_dict = {}
        return_dict[id] = self.team_name_box.get()
        for key in self.id_dict.keys():
            index = self.id_dict[key]
            val = self.box_list[index].get()
            return_dict[key] = val
        return return_dict

class ManagerCounterTextFrame(ManagerChildrenFrame):
    def __init__(self, parent, manager, *args, **kwargs):
        ManagerChildrenFrame.__init__(self, parent, manager, text="CounterText", *args, **kwargs)
        self.cls = "ManagerCounterTextFrame"
        self.box = ttk.Combobox(self, values=list(range(10)))
        self.box.pack(padx=5, pady=2)

class ManagerCounterImageFrame(ManagerChildrenFrame):
    def __init__(self, parent, manager, data: Obj.LayoutData, *args, **kwargs):
        ManagerChildrenFrame.__init__(self, parent, manager, text="CounterImage", *args, **kwargs)
        self.cls = "ManagerCounterImageFrame"
        self.box = ttk.Combobox(self, values=list(data.image_list.keys()), state="readonly")
        self.box.pack(padx=5, pady=2)



class CustomCanvas(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        tk.Canvas.__init__(self, parent, *args, **kwargs)
        self.bind("<Button-1>", lambda event:self.left_click(event))
        self.bind("<Button1-Motion>", lambda event:self.mouse_drag(event))
        self.bind("<ButtonRelease>", lambda event:self.mouse_release())
        self.bind("<Button-3>", lambda event:self.right_click(event))
        self.resize_direction = False
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Delete", command=self.delete_object)

    def _create_canvas_object(self):
        raise NotImplementedError

    def delete_object(self):
        raise NotImplementedError

    def image_move(self, id: str, x: int, y: int):
        self.move(id, x, y)

    def image_re_create(self, object: Obj.UNION_OBJECT):
        bbox = self.find_bbox(object.id)
        self.delete(object.id)
        self.create_image(
            (bbox[0] + bbox[2]) /2,
            (bbox[1] + bbox[3]) /2,
            anchor="center",
            image=object.image_tk,
            tag=object.id
            )
        self.image_select(object.id)
        self.layer_update()

    def image_select(self, image_id):
        self.rect_delete()
        self.move_tag_delete()
        self.tag = (image_id, "current")
        self.addtag_withtag("move", image_id)
        self._create_rect(self.find_bbox(image_id))

    def mouse_drag(self, event):
        if self.resize_direction:
            self.resize_rect(event)
        elif self.tag:
            self.move(
                "move",
                event.x - self.x,
                event.y - self.y
                )
            self.x = event.x
            self.y = event.y
            self.object_position_update(self.tag[0])

    def resize_rect(self, event):
        raise NotImplementedError

    def object_position_update(self, id: str):
        raise NotImplementedError

    def find_tag(self, event):
        closest_ids = self.find_closest(event.x, event.y)
        if len(closest_ids) != 0:
            tag = self.gettags(closest_ids[0])
            return tag
        return False

    def tag_get_all(self):
        ids = self.find_all()
        tags = [self.gettags(tag) for tag in ids]
        return tags

    def find_bbox(self, name):
        bbox = self.bbox(name)
        return bbox

    def rect_delete(self):
        tags = self.tag_get_all()
        for tag in tags:
            if "rect" in tag[0]:
                self.delete(tag[0])

    def resize_check(self, tag):
        if "rect_" in tag[0]:
            self.resize_direction = tag[0]
            return True
        else:
            self.rect_delete()
            self.resize_direction = False
            return False

    def move_tag_delete(self):
        tags = self.tag_get_all()
        for tag in tags:
            if "move" in tag:
                self.dtag(tag[0], "move")

    def left_click(self, event):
        tag = self.find_tag(event)
        if tag:
            if tag[-1] == "current":
                if not self.resize_check(tag) and tag[0] != "rect":
                    self.image_select(tag[0])
                    self.tag = tag
                    self.x = event.x
                    self.y = event.y
            else:
                self.rect_delete()
                self.tag = False

    def right_click(self, event):
        tag = self.find_tag(event)
        if tag:
            if tag[-1] == "current":
                self.tag = tag
                self.menu.post(event.x_root, event.y_root)

    def _create_rect(self, bbox):
        rect_size = 3
        rect_color = "red"
        x_middle = (bbox[0] + bbox[2]) /2
        y_middle = (bbox[1] + bbox[3]) /2
        self.create_rectangle(
            bbox[0],
            bbox[1],
            bbox[2],
            bbox[3],
            width=2,
            tag=("rect", "move")
            )
        left_top = self.create_rectangle(
            bbox[0] -rect_size,
            bbox[1] -rect_size,
            bbox[0] +rect_size,
            bbox[1] +rect_size,
            fill=rect_color,
            tag=(f"rect_left_top", "move")
            )
        right_top = self.create_rectangle(
            bbox[2] -rect_size,
            bbox[1] -rect_size,
            bbox[2] +rect_size,
            bbox[1] +rect_size,
            fill=rect_color,
            tag=(f"rect_right_top", "move")
            )
        left_bottom = self.create_rectangle(
            bbox[0] -rect_size,
            bbox[3] -rect_size,
            bbox[0] +rect_size,
            bbox[3] +rect_size,
            fill=rect_color,
            tag=(f"rect_left_bottom", "move")
            )
        right_bottom = self.create_rectangle(
            bbox[2] -rect_size,
            bbox[3] -rect_size,
            bbox[2] +rect_size,
            bbox[3] +rect_size,
            fill=rect_color,
            tag=(f"rect_right_bottom", "move")
            )
        top = self.create_rectangle(
            x_middle -rect_size,
            bbox[1] -rect_size,
            x_middle +rect_size,
            bbox[1] +rect_size,
            fill=rect_color,
            tag=(f"rect_top", "move")
            )
        bottom = self.create_rectangle(
            x_middle -rect_size,
            bbox[3] -rect_size,
            x_middle +rect_size,
            bbox[3] +rect_size,
            fill=rect_color,
            tag=(f"rect_bottom", "move")
            )
        left = self.create_rectangle(
            bbox[0] -rect_size,
            y_middle -rect_size,
            bbox[0] +rect_size,
            y_middle +rect_size,
            fill=rect_color,
            tag=(f"rect_left", "move")
            )
        right = self.create_rectangle(
            bbox[2] -rect_size,
            y_middle -rect_size,
            bbox[2] +rect_size,
            y_middle +rect_size,
            fill=rect_color,
            tag=(f"rect_right", "move")
            )
        self.tag_bind(left_top,  "<Enter>", lambda event:self.on_mouse_enter("ul_angle"))
        self.tag_bind(left_top,  "<Leave>", lambda event:self.on_mouse_leave())
        self.tag_bind(right_top,  "<Enter>", lambda event:self.on_mouse_enter("ur_angle"))
        self.tag_bind(right_top,  "<Leave>", lambda event:self.on_mouse_leave())
        self.tag_bind(left_bottom,  "<Enter>", lambda event:self.on_mouse_enter("ll_angle"))
        self.tag_bind(left_bottom,  "<Leave>", lambda event:self.on_mouse_leave())
        self.tag_bind(right_bottom,  "<Enter>", lambda event:self.on_mouse_enter("lr_angle"))
        self.tag_bind(right_bottom,  "<Leave>", lambda event:self.on_mouse_leave())
        self.tag_bind(top,  "<Enter>", lambda event:self.on_mouse_enter("sb_v_double_arrow"))
        self.tag_bind(top,  "<Leave>", lambda event:self.on_mouse_leave())
        self.tag_bind(bottom,  "<Enter>", lambda event:self.on_mouse_enter("sb_v_double_arrow"))
        self.tag_bind(bottom,  "<Leave>", lambda event:self.on_mouse_leave())
        self.tag_bind(left,  "<Enter>", lambda event:self.on_mouse_enter("sb_h_double_arrow"))
        self.tag_bind(left,  "<Leave>", lambda event:self.on_mouse_leave())
        self.tag_bind(right,  "<Enter>", lambda event:self.on_mouse_enter("sb_h_double_arrow"))
        self.tag_bind(right,  "<Leave>", lambda event:self.on_mouse_leave())

    def on_mouse_enter(self, anchor: str):
        self.config(cursor=anchor)

    def on_mouse_leave(self):
        self.config(cursor="arrow")

    def mouse_release(self):
        self.move_tag_delete()
        if self.resize_direction:
            self.resize_direction = False
            self.image_select(self.tag[0])
            self.on_mouse_leave()

    def layer_update(self):
        raise NotImplementedError

class LayoutObjectCanvas(CustomCanvas):
    def __init__(self, parent, dataframe, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.dict = LayoutObjectCustomList(self, dataframe)

    def save_check(self) -> bool:
        result = [obj.object.position for obj in self.dict.dict.values()]
        for res in result:
            if res[0] < 0 or res[1] < 0 or res[2] > 960 or res[3] > 540:
                return False
        return True

    def save_layouts(self) -> "list[Obj.LayoutElement]":
        save_list = [obj.save_object() for obj in self.dict.dict.values()]
        return save_list

    def add_object(self, class_name: str, name: str, category: str):
        object = Obj.layout_element_check(class_name)(name, category, f"id_{random_id(10)}")
        self.dict.add_object(object)

    def add_const_image_object(self, path: str):
        object = Obj.ConstImageLayoutObject(path, "Const", f"id_{random_id(10)}")
        self.dict.add_object(object)

    def add_counter_image_object(self, name: str, category: str, folder_path: str):
        object = Obj.CounterImageLayoutObject(name=name, category=category, id=f"id_{random_id(10)}", folder_path=folder_path)
        self.dict.add_object(object)

    def _create_canvas_object(self, obj: Obj.UNION_OBJECT):
        self.create_image(
            (obj.position[2] + obj.position[0])/2,
            (obj.position[3] + obj.position[1])/2,
            anchor="center",
            image=obj.image_tk,
            tag=obj.id
            )
        self.lower(obj.id)
        self.object_position_update(obj.id)

    def delete_object(self):
        self.rect_delete()
        self.delete(self.tag[0])
        self.dict.delete_object(self.tag[0])
        self.tag = False

    def object_position_update(self, tag):
        position = self.find_bbox(tag)
        self.dict.object_position_update(tag, position)

    def image_select(self, image_id):
        super().image_select(image_id)
        self.dict.label_frame_select(image_id)

    def resize_rect(self, event):
        self.rect_delete()
        bbox = self.find_bbox(self.tag[0])
        if self.resize_direction == "rect_top":
            pos = (bbox[0], event.y, bbox[2], bbox[3])
        elif self.resize_direction == "rect_bottom":
            pos = (bbox[0], bbox[1], bbox[2], event.y)
        elif self.resize_direction == "rect_left":
            pos = (event.x, bbox[1], bbox[2], bbox[3])
        elif self.resize_direction == "rect_right":
            pos = (bbox[0], bbox[1], event.x, bbox[3])
        elif self.resize_direction == "rect_left_top":
            pos = (event.x, event.y, bbox[2], bbox[3])
        elif self.resize_direction == "rect_right_top":
            pos = (bbox[0], event.y, event.x, bbox[3])
        elif self.resize_direction == "rect_left_bottom":
            pos = (event.x, bbox[1], bbox[2], event.y)
        elif self.resize_direction == "rect_right_bottom":
            pos = (bbox[0], bbox[1], event.x, event.y)
        width = pos[2] - pos[0]
        height = pos[3] - pos[1]
        if width > 5 and height > 5:
            self.delete(self.tag[0])
            self.dict.dict[self.tag[0]].object.resize((pos[2] - pos[0],
                                                       pos[3] - pos[1]))
            self.create_image(
                pos[0],
                pos[1],
                anchor="nw",
                image=self.dict.dict[self.tag[0]].object.image_tk,
                tag=self.tag[0]
                )
            self.object_position_update(self.tag[0])
            self.dict.object_size_update(self.tag[0])

    def mouse_release(self):
        super().mouse_release()
        self.layer_update()

    def layer_update(self):
        [self.lower(key) for key in self.dict.dict]



class LayoutCanvas(CustomCanvas):
    def __init__(self, parent, layout_manager, frame: ScrollFrame, *args, **kwargs):
        import Manager
        super().__init__(parent, *args, **kwargs)
        self.layout_manager: Manager.LayoutManager = layout_manager
        self.frame = frame
        self.widgets: "dict[str: LayoutViewer]" = self.layout_manager.widgets
        self.resize_direction = False
        self.tag = False

    def add_layout(self, obj: Obj.LayoutCollection):
        self.layout_manager.add_layout_collection(obj)
        self.create_image(
            (obj.position[2] + obj.position[0])/2,
            (obj.position[3] + obj.position[1])/2,
            anchor="center",
            image=obj.image_tk,
            tag=obj.id
            )
        self.widgets[obj.id] = LayoutViewer(obj, self.frame, self.image_re_create)

    def re_create(self, id: str=""):
        if id:
            self.widgets[id].frame_pack_forget()
            self.layout_manager.delete_layout_collection(self.tag[0])
            del self.widgets[self.tag[0]]
        else:
            [self.add_layout(collection) for collection in self.layout_manager.layout_dic.values()]

    def object_position_update(self, tag):
        position = self.find_bbox(tag)
        self.layout_manager.position_update(tag, position)
        self.widgets[tag].position_update()

    def object_size_update(self, tag: str, width: int, height: int):
        self.layout_manager.size_update(tag, (width, height))
        self.widgets[tag].size_update()

    def resize_rect(self, event):
        self.rect_delete()
        bbox = self.find_bbox(self.tag[0])
        if self.resize_direction == "rect_top":
            pos = (bbox[0], event.y, bbox[2], bbox[3])
        elif self.resize_direction == "rect_bottom":
            pos = (bbox[0], bbox[1], bbox[2], event.y)
        elif self.resize_direction == "rect_left":
            pos = (event.x, bbox[1], bbox[2], bbox[3])
        elif self.resize_direction == "rect_right":
            pos = (bbox[0], bbox[1], event.x, bbox[3])
        elif self.resize_direction == "rect_left_top":
            pos = (event.x, event.y, bbox[2], bbox[3])
        elif self.resize_direction == "rect_right_top":
            pos = (bbox[0], event.y, event.x, bbox[3])
        elif self.resize_direction == "rect_left_bottom":
            pos = (event.x, bbox[1], bbox[2], event.y)
        elif self.resize_direction == "rect_right_bottom":
            pos = (bbox[0], bbox[1], event.x, event.y)
        width = pos[2] - pos[0]
        height = pos[3] - pos[1]
        if width > 5 and height > 5:
            self.delete(self.tag[0])
            self.object_size_update(self.tag[0], width, height)
            self.create_image(
                pos[0],
                pos[1],
                anchor="nw",
                image=self.layout_manager.layout_dic[self.tag[0]].image_tk,
                tag=self.tag[0]
                )
            self.object_position_update(self.tag[0])

    def image_re_create(self, obj: Obj.LayoutCollection):
        self.delete(obj.id)
        self.create_image(
                obj.position[0],
                obj.position[1],
                anchor="nw",
                image=obj.image_tk,
                tag=obj.id
                )

    def delete_object(self):
        self.rect_delete()
        self.delete(self.tag[0])
        self.re_create(self.tag[0])
        self.layout_manager.delete_widget(self.tag[0])
        self.tag = False



class CustomLabelFrame(tk.LabelFrame):
    def __init__(self, parent, text="", *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, text=text, *args, **kwargs)
        if isinstance(parent, CustomLabelFrame):
            self.parent_label = parent.label
        else:
            self.parent_label = ""
        self.label = text
        self.widgets = {}

    def create_button(self, text: str, width=20, padx=5, pady=5):
        button = tk.Button(self, text=text, width=width)
        button.pack(padx=padx, pady=pady)
        self.widgets[text] = button

    def create_commbo_box(self, values=[], width=20, padx=5, pady=5):
        self.box = ttk.Combobox(self, values=values, width=width)
        self.box.pack(padx=padx, pady=pady)

    def create_font_box(self, font_list, width=20, padx=5, pady=5):
        self.font_box = ttk.Combobox(self, values=font_list, width=width)
        self.font_box.set("フォントを選択")
        self.font_box.pack(padx=padx, pady=pady)

class CustomEntry(tk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.value = tk.StringVar()
        self.box = tk.Entry(self, width=18, textvariable=self.value)
        self.box.pack(padx=2, pady=2)

    def set(self, text: str):
        self.value.set(text)

    def get(self) -> str:
        return self.value.get()

class CustomSpinbox(tk.LabelFrame):
    def __init__(self, parent, width: int, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.value = tk.IntVar()
        self.box = tk.Spinbox(self, width=width, increment=1, from_=1, to=9999, textvariable=self.value)
        self.box.pack(padx=2, pady=2)

    def set(self, value: int):
        self.value.set(value)

    def get(self) -> int:
        return self.value.get()

class CustomCombobox(tk.LabelFrame):
    def __init__(self, parent, values, width=18, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.box = ttk.Combobox(self, width=width, values=values, state="readonly")
        self.box.pack(padx=2, pady=2)
        self.set(values[1])

    def set(self, value: str):
        self.box.set(value)

    def get(self) -> str:
        return self.box.get()

class CustomFontCombobox(tk.LabelFrame):
    def __init__(self, parent, width=18, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.box = ttk.Combobox(self, width=width, values=os.listdir("StreamHelper/Font"), state="readonly")
        self.box.pack(padx=2, pady=2)
        if "meiryo.ttc" in os.listdir("StreamHelper/Font"):
            self.set("meiryo.ttc")
        else:
            self.box.current(0)

    def set(self, value: str):
        self.box.set(value)

    def get(self) -> str:
        return self.box.get()

class FontWidget:
    def __init__(self, object: Obj.UNION_OBJECT, parent: tk.Frame):
        self.window = None
        self.object = object
        self.create_button_image()
        self.button = tk.Button(parent, image=self.image, command=self.create_window)

    def create_button_image(self):
        image = Obj.create_text_image(
            "フォント設定",
            self.object.font,
            (200, 20)
        )
        self.image = Obj.image_tk(image)

    def font_update(self):
        self.object.font.font = self.font_box.get()
        self.object.font.anchor = self.anchor_box.get()
        self.object.font.stroke_width = int(self.width_box.get())
        self.create_button_image()
        self.button.config(image=self.image)
        self.image_label.config(image=self.image)

    def create_window(self):
        if self.window is not None:
            self.window.destroy()
        self.window = tk.Toplevel()
        self.window.geometry("300x400")
        self.window.title("フォント設定")
        label_frame = tk.LabelFrame(self.window, text="フォントイメージ")
        label_frame.pack()
        self.image_label = tk.Label(label_frame, image=self.image)
        self.image_label.pack(padx=2, pady=2)
        color_box = tk.Button(self.window, text="文字色", command=lambda: self.color_change(color_box, "fill"), width=18,
                              bg=self.object.font.fill, fg=Obj.color_reverse(self.object.font.fill))
        color_box.pack()
        self.font_box = CustomFontCombobox(self.window, text="使用フォント")
        self.font_box.set(self.object.font.font)
        self.font_box.box.bind("<<ComboboxSelected>>", lambda e: self.font_update())
        self.font_box.pack()
        self.anchor_box = CustomCombobox(self.window, ["左寄", "中央", "右寄"], text="Grid")
        self.anchor_box.set(self.object.font.anchor)
        self.anchor_box.box.bind("<<ComboboxSelected>>", lambda e: self.font_update())
        self.anchor_box.pack()
        self.width_box = CustomCombobox(self.window, [num for num in range(51)], text="縁幅")
        self.width_box.set(self.object.font.stroke_width)
        self.width_box.box.bind("<<ComboboxSelected>>", lambda e: self.font_update())
        self.width_box.pack()
        stroke_fill_box = tk.Button(self.window, text="縁色", command=lambda: self.color_change(stroke_fill_box, "stroke_fill"), width=18,
                                    bg=self.object.font.stroke_fill, fg=Obj.color_reverse(self.object.font.stroke_fill))
        stroke_fill_box.pack()

    def color_change(self, widget: tk.Button, value):
        color = colorchooser.askcolor(parent=self.window)
        if color[0] != None:
            if value == "fill":
                self.object.font.fill = color[1]
            elif value == "stroke_fill":
                self.object.font.stroke_fill = color[1]
            widget.config(bg=color[1])
            widget.config(fg=Obj.color_reverse(color[1]))
            self.font_update()

class PositionWidget:
    def __init__(self, object: Obj.UNION_OBJECT, parent: tk.Tk, method: Callable):
        self.object = object
        self.method = method
        self.frame = tk.Frame(parent)
        self.pos_left_box = CustomSpinbox(self.frame, 5, text="LEFT")
        self.pos_left_box.pack(side=tk.LEFT, padx=3, pady=2)
        self.pos_top_box = CustomSpinbox(self.frame, 5, text="TOP")
        self.pos_top_box.pack(side=tk.LEFT, padx=3, pady=2)
        self.pos_right_box = CustomSpinbox(self.frame, 5, text="RIGHT")
        self.pos_right_box.pack(side=tk.LEFT, padx=3, pady=2)
        self.pos_bottom_box = CustomSpinbox(self.frame, 5, text="BOTTOM")
        self.pos_bottom_box.pack(side=tk.LEFT, padx=3, pady=2)
        self.pos_left_box.box.config(command=lambda: self.image_move("LEFT"))
        self.pos_left_box.box.bind("<KeyRelease>", lambda e: self.image_move("LEFT"))
        self.pos_left_box.box.bind("<MouseWheel>", lambda event: self.mouse_scroll(event, "LEFT", self.pos_left_box))
        self.pos_top_box.box.config(command=lambda: self.image_move("TOP"))
        self.pos_top_box.box.bind("<KeyRelease>", lambda e: self.image_move("TOP"))
        self.pos_top_box.box.bind("<MouseWheel>", lambda event: self.mouse_scroll(event, "TOP", self.pos_top_box))
        self.pos_right_box.box.config(command=lambda: self.image_move("RIGHT"))
        self.pos_right_box.box.bind("<KeyRelease>", lambda e: self.image_move("RIGHT"))
        self.pos_right_box.box.bind("<MouseWheel>", lambda event: self.mouse_scroll(event, "RIGHT", self.pos_right_box))
        self.pos_bottom_box.box.config(command=lambda: self.image_move("BOTTOM"))
        self.pos_bottom_box.box.bind("<KeyRelease>", lambda e: self.image_move("BOTTOM"))
        self.pos_bottom_box.box.bind("<MouseWheel>", lambda event: self.mouse_scroll(event, "BOTTOM", self.pos_bottom_box))

    def mouse_scroll(self, event, anchor: str, widget: CustomSpinbox):
        if event.delta > 0:
            widget.set(widget.get() -10)
        elif event.delta < 0:
            widget.set(widget.get() +10)
        self.image_move(anchor)

    def image_move(self, anchor: str):
        x, y = 0, 0
        if anchor == "LEFT":
            value = self.pos_left_box.get()
            other_value = value + self.object.width
            x = other_value - self.object.position[2]
            self.position_update([value, self.object.position[1], other_value, self.object.position[3]])
        elif anchor == "TOP":
            value = self.pos_top_box.get()
            other_value = value + self.object.height
            y = other_value - self.object.position[3]
            self.position_update([self.object.position[0], value, self.object.position[2], other_value])
        elif anchor == "RIGHT":
            value = self.pos_right_box.get()
            other_value = value - self.object.width
            x = other_value - self.object.position[0]
            self.position_update([other_value, self.object.position[1], value, self.object.position[3]])
        elif anchor == "BOTTOM":
            value = self.pos_bottom_box.get()
            other_value = value - self.object.height
            y = other_value - self.object.position[1]
            self.position_update([self.object.position[0], other_value, self.object.position[2], value])
        self.method(self.object.id, x, y)

    def position_update(self, position: "list[int]"):
        self.object.position = position
        self.pos_left_box.set(position[0])
        self.pos_top_box.set(position[1])
        self.pos_right_box.set(position[2])
        self.pos_bottom_box.set(position[3])
        self.pos_left_box.box.config(fg="red") if self.object.position[0] < 0 else self.pos_left_box.box.config(fg="black")
        self.pos_top_box.box.config(fg="red") if self.object.position[1] < 0 else self.pos_top_box.box.config(fg="black")
        self.pos_right_box.box.config(fg="red") if self.object.position[2] > 960 else self.pos_right_box.box.config(fg="black")
        self.pos_bottom_box.box.config(fg="red") if self.object.position[3] > 540 else self.pos_bottom_box.box.config(fg="black")

class LayoutObjectViewer:
    def __init__(self, object: Obj.UNION_OBJECT, frame: tk.Tk, method: Callable, move_method: Callable, resize_method: Callable):
        self.object = object
        self.method = method
        self.move_method = move_method
        self.resize_method = resize_method
        self.frame = tk.LabelFrame(frame, text=object.cls, relief=tk.SOLID, bd=2)
        self.frame.pack(pady=2)
        box_frame = tk.Frame(self.frame)
        box_frame.pack(side=tk.RIGHT)
        self.name_box = CustomEntry(box_frame, text="Name")
        self.name_box.grid(row=0, column=0, padx=2, pady=2)
        self.name_box.set(object.name)
        self.id_box = CustomEntry(box_frame, text="ID")
        self.id_box.grid(row=0, column=1, padx=2, pady=2)
        self.id_box.set(object.id)
        self.width_box = CustomSpinbox(box_frame, 10, text="Width")
        self.width_box.box.config(command=lambda: self.resize())
        self.width_box.box.bind("<KeyRelease>", lambda e: self.resize())
        self.width_box.box.bind("<MouseWheel>", lambda event: self.mouse_scroll(event, self.width_box))
        self.width_box.grid(row=1, column=0, padx=2, pady=2)
        self.heigth_box = CustomSpinbox(box_frame, 10, text="Heigth")
        self.heigth_box.box.config(command=lambda: self.resize())
        self.heigth_box.box.bind("<KeyRelease>", lambda e: self.resize())
        self.heigth_box.box.bind("<MouseWheel>", lambda event: self.mouse_scroll(event, self.heigth_box))
        self.heigth_box.grid(row=1, column=1, padx=2, pady=2)
        self.size_update()
        self.position_widget = PositionWidget(self.object, box_frame, self.move_method)
        self.position_widget.frame.grid(row=2, column=0, columnspan=2, padx=2, pady=2)
        if "Text" in object.cls:
            self.font_widget = FontWidget(self.object, box_frame)
            self.font_widget.button.grid(row=3, column=0, columnspan=2, padx=2, pady=2)
        button_frame = tk.Frame(self.frame)
        button_frame.pack(side=tk.RIGHT)
        up_button = tk.Button(button_frame, text="▲", command=self.up_button_click)
        up_button.pack(side=tk.TOP, padx=2, pady=5)
        down_button = tk.Button(button_frame, text="▼", command=self.down_button_click)
        down_button.pack(side=tk.BOTTOM, padx=2, pady=5)

    def mouse_scroll(self, event, widget: CustomSpinbox):
        if event.delta > 0:
            widget.set(widget.get() -10)
        elif event.delta < 0:
            widget.set(widget.get() +10)
        self.resize()

    def resize(self):
        self.object.resize((self.width_box.get(), self.heigth_box.get()))
        self.resize_method(self.object)

    def size_update(self):
        self.width_box.set(self.object.width)
        self.heigth_box.set(self.object.height)

    def position_update(self, position):
        self.position_widget.position_update(position)

    def re_pack(self):
        self.frame.pack()

    def frame_pack_forget(self):
        self.frame.pack_forget()

    def up_button_click(self):
        self.method(self.object.id, True)

    def down_button_click(self):
        self.method(self.object.id, False)

    def save_object(self):
        self.size_update()
        self.object.position = [
            self.position_widget.pos_left_box.get(),
            self.position_widget.pos_top_box.get(),
            self.position_widget.pos_right_box.get(),
            self.position_widget.pos_bottom_box.get()
        ]
        return self.object.save_cls()


class LayoutObjectCustomList:
    def __init__(self, canvas: CustomCanvas, dataframe):
        self.dict: dict[str, LayoutObjectViewer] = {}
        self.canvas = canvas
        self.frame = dataframe

    def load(self, list: "list[LayoutObjectViewer]"):
        self.dict = {obj.object.id: obj for obj in list}

    def add_object(self, obj: Obj.UNION_OBJECT):
        self.dict[obj.id] = LayoutObjectViewer(obj, self.frame, self.layer_update, self.canvas_move_position, self.canvas_image_re_create)
        self.dict[obj.id].frame.bind("<Button-1>", lambda event:self.canvas.image_select(obj.id))
        self.canvas._create_canvas_object(obj)

    def delete_object(self, id: str):
        self.canvas.delete(id)
        self.dict[id].frame.destroy()
        del self.dict[id]

    def load_object_list(self, load_list: "list[Obj.LayoutElement]"):
        self.canvas.rect_delete()
        [self.delete_object(obj.object.id) for obj in list(self.dict.values()) if isinstance(obj, LayoutObjectViewer)]
        [self.add_object(Obj.layout_element_check(obj).load_cls(obj)) for obj in load_list]

    def object_position_update(self, id: str, position: "list[int]"):
        self.dict[id].position_update(position)

    def object_size_update(self, id: str):
        self.dict[id].size_update()

    def label_frame_select(self, id: str):
        if len(self.dict) > 0:
            [obj.frame.config(bg="SystemButtonFace") for obj in self.dict.values()]
        self.dict[id].frame.config(bg="red")

    def layer_update(self, id: str, upper: bool):
        new_dict = {index: obj for (index, obj) in enumerate(self.dict.values())}
        target = [obj for obj in self.dict.values() if obj.object.id == id][0]
        index = [key for key, value in new_dict.items() if value == target][0]
        if len(self.dict) != 0 and len(self.dict) != 1:
            if upper:
                if index != 0:
                    new_dict[index-1], new_dict[index] = new_dict[index], new_dict[index-1]
            else:
                if index != len(self.dict)-1:
                    new_dict[index+1], new_dict[index] = new_dict[index], new_dict[index+1]
            self.dict = {obj.object.id: obj for obj in new_dict.values()}
            self.re_pack()
            self.canvas_layer_update()

    def re_pack(self):
        [obj.frame_pack_forget() for obj in self.dict.values()]
        [obj.re_pack() for obj in self.dict.values()]

    def canvas_layer_update(self):
        [self.canvas.lower(key) for key in self.dict]

    def canvas_move_position(self, id: str, x: int, y: int):
        self.canvas.image_move(id, x, y)
        self.canvas.image_select(id)

    def canvas_image_re_create(self, object: Obj.UNION_OBJECT):
        self.canvas.image_re_create(object)


class LayoutViewer:
    def __init__(self, object: Obj.LayoutCollection, frame: ScrollFrame, mirror_method: Callable):
        self.object = object
        self.mirror_method = mirror_method
        self.frame = tk.LabelFrame(frame, text=object.name, relief=tk.SOLID, bd=2)
        self.frame.pack(pady=2)
        box_frame = tk.Frame(self.frame)
        box_frame.pack(side=tk.RIGHT)
        self.mirror_box = tk.Button(box_frame, text="  mirror  ", command=self.mirror_button_click)
        self.mirror_box.grid(row=0, column=0, padx=2, pady=2)
        self.mirror_button_color_update()
        self.id_box = CustomEntry(box_frame, text="ID")
        self.id_box.grid(row=0, column=1, padx=2, pady=2)
        self.id_box.set(object.id)
        self.width_box = CustomSpinbox(box_frame, 10, text="Width")
        self.width_box.grid(row=1, column=0, padx=2, pady=2)
        self.heigth_box = CustomSpinbox(box_frame, 10, text="Heigth")
        self.heigth_box.grid(row=1, column=1, padx=2, pady=2)
        self.size_update()
        pos_frame = tk.Frame(box_frame)
        pos_frame.grid(row=2, column=0, columnspan=2, padx=2, pady=2)
        self.pos_left_box = CustomSpinbox(pos_frame, 5, text="LEFT")
        self.pos_left_box.pack(side=tk.LEFT, padx=3, pady=2)
        self.pos_top_box = CustomSpinbox(pos_frame, 5, text="TOP")
        self.pos_top_box.pack(side=tk.LEFT, padx=3, pady=2)
        self.pos_right_box = CustomSpinbox(pos_frame, 5, text="RIGHT")
        self.pos_right_box.pack(side=tk.LEFT, padx=3, pady=2)
        self.pos_bottom_box = CustomSpinbox(pos_frame, 5, text="BOTTOM")
        self.pos_bottom_box.pack(side=tk.LEFT, padx=3, pady=2)
        button_frame = tk.Frame(self.frame)
        button_frame.pack(side=tk.RIGHT)
        up_button = tk.Button(button_frame, text="▲", command=self.up_button_click)
        up_button.pack(side=tk.TOP, padx=2, pady=5)
        down_button = tk.Button(button_frame, text="▼", command=self.down_button_click)
        down_button.pack(side=tk.BOTTOM, padx=2, pady=5)

    def size_update(self):
        self.width_box.set(self.object.width)
        self.heigth_box.set(self.object.height)

    def position_update(self):
        self.pos_left_box.set(self.object.position[0])
        self.pos_top_box.set(self.object.position[1])
        self.pos_right_box.set(self.object.position[2])
        self.pos_bottom_box.set(self.object.position[3])
        self.pos_left_box.box.config(fg="red") if self.object.position[0] < 0 else self.pos_left_box.box.config(fg="black")
        self.pos_top_box.box.config(fg="red") if self.object.position[1] < 0 else self.pos_top_box.box.config(fg="black")
        self.pos_right_box.box.config(fg="red") if self.object.position[2] > 960 else self.pos_right_box.box.config(fg="black")
        self.pos_bottom_box.box.config(fg="red") if self.object.position[3] > 540 else self.pos_bottom_box.box.config(fg="black")

    def mirror_button_click(self):
        self.object.mirror_update()
        self.mirror_button_color_update()
        self.mirror_method(self.object)

    def mirror_button_color_update(self):
        if self.object.mirror:
            self.mirror_box.config(bg="blue")
        else:
            self.mirror_box.config(bg="SystemButtonFace")

    def re_pack(self):
        self.frame.pack()

    def frame_pack_forget(self):
        self.frame.pack_forget()

    def up_button_click(self):
        self.method(self.object.id, True)

    def down_button_click(self):
        self.method(self.object.id, False)


if __name__ == "__main__":
    print(__name__)