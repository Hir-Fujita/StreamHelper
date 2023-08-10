#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from typing import Union, Callable
import Object as Obj
import Widget as Wid
import Manager
import random, string


def random_id(n):
    return str(random.randrange(10**(n-1),10**n))



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

    def image_select(self):
        raise NotImplementedError

    def mouse_drag(self, event):
        raise NotImplementedError

    def resize_rect(self, event):
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


class LayoutObjectCanvas(CustomCanvas):
    def __init__(self, parent, dataframe, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.dict = Wid.LayoutObjectCustomList(self, dataframe)

    def save_check(self) -> bool:
        result = [obj.object.position for obj in self.dict.dict.values()]
        for res in result:
            if res[0] < 0 or res[1] < 0 or res[2] > 960 or res[3] > 540:
                return False
        return True

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
        self.rect_delete()
        self.move_tag_delete()
        self.tag = (image_id, "current")
        self.dict.label_frame_select(image_id)
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


class LayoutCanvas(CustomCanvas):
    def __init__(self, parent, layout_manager: Manager.LayoutManager, frame: Wid.ScrollFrame, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.layout_manager = layout_manager
        self.frame = frame
        self.widgets: "dict[str: Wid.LayoutViewer]" = layout_manager.widgets
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
        self.widgets[obj.id] = Wid.LayoutViewer(obj, self.frame, self.image_re_create)

    def image_select(self, image_id):
        self.rect_delete()
        self.move_tag_delete()
        self.tag = (image_id, "current")
        # self.dict.label_frame_select(image_id)
        self.addtag_withtag("move", image_id)
        self._create_rect(self.find_bbox(image_id))

    def re_create(self, id: str=""):
        if id:
            self.widgets[id].frame_pack_forget()
            self.layout_manager.delete_layout_collection(self.tag[0])
            del self.widgets[self.tag[0]]
        else:
            for key, wid in self.layout_manager.layout_dic.items():
                print(key, wid)

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



if __name__ == "__main__":
    print(__name__)