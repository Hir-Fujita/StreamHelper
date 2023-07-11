#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk



class ScrollFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        scrollbar = ttk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(self, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        scrollbar.config(command=self.canvas.yview)

        self.frame = ttk.Frame(self.canvas)
        self.frame.bind("<Configure>", self._on_frame_configure)

        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

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


class CustomCanvas(tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        tk.Canvas.__init__(self, parent, *args, **kwargs)
        self.bind("<Button-1>", lambda event:self.left_click(event))

    def find_tag(self, event):
        closest_ids = self.find_closest(event.x, event.y)
        if len(closest_ids) != 0:
            tag = self.gettags(closest_ids[0])
            return tag

    def left_click(self, event):
        tag = self.find_tag(event)
        print(tag)


