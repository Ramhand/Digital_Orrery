from api_requests import *
from planets import *
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import math

class Orr_App:
    """
    A class to create the graphical user interface (GUI) for the orrery application.
    """

    def __init__(self, top=False):
        """
        Initializes the Orr_App class, setting up the main window and components.
        
        Args:
            top (bool): If True, only displays the top-level menu for location settings.
        """
        self.root = Tk()
        if not top:
            # Initialize the Orrery object and set up the window
            self.orrery = Orrery()
            self.docked = False
            self.root.arrows = {}
            self.root.planets = {}
            self.root.tooltips = []
            # Load planetary images and set up the graphics
            self.arms = {i: Image.open(f'GUI/Planets/{i.lower()}_tr.png') for i in self.orrery.df.columns}
            self.arrow_raw = Image.open('GUI/Arrow5.png')
            self.circle_raw = Image.open('GUI/11.png')
            self.scr_wid, self.scr_hei = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            self.cir_wid, self.cir_hei = int(self.scr_wid / 10), int(self.scr_hei / 3)
            self.wid, self.hei = int(self.scr_wid / 5), int(self.scr_hei / 1.5)
            x = int(self.scr_wid - self.wid)
            y = int((self.scr_hei / 2) - (self.hei / 2))
            # Set up window geometry
            self.undock_geo = f'{self.wid}x{self.hei}+{x}+{y}'
            self.dock_geo = f'{self.wid}x{self.hei}+{self.scr_wid - 3}+{y}'
            self.root.geometry(self.undock_geo)
            root = self.root
            self.canvas = Canvas(root, width=self.wid, height=self.hei)
            self.background = ImageTk.PhotoImage(Image.open('GUI/BG.jpg').resize((self.wid, self.hei)))
            # Display the background image
            self.canvas.create_image(int(self.wid / 2), int(self.hei / 2), image=self.background, tags='bg')
            self.canvas.bind('<Leave>', self.dock)
            self.canvas.bind('<Enter>', self.undock)
            self.canvas.bind('<1>', self.menu)
            self.canvas.pack()
            # Remove window decorations
            self.root.overrideredirect(True)
            # Start rotating elements
            self.circle_rotate(0)
            self.arms_rotate()
            self.root.mainloop()
        else:
            # Display menu only
            self.menu('pss', pss=True)
            self.root.mainloop()

    def dock(self, event):
        """
        Dock the application to the side of the screen when the mouse leaves the window.
        """
        if self.root.winfo_pointerx() in range(self.scr_wid - self.wid, self.scr_wid):
            if self.root.winfo_pointery() in range(int(self.scr_hei * (1 / 6)), int(self.scr_hei * (5 / 6))):
                return
        self.root.after(125, self.root.geometry, self.dock_geo)
        self.docked = True
        self.hover_murder(0)

    def undock(self, event):
        """
        Undock the application from the side of the screen when the mouse enters the window.
        """
        self.root.after(125, self.root.geometry, self.undock_geo)
        self.docked = False
        self.circle_rotate(0)
        self.arms_rotate()

    def menu(self, event, pss=False):
        """
        Display a menu for location settings or exiting the application.
        
        Args:
            pss (bool): If True, shows only the location settings menu.
        """
        if not pss:
            if event.x not in range(self.wid - 10, self.wid) or event.y not in range(int(self.hei/2) - 10, int(self.hei/2) + 10):
                return
        top = Toplevel(self.root)
        self.top = top
        top.geometry('400x180')
        top.title('Location Settings')
        top.note = ttk.Notebook(self.top)
        top.tab1 = ttk.Frame(top.note)
        top.tab2 = ttk.Frame(top.note)
        top.note.add(top.tab1, text='Location Settings')
        top.note.add(top.tab2, text='Exit')
        top.note.pack(expand=1, fill='both')

        top.text = StringVar()
        top.text2 = StringVar()
        top.entry = Entry(top.tab1, width=50, textvariable=top.text)
        top.entry.pack(pady=(25,25))
        top.entry.insert(0, 'Input Address')
        top.entry2 = Entry(top.tab1, width=50, textvariable=top.text2)
        top.entry2.pack(pady=(25,25))
        top.entry2.insert(0, 'Input RapidAPI key')

        Button(top.tab1, text='Submit', command=self.location_update).pack(pady=(0,10))
        Button(top.tab1, text='Cancel', command=top.destroy).pack()
        Button(top.tab1, text='Close', command=self.root.destroy).pack(pady=(10,0))

    def location_update(self):
        """
        Update the application with a new location based on user input.
        """
        address = self.top.text.get()
        rapidkey = self.top.text2.get()
        GEO_API = {
    'x-rapidapi-key': f"{rapidkey}",
    'x-rapidapi-host': "map-geocoding.p.rapidapi.com"
}
        ELE_API = {
	"x-rapidapi-key": f"{rapidkey}",
	"x-rapidapi-host": "elevation-from-latitude-and-longitude.p.rapidapi.com"
}
        with open('../Data/keys.dat', 'wb') as file:
            pickle.dump([GEO_API, ELE_API], file)
        re_location(address)
        self.top.destroy()
        Orr_App()
        self.root.destroy()


    def circle_rotate(self, deg):
        """
        Rotate the circular element in the GUI.
        
        Args:
            deg (float): The degree of rotation.
        """
        rot_image = self.circle_raw.rotate(360 - deg)
        rot_image = rot_image.resize((self.cir_hei, self.cir_hei))
        self.circle = ImageTk.PhotoImage(rot_image)
        self.canvas.delete('circ')
        self.canvas.create_image(self.wid, self.hei / 2, image=self.circle, tags='circ')
        deg += .375
        if deg == 360:
            deg = 0
        if not self.docked:
            self.root.after(10, self.circle_rotate, deg)

    def arms_rotate(self):
        """
        Rotate the planetary arms in the GUI.
        """
        loc = self.orrery.location_return()
        size_x = int(self.cir_hei / 8)
        size_y = int(self.cir_hei / 4)
        cx, cy = int(self.wid), int(self.hei / 2) - int((self.cir_hei + size_y) / 2)
        cy2 = int(self.hei / 2) - int((self.cir_hei + size_x) / 2) - size_y
        ox, oy = int(self.wid), int(self.hei / 2)
        for i in loc.keys():
            prog = loc[i]
            if prog:
                angle = (1 - prog) * 180
                arr_loc = self.orrery.center_rotate([cx, cy], [ox, oy], angle)
                pla_loc = self.orrery.center_rotate([cx, cy2], [ox, oy], angle)
                arrow = self.arrow_raw.resize((size_x, size_y), resample=Image.BICUBIC)
                arrow = arrow.rotate(angle, expand=True, resample=Image.BICUBIC)
                self.root.arrows[i] = ImageTk.PhotoImage(arrow)
                plan = self.arms[i].resize((size_x, size_x))
                self.root.planets[i] = ImageTk.PhotoImage(plan)
                self.canvas.delete(f'{i}')
                self.canvas.create_image(*arr_loc, image=self.root.arrows[i], tags=f'{i}')
                self.canvas.create_image(*pla_loc, image=self.root.planets[i], tags=f'{i}')
                self.canvas.tag_bind(i, '<Enter>', self.hover_maker)
                self.canvas.tag_bind(i, '<Leave>', self.hover_murder)
            else:
                self.canvas.delete(i)
        if not self.docked:
            self.root.after(120000, self.arms_rotate)

    def hover_maker(self, event):
        """
        Create tooltips to display planetary data when hovering over a planet.
        """
        names = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        name = None
        text = ''
        for i in names:
            if self.canvas.gettags(i)[0] != 'bg':
                name = self.canvas.gettags(i)[0]
                if text:
                    text += '\n~~~~~~~~~~~\n' + self.hover_helper(name)
                else:
                    text += self.hover_helper(name)
        if name:
            tooltip = Toplevel(self.root)
            self.root.tooltips.append(tooltip)
            tooltip_label = Label(tooltip, text=text, background="lightyellow", relief="solid", borderwidth=1)
            tooltip_label.pack()
            tooltip.geometry(
                f'+{int(self.scr_wid * (4 / 5)) + (event.x + 15)}+{int(self.scr_hei * (1 / 6) + (event.y - 15))}')
            tooltip.overrideredirect(True)
            tooltip.deiconify()

    def hover_murder(self, event):
        """
        Destroy tooltips when the mouse leaves the planet's area.
        """
        for i in self.root.tooltips:
            i = self.root.tooltips.pop(self.root.tooltips.index(i))
            i.destroy()

    def hover_helper(self, name):
        """
        Helper function to retrieve planetary data for the tooltips.
        
        Args:
            name (str): The name of the planet to retrieve data for.
        
        Returns:
            str: The formatted string with planetary data (altitude, azimuth, phase).
        """
        api_request(soup=False)
        with open('current.dat', 'rb') as file:
            df, phase, _ = pickle.load(file)
        if name.lower() != 'moon':
            return f'{name}\nAltitude: {df.loc[1, name][0]}\nAzimuth: {df.loc[1, name][1]}'
        else:
            return f'{name}\nAltitude: {df.loc[1, name][0]}\nAzimuth: {df.loc[1, name][1]}\nPhase: {phase}'
