from api_requests import *
from planets import *
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from tktooltip import ToolTip
import math

class Orr_App:

    def __init__(self, top=False):
        self.root = Tk()
        if not top:
            self.orrery = Orrery()
            self.docked = False
            self.root.arrows = {}
            self.root.planets = {}
            self.root.tooltips = []
            self.arms = {i:Image.open(f'GUI/Planets/{i.lower()}_tr.png') for i in self.orrery.df.columns}
            self.arrow_raw = Image.open('GUI/Arrow5.png')
            self.circle_raw = Image.open('GUI/11.png')
            self.scr_wid, self.scr_hei = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            self.cir_wid, self.cir_hei = int(self.scr_wid / 10), int(self.scr_hei / 3)
            self.wid, self.hei = int(self.scr_wid / 5), int(self.scr_hei / 1.5)
            x = int(self.scr_wid - (self.wid))
            y = int((self.scr_hei / 2) - (self.hei / 2))
            self.undock_geo = f'{self.wid}x{self.hei}+{x}+{y}'
            self.dock_geo = f'{self.wid}x{self.hei}+{self.scr_wid - 3}+{y}'
            self.root.geometry(self.undock_geo)
            root = self.root
            self.canvas = Canvas(root, width=self.wid, height=self.hei)
            self.background = ImageTk.PhotoImage(Image.open('GUI/BG.jpg').resize((self.wid, self.hei)))
            self.canvas.create_image(int(self.wid/2), int(self.hei/2), image=self.background, tags='bg')
            self.canvas.bind('<Leave>', self.dock)
            self.canvas.bind('<Enter>', self.undock)
            self.canvas.bind('<1>', self.menu)
            self.canvas.pack()
            self.root.overrideredirect(True)
            self.root.wm_attributes('-alpha', 0.0)
            self.root.wm_attributes('-topmost', False)
            self.circle_rotate(0)
            self.arms_rotate()
            self.root.mainloop()
        else:
            self.menu('pss', pss=True)
            self.root.mainloop()

    def dock(self, event):
        self.root.after(375, self.root.geometry, self.dock_geo)
        self.docked = True
        self.hover_murder(0)

    def undock(self, event):
        self.root.after(375, self.root.geometry, self.undock_geo)
        self.docked = False
        self.circle_rotate(0)
        self.arms_rotate()

    def menu(self, event, pss=False):
        if not pss:
            if event.x not in range(self.wid - 10, self.wid) or event.y not in range(int(self.hei/2) - 10, int(self.hei/2) + 10):
                return
        top = Toplevel(self.root)
        self.top = top
        top.geometry('400x180')
        top.title('Location Settings')
        top.text = StringVar()
        top.entry = Entry(top, width=50, textvariable=top.text)
        top.entry.pack(pady=(25,25))
        top.entry.insert(0, 'Input Address')
        Button(top, text='Submit', command=self.location_update).pack(pady=(0,10))
        Button(top, text='Cancel', command=top.destroy).pack()
        Button(top, text='Close', command=self.root.destroy).pack(pady=(10,0))

    def location_update(self):
        address = self.top.text.get()
        re_location(address)
        self.top.destroy()
        Orr_App()
        self.root.destroy()

    def circle_rotate(self, deg):
        rot_image = self.circle_raw.rotate(360 - deg)
        rot_image = rot_image.resize((self.cir_hei, self.cir_hei))
        self.circle = ImageTk.PhotoImage(rot_image)
        self.canvas.delete('circ')
        self.canvas.create_image(self.wid, self.hei/2, image=self.circle, tags='circ')
        deg += .375
        if deg == 360:
            deg = 0
        if not self.docked:
            self.root.after(10, self.circle_rotate, deg)

    def arms_rotate(self):
        loc = self.orrery.location_return()
        size_x = int(self.cir_hei / 8)
        size_y = int(self.cir_hei / 4)
        rat_x = size_x/self.arrow_raw.size[0]
        rat_y = size_y/self.arrow_raw.size[1]
        cx, cy = int(self.wid), int(self.hei/2) - int((self.cir_hei + size_y)/2)
        cy2 = int(self.hei / 2) - int((self.cir_hei + size_x) / 2) - size_y
        ox, oy = int(self.wid), int(self.hei/2)
        for i in loc.keys():
            prog = loc[i]
            if prog:
                angle = (1 - prog) * 180
                arr_loc = self.orrery.center_rotate([cx, cy], [ox, oy], angle)
                pla_loc = self.orrery.center_rotate([cx, cy2], [ox, oy], angle)
                arrow = self.arrow_raw.rotate(angle, expand=True)
                arrow = arrow.resize((int(arrow.size[0]*rat_x), int(arrow.size[1]*rat_y)))
                self.root.arrows[i] = ImageTk.PhotoImage(arrow)
                plan = self.arms[i].resize((size_x, size_x))
                self.root.planets[i] = ImageTk.PhotoImage(plan)
                self.canvas.delete(f'{i}')
                a = self.canvas.create_image(*arr_loc, image=self.root.arrows[i], tags=f'{i}')
                b = self.canvas.create_image(*pla_loc, image=self.root.planets[i], tags=f'{i}')
                self.canvas.tag_bind(i, '<Enter>', self.hover_maker)
                self.canvas.tag_bind(i, '<Leave>', self.hover_murder)
            else:
                self.canvas.delete(i)
        if not self.docked:
            self.root.after(120000, self.arms_rotate)

    def hover_maker(self, event):
        names = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        name = None
        for i in names:
            if self.canvas.gettags(i)[0] != 'bg':
                name = self.canvas.gettags(i)[0]
                break
        if name:
            text = self.hover_helper(name)
            tooltip = Toplevel(self.root)
            self.root.tooltip = tooltip
            tooltip_label = Label(tooltip, text=text, background="lightyellow", relief="solid", borderwidth=1)
            tooltip_label.pack()
            tooltip.geometry(f'+{int(self.scr_wid * (4 / 5)) + (event.x + 10)}+{int(self.scr_hei * (1/6) + (event.y + 10))}')
            tooltip.overrideredirect(True)
            tooltip.deiconify()

    def hover_murder(self, event):
        self.root.tooltip.withdraw()
        self.root.tooltip.destroy()

    def hover_helper(self, name):
        df = api_request(soup=False)
        return f'{name}\nAltitude: {df.loc[1, name][0]}\nAzimuth: {df.loc[1, name][1]}'


if __name__ == '__main__':
    if first_try():
        Orr_App()
    else:
        Orr_App(top=True)
