#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from tkinter import ttk
from typing import Union, Callable
import Object as Obj

UNION_OBJECT = Union[Obj.ConstTextLayoutObject, Obj.ConstImageLayoutObject, Obj.VariableImageLayoutObject, Obj.VariableTextLayoutObject, Obj.CounterTextLayoutObject, Obj.CounterImageLayoutObject]




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


class LayoutObjectViewer:
    def __init__(self, object: UNION_OBJECT, frame: tk.Tk, method: Callable):
        self.object = object
        self.method = method
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
        if "Text" in object.cls:
            font_frame = tk.Frame(box_frame)
            font_frame.grid(row=3, column=0, columnspan=2, padx=2, pady=2)
            self.font_box = CustomFontCombobox(font_frame, 30, text="Font")
            self.font_box.box.bind("<<ComboboxSelected>>", lambda event: self.font_update())
            self.font_box.pack(padx=2, pady=2)

        button_frame = tk.Frame(self.frame)
        button_frame.pack(side=tk.RIGHT)
        up_button = tk.Button(button_frame, text="▲", command=self.up_button_click)
        up_button.pack(side=tk.TOP, padx=2, pady=5)
        down_button = tk.Button(button_frame, text="▼", command=self.down_button_click)
        down_button.pack(side=tk.BOTTOM, padx=2, pady=5)

    def size_update(self):
        self.width_box.set(self.object.width)
        self.heigth_box.set(self.object.height)

    def position_update(self, position):
        self.object.position = position
        self.pos_left_box.set(position[0])
        self.pos_top_box.set(position[1])
        self.pos_right_box.set(position[2])
        self.pos_bottom_box.set(position[3])
        self.pos_left_box.box.config(fg="red") if self.object.position[0] < 0 else self.pos_left_box.box.config(fg="black")
        self.pos_top_box.box.config(fg="red") if self.object.position[1] < 0 else self.pos_top_box.box.config(fg="black")
        self.pos_right_box.box.config(fg="red") if self.object.position[2] > 960 else self.pos_right_box.box.config(fg="black")
        self.pos_bottom_box.box.config(fg="red") if self.object.position[3] > 540 else self.pos_bottom_box.box.config(fg="black")

    def font_update(self):
        self.object.font = self.font_box.get()

    def re_pack(self):
        self.frame.pack()

    def frame_pack_forget(self):
        self.frame.pack_forget()

    def up_button_click(self):
        self.method(self.object.id, True)

    def down_button_click(self):
        self.method(self.object.id, False)



class LayoutObjectCustomList:
    import Canvas
    def __init__(self, canvas: Canvas.CustomCanvas, dataframe):
        self.dict: dict[str, LayoutObjectViewer] = {}
        self.canvas = canvas
        self.frame = dataframe

    def load(self, list: "list[LayoutObjectViewer]"):
        self.dict = {obj.object.id: obj for obj in list}

    def add_object(self, obj: UNION_OBJECT):
        self.dict[obj.id] = LayoutObjectViewer(obj, self.frame, self.layer_update)
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


class ManagerFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)


if __name__ == "__main__":
    print(__name__)