#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from tkinter import ttk
from PIL import Image
from typing import Union, Callable
import Object as Obj
# from Object import ConstImageLayoutObject, ConstTextLayoutObject, VariableImageLayoutObject, VariableTextLayoutObject, CounterTextLayoutObject, CounterImageLayoutObject
import random, string

UNION_OBJECT = Union[Obj.ConstTextLayoutObject, Obj.ConstImageLayoutObject, Obj.VariableImageLayoutObject, Obj.VariableTextLayoutObject, Obj.CounterTextLayoutObject, Obj.CounterImageLayoutObject]
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


class CustomCanvas(tk.Canvas):
    def __init__(self, parent, dataframe, *args, **kwargs):
        tk.Canvas.__init__(self, parent, *args, **kwargs)
        self.dict = LayoutObjectCustomList(self, dataframe)
        self.bind("<Button-1>", lambda event:self.left_click(event))
        self.bind("<Button1-Motion>", lambda event:self.mouse_drag(event))
        self.bind("<ButtonRelease>", lambda event:self.mouse_release())
        self.bind("<Button-3>", lambda event:self.right_click(event))
        self.resize_direction = False
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Delete", command=self.delete_object)

    def save_layouts(self) -> "list[Obj.LayoutElement]":
        save_list = [obj.object.save_cls() for obj in self.dict.dict.values()]
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

    def _create_canvas_object(self, obj: UNION_OBJECT):
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

    def object_position_update(self, tag):
        position = self.find_bbox(tag)
        self.dict.object_position_update(tag, position)

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

    def image_select(self, image_id):
        self.rect_delete()
        self.move_tag_delete()
        self.tag = (image_id, "current")
        self.dict.label_frame_select(image_id)
        self.addtag_withtag("move", image_id)
        self._create_rect(self.find_bbox(image_id))

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
        self.move_tag_delete()
        if self.resize_direction:
            self.resize_direction = False
            self.image_select(self.tag[0])
            self.on_mouse_leave()







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
    def __init__(self, canvas: CustomCanvas, dataframe):
        self.dict: dict[str, LayoutObjectViewer] = {}
        self.canvas: CustomCanvas = canvas
        self.frame = dataframe

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
        [self.delete_object(obj.object.id) for obj in list(self.dict.values())]
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



if __name__ == "__main__":
    print(__name__)