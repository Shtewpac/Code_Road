import sys
import tkinter as tk
from tkinter import messagebox
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from shapely.ops import unary_union
from shapely.geometry import Point, MultiPoint
from shapely.affinity import rotate, scale
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QTimer

# Gear generation logic adapted for GUI
def generate_gear(teeth_count=8, tooth_width=1., pressure_angle=np.deg2rad(20.), backlash=0., frame_count=16):
    tooth_width -= backlash
    pitch_circumference = tooth_width * 2 * teeth_count
    pitch_radius = pitch_circumference / (2 * np.pi)
    addendum = tooth_width * (2 / np.pi)
    dedendum = addendum
    outer_radius = pitch_radius + addendum

    profile = np.array([
        [-(.5 * tooth_width + addendum * np.tan(pressure_angle)),  addendum],
        [-(.5 * tooth_width - dedendum * np.tan(pressure_angle)), -dedendum],
        [( .5 * tooth_width - dedendum * np.tan(pressure_angle)), -dedendum],
        [( .5 * tooth_width + addendum * np.tan(pressure_angle)),  addendum]
    ])

    poly_list = []
    prev_X = None
    l = 2 * tooth_width / pitch_radius
    for theta in np.linspace(0, l, frame_count):
        X = rotation(profile + np.array((-theta * pitch_radius, pitch_radius)), theta)
        if prev_X is not None:
            poly_list.append(MultiPoint([x for x in X] + [x for x in prev_X]).convex_hull)
        prev_X = X

    # tooth_poly = cascaded_union(poly_list)
    tooth_poly = unary_union(poly_list)
    tooth_poly = tooth_poly.union(scale(tooth_poly, -1, 1, 1, Point(0., 0.)))

    gear_poly = Point(0., 0.).buffer(outer_radius)
    for i in range(teeth_count):
        gear_poly = rotate(gear_poly.difference(tooth_poly), (2 * np.pi) / teeth_count, Point(0., 0.), use_radians=True)
    
    return gear_poly

# Rotational transformation functions
def rot_matrix(x):
    c, s = np.cos(x), np.sin(x)
    return np.array([[c, -s], [s, c]])

def rotation(X, angle, center=None):
    if center is None:
        return np.dot(X, rot_matrix(angle))
    else:
        return np.dot(X - center, rot_matrix(angle)) + center

class Gear:
    def __init__(self, teeth_count, tooth_width, pressure_angle, backlash, frame_count):
        self.teeth_count = teeth_count
        self.tooth_width = tooth_width
        self.pressure_angle = pressure_angle
        self.backlash = backlash
        self.frame_count = frame_count
        # Generate the gear with the given parameters
        self.gear_poly = generate_gear(self.teeth_count, self.tooth_width, self.pressure_angle, self.backlash, self.frame_count)
        
    def draw(self, ax):
        # Draw the gear and return the artists
        x, y = self.gear_poly.exterior.xy
        polygon = ax.fill(x, y, alpha=0.5, fc='r', ec='none')
        return polygon  # ax.fill returns a list of Polygon objects
        

