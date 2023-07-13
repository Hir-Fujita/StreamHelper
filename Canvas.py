#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from PIL import Image
from typing import Union
from Object import ConstImageLayoutObject, ConstTextLayoutObject
UNION_OBJECT = Union[ConstTextLayoutObject, ConstImageLayoutObject]
import random, string

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
    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
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
        self.resize_direction = False

    def add_const_image_object(self, path: str):
        self.dict.add_object(ConstImageLayoutObject(path, f"id_{random_id(10)}"))

    def _create_canvas_object(self, obj: UNION_OBJECT):
        self.create_image(
            480,
            270,
            anchor="center",
            image=obj.image_tk,
            tag=obj.id
            )
        self.object_position_update(obj.id)

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
                if not self.resize_check(tag):
                    self.image_select(tag[0])
                    self.tag = tag
                    self.x = event.x
                    self.y = event.y
            else:
                self.rect_delete()
                self.tag = False

    def image_select(self, image_id):
        self.rect_delete()
        self.move_tag_delete()
        self.tag = (image_id, "current")
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
        self.box = tk.Entry(self, width=18)
        self.box.pack(padx=2, pady=2)

    def set(self, text: str):
        self.box.delete(0, tk.END)
        self.box.insert(0, text)

    def get(self) -> str:
        return self.box.get()

class CustomSpinbox(tk.LabelFrame):
    def __init__(self, parent, width: int, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.variable = tk.IntVar()
        self.box = tk.Spinbox(self, width=width, increment=1, from_=1, to=9999, textvariable=self.variable)
        self.box.pack(padx=2, pady=2)

    def set(self, value: int):
        self.variable.set(value)

    def get(self) -> int:
        return self.variable.get()


class LayoutObjectViewer:
    def __init__(self, object: UNION_OBJECT, frame):
        self.object = object
        self.frame = tk.Frame(frame, relief=tk.SOLID, bd=2)
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

        button_frame = tk.Frame(self.frame)
        button_frame.pack(side=tk.RIGHT)
        up_button = tk.Button(button_frame, text="▲")
        up_button.pack(side=tk.TOP, padx=2, pady=5)
        down_button = tk.Button(button_frame, text="▼")
        down_button.pack(side=tk.BOTTOM, padx=2, pady=5)

    def size_update(self):
        self.width_box.set(self.object.data.width)
        self.heigth_box.set(self.object.data.height)

    def position_update(self, position):
        self.object.data.position = position
        self.pos_left_box.set(position[0])
        self.pos_top_box.set(position[1])
        self.pos_right_box.set(position[2])
        self.pos_bottom_box.set(position[3])


class LayoutObjectCustomList:
    def __init__(self, canvas: CustomCanvas, dataframe):
        self.dict = {}
        self.canvas = canvas
        self.frame = dataframe

    def add_object(self, obj: UNION_OBJECT):
        obj.update_image()
        self.dict[obj.id] = LayoutObjectViewer(obj, self.frame)
        self.canvas._create_canvas_object(obj)

    def object_position_update(self, id, position):
        self.dict[id].position_update(position)

    def object_size_update(self, id):
        self.dict[id].size_update()