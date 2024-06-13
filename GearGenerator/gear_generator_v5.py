import tkinter as tk
from tkinter import messagebox
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from shapely.ops import cascaded_union, unary_union
from shapely.geometry import Point, MultiPoint
from shapely.affinity import rotate, scale

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

# GUI Application with embedded gear generation
class GearGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gear Generator")
        self.geometry("800x600")
        
        self.teeth_count_var = tk.IntVar(value=17)
        self.tooth_width_var = tk.DoubleVar(value=10.0)
        self.pressure_angle_var = tk.DoubleVar(value=20.0)
        self.backlash_var = tk.DoubleVar(value=0.2)
        self.frame_count_var = tk.IntVar(value=16)
        
        self.create_widgets()

    def create_widgets(self):
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
        
        tk.Button(self, text="Generate Gear", command=self.generate_and_display_gear).pack()

    def generate_and_display_gear(self):
        gear_poly = generate_gear(
            teeth_count=self.teeth_count_var.get(),
            tooth_width=self.tooth_width_var.get(),
            pressure_angle=np.deg2rad(self.pressure_angle_var.get()),
            backlash=self.backlash_var.get(),
            frame_count=self.frame_count_var.get()
        )

        self.visualize_gear(gear_poly)
    
    def visualize_gear(self, gear_poly):
        fig = Figure(figsize=(6, 6))
        ax = fig.add_subplot(111)
        x, y = gear_poly.exterior.xy
        ax.fill(x, y, alpha=0.5, fc='r', ec='none')
        ax.axis('equal')
        
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack()

if __name__ == "__main__":
    app = GearGeneratorApp()
    app.mainloop()