# GUI Application with embedded gear generation
class GearGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gear Generator")
        self.geometry("800x600")

        # Initialize the variables
        self.teeth_count_var = tk.IntVar(value=17)
        self.tooth_width_var = tk.DoubleVar(value=10.0)
        self.pressure_angle_var = tk.DoubleVar(value=20.0)
        self.backlash_var = tk.DoubleVar(value=0.2)
        self.frame_count_var = tk.IntVar(value=16)

        # Initialize gears list with one default gear
        self.gears = [Gear(
            teeth_count=self.teeth_count_var.get(),
            tooth_width=self.tooth_width_var.get(),
            pressure_angle=np.deg2rad(self.pressure_angle_var.get()),
            backlash=self.backlash_var.get(),
            frame_count=self.frame_count_var.get()
        )]
        
        # Set up the canvas for drawing gears
        self.setup_canvas()  # Ensure this is called before create_widgets if it uses the canvas

        # Create widgets in the UI
        self.create_widgets()

        # Setup animation
        self.setup_animation()
        
        # Create widgets and setup animation
        self.create_widgets()
        self.setup_animation()
        
    def setup_canvas(self):
        # Set up the canvas and 'ax' attribute
        self.fig = Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('equal')

        # Embed the figure in the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack()

    def create_widgets(self):
        # Create and pack widgets for gear parameters
        tk.Label(self, text="Teeth Count:").pack()
        tk.Entry(self, textvariable=self.teeth_count_var).pack()

        tk.Label(self, text="Tooth Width:").pack()
        tk.Entry(self, textvariable=self.tooth_width_var).pack()

        tk.Label(self, text="Pressure Angle:").pack()
        tk.Entry(self, textvariable=self.pressure_angle_var).pack()

        tk.Label(self, text="Backlash:").pack()
        tk.Entry(self, textvariable=self.backlash_var).pack()

        tk.Label(self, text="Frame Count:").pack()
        tk.Entry(self, textvariable=self.frame_count_var).pack()

        # Button to add a new gear based on the entered parameters
        tk.Button(self, text="Add New Gear", command=self.add_new_gear).pack()

        # Initially draw the default gear
        self.draw_gears()
        
    def add_new_gear(self):
        # Method to create and add a new gear based on the entered parameters
        new_gear = Gear(
            teeth_count=self.teeth_count_var.get(),
            tooth_width=self.tooth_width_var.get(),
            pressure_angle=np.deg2rad(self.pressure_angle_var.get()),
            backlash=self.backlash_var.get(),
            frame_count=self.frame_count_var.get()
        )
        self.gears.append(new_gear)
        self.draw_gears()
        
    def generate_and_display_gear(self):
        gear = Gear(
            teeth_count=self.teeth_count_var.get(),
            tooth_width=self.tooth_width_var.get(),
            pressure_angle=np.deg2rad(self.pressure_angle_var.get()),
            backlash=self.backlash_var.get(),
            frame_count=self.frame_count_var.get()
        )
        self.gears.append(gear)
        self.draw_gears()
    
    def visualize_gear(self, gear_poly):
        fig = Figure(figsize=(6, 6))
        ax = fig.add_subplot(111)
        x, y = gear_poly.exterior.xy
        ax.fill(x, y, alpha=0.5, fc='r', ec='none')
        ax.axis('equal')
        
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack()
    
    def setup_animation(self):
        self.fig = Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('equal')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack()
        self.anim = FuncAnimation(self.fig, self.animate_gears, init_func=self.draw_gears, interval=100, blit=True)

    def draw_gears(self):
        # Clear the axes for the new frame
        self.ax.clear()
        self.ax.axis('equal')

        # List to store the artists for the animation
        artists = []

        # Draw the gears here and add the resulting artists to the list
        for gear in self.gears:
            # Assuming gear.draw() is adapted to return the artists it draws
            gear_artists = gear.draw(self.ax)
            artists.extend(gear_artists)

        # Redraw the canvas
        self.canvas.draw()

        # The init function must return a sequence of Artist objects.
        return artists

    def setup_animation(self):
        # Set up the animation using 'self.ax'
        self.anim = FuncAnimation(self.fig, self.animate_gears, init_func=self.draw_gears, interval=100, blit=True)



class Gear:
    def __init__(self, teeth_count, tooth_width, pressure_angle, backlash, frame_count):
        self.teeth_count = teeth_count
        self.tooth_width = tooth_width
        self.pressure_angle = pressure_angle
        self.backlash = backlash
        self.frame_count = frame_count
        self.gear_poly = generate_gear(teeth_count, tooth_width, pressure_angle, backlash, frame_count)
        self.angle = 0
    
    def rotate(self, angle_increment):
        self.angle += angle_increment
        self.gear_poly = rotate(self.gear_poly, angle_increment, origin='centroid', use_radians=True)
    
    def draw(self, ax):
        x, y = self.gear_poly.exterior.xy
        ax.fill(x, y, alpha=0.5, fc='r', ec='none')
        
class GearCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gears = []

    def paintEvent(self, event):
        painter = QPainter(self)
        # Draw gears
        for gear in self.gears:
            gear.draw(painter)

    def add_gear(self, gear):
        self.gears.append(gear)
        self.update()

if __name__ == '__main__':
    app = GearGeneratorApp()
    app.mainloop()
    # main()