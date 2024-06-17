import tkinter as tk
from tkinter import ttk
import numpy as np
from shapely.geometry import Point, MultiPoint
from shapely.affinity import translate, rotate, scale
from shapely.ops import unary_union

# Consolidate the helper functions for gear generation
def rotation(X, angle, center=None):
    c, s = np.cos(angle), np.sin(angle)
    matrix = np.array([[c, -s], [s, c]])
    if center is None:
        return np.dot(X, matrix)
    else:
        return np.dot(X - center, matrix) + center

class Gear:
    def __init__(self, num_teeth, module, tooth_width, pressure_angle_deg=20, backlash=0, position=None, rotation_speed=1, connection_angle=0):
        self.num_teeth = num_teeth
        self.module = module
        self.tooth_width = tooth_width
        self.pressure_angle = np.deg2rad(pressure_angle_deg)
        self.backlash = backlash
        self.position = position if position is not None else (0, 0)
        self.rotation_speed = rotation_speed
        self.connection_angle = connection_angle  # Connection angle in degrees
        self.geometry = None

    def generate_gear_geometry(self):
        tooth_width_adjusted = self.tooth_width - self.backlash
        pitch_circumference = tooth_width_adjusted * 2 * self.num_teeth
        pitch_radius = pitch_circumference / (2 * np.pi)
        addendum = tooth_width_adjusted * (2 / np.pi)
        dedendum = addendum
        outer_radius = pitch_radius + addendum

        profile = np.array([
            [-(.5 * tooth_width_adjusted + addendum * np.tan(self.pressure_angle)),  addendum],
            [-(.5 * tooth_width_adjusted - dedendum * np.tan(self.pressure_angle)), -dedendum],
            [( .5 * tooth_width_adjusted - dedendum * np.tan(self.pressure_angle)), -dedendum],
            [( .5 * tooth_width_adjusted + addendum * np.tan(self.pressure_angle)),  addendum]
        ])

        poly_list = []
        prev_X = None
        l = 2 * tooth_width_adjusted / pitch_radius
        for theta in np.linspace(0, l, 16):  # Assuming frame_count=16
            X = rotation(profile + np.array((-theta * pitch_radius, pitch_radius)), theta)
            if prev_X is not None:
                poly_list.append(MultiPoint([x for x in X] + [x for x in prev_X]).convex_hull)
            prev_X = X

        tooth_poly = unary_union(poly_list)
        tooth_poly = tooth_poly.union(scale(tooth_poly, -1, 1, 1, Point(0., 0.)))

        gear_poly = Point(0., 0.).buffer(outer_radius)
        for i in range(self.num_teeth):
            gear_poly = rotate(gear_poly.difference(tooth_poly), (2 * np.pi) / self.num_teeth, Point(0., 0.), use_radians=True)

        self.geometry = gear_poly
        # Print statements for debugging
        print(f"Gear {self.num_teeth} teeth, Module: {self.module}")
        print(f"Pitch Radius: {pitch_radius}, Outer Radius: {outer_radius}")
        print(f"Profile: {profile}")
        print(f"Total poly count: {len(poly_list)}")
    
    def draw(self, canvas, canvas_scale=2, canvas_center=(250, 250)):
        print(f"Drawing gear at position: {self.position}")
        if self.geometry:            
            # Translate the geometry to the gear's position on the canvas
            translated_geometry = translate(self.geometry, xoff=self.position[0], yoff=self.position[1])
            
            # Scale the geometry to fit the canvas size
            scaled_geometry = scale(translated_geometry, xfact=canvas_scale, yfact=canvas_scale, origin=(0, 0))
            
            # Get the scaled and translated coordinates of the gear's exterior
            x, y = scaled_geometry.exterior.xy
            
            # Offset the drawing by the canvas center
            canvas_coords = [(xi + canvas_center[0], yi + canvas_center[1]) for xi, yi in zip(x, y)]
            
            # Draw the gear on the canvas
            canvas.create_polygon(canvas_coords, fill='red', outline='black')
      
    
class GearGeneratorApp(tk.Tk):
    DEFAULT_NUM_TEETH = 13
    DEFAULT_MODULE = 2
    DEFAULT_PRESSURE_ANGLE_DEG = 24
    DEFAULT_BASE_DIAMETER = DEFAULT_NUM_TEETH * DEFAULT_MODULE
    
    def __init__(self):
        super().__init__()
        self.title("Gear Generator")
        self.gears = []
        self.animation_running = False
        self.create_widgets()
        self.create_default_gear()
    
    def create_widgets(self):
        # Buttons for adding and removing gears with grid layout
        ttk.Button(self, text="Add Gear", command=self.add_gear).grid(row=0, column=0, columnspan=2, sticky='ew')
        ttk.Button(self, text="Remove Gear", command=self.remove_gear).grid(row=0, column=2, columnspan=2, sticky='ew')

        # Inputs for gear properties
        
        # Input for Module with change event binding
        self.module_entry = ttk.Entry(self)
        self.module_entry.insert(0, self.DEFAULT_MODULE)
        self.module_entry.bind('<KeyRelease>', self.on_module_change)
        
        # Input for Number of teeth with change event binding
        self.num_teeth_entry = ttk.Entry(self)
        self.num_teeth_entry.insert(0, self.DEFAULT_NUM_TEETH)
        self.num_teeth_entry.bind('<KeyRelease>', self.on_num_teeth_change)
        
        # Input for Base diameter with change event binding
        self.base_diameter_entry = ttk.Entry(self)
        self.base_diameter_entry.insert(0, self.DEFAULT_NUM_TEETH * self.DEFAULT_MODULE)
        self.base_diameter_entry.bind('<KeyRelease>', self.on_base_diameter_change)

        # Input for Pressure Angle with change event binding
        self.pressure_angle_entry = ttk.Entry(self)
        self.pressure_angle_entry.insert(0, self.DEFAULT_PRESSURE_ANGLE_DEG)
        self.pressure_angle_entry.bind('<KeyRelease>', self.on_pressure_angle_change)

        # Setup UI for gear properties using grid layout
        self.setup_ui("Module (M):", self.module_entry, 1)
        self.setup_ui("Number of teeth* (N):", self.num_teeth_entry, 2)
        self.setup_ui("Base diameter* (D):", self.base_diameter_entry, 3)
        self.setup_ui("Pressure Angle (PA):", self.pressure_angle_entry, 4)

        # Animation controls
        self.animation_speed_entry = ttk.Entry(self)
        self.setup_ui("Animation Speed (RPM):", self.animation_speed_entry, 5)
        self.animation_button = ttk.Button(self, text="Start Animation", command=self.toggle_animation)
        self.animation_button.grid(row=5, column=2, columnspan=2, sticky='ew')

        # Canvas for displaying gears
        self.canvas = tk.Canvas(self, width=500, height=400, background="white")
        self.canvas.grid(row=6, column=0, columnspan=4, sticky='nsew')

        # Download options (Placeholder: Implement file generation logic)
        self.download_dxf_button = ttk.Button(self, text="Download DXF", command=self.download_dxf)
        self.download_dxf_button.grid(row=7, column=0, columnspan=2, sticky='ew')
        self.download_svg_button = ttk.Button(self, text="Download SVG", command=self.download_svg)
        self.download_svg_button.grid(row=7, column=2, columnspan=2, sticky='ew')

        # Configure the grid to distribute extra space to the canvas
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(6, weight=1)  # Give the canvas row extra space

    def setup_ui(self, label_text, widget, row):
        label = ttk.Label(self, text=label_text)
        label.grid(row=row, column=0, sticky='e')
        widget.grid(row=row, column=1, sticky='ew', padx=5)
    
    def on_module_change(self, event=None):
        # This method will be called whenever the module entry changes
        try:
            module = float(self.module_entry.get())
            num_teeth = int(self.num_teeth_entry.get())
            pressure_angle = float(self.pressure_angle_entry.get())

            # Calculate base diameter based on module and number of teeth
            base_diameter = module * num_teeth
            # Update the base diameter entry
            self.base_diameter_entry.delete(0, tk.END)
            self.base_diameter_entry.insert(0, str(base_diameter))

            # Recalculate gear geometry
            # This assumes that you have a method to recalculate gear geometry based on new parameters
            self.recalculate_gear_geometry(module, num_teeth, pressure_angle)

        except ValueError:
            # Handle the case where the entry values are not valid numbers
            pass
        
    def on_num_teeth_change(self, event=None):
        # This method will be called whenever the number of teeth entry changes
        try:
            module = float(self.module_entry.get())
            num_teeth = int(self.num_teeth_entry.get())
            pressure_angle = float(self.pressure_angle_entry.get())

            # Calculate base diameter based on module and number of teeth
            base_diameter = module * num_teeth
            # Update the base diameter entry
            self.base_diameter_entry.delete(0, tk.END)
            self.base_diameter_entry.insert(0, str(base_diameter))

            # Recalculate gear geometry
            # This assumes that you have a method to recalculate gear geometry based on new parameters
            self.recalculate_gear_geometry(module, num_teeth, pressure_angle)

        except ValueError:
            # Handle the case where the entry values are not valid numbers
            pass
        
    def on_base_diameter_change(self, event=None):
        # This method will be called whenever the base diameter entry changes
        try:
            module = float(self.module_entry.get())
            num_teeth = int(self.num_teeth_entry.get())
            base_diameter = float(self.base_diameter_entry.get())
            pressure_angle = float(self.pressure_angle_entry.get())

            # Recalculate module and number of teeth based on base diameter
            # This assumes that you have a method to recalculate module and number of teeth based on base diameter
            self.recalculate_module_and_num_teeth(base_diameter, pressure_angle)

        except ValueError:
            # Handle the case where the entry values are not valid numbers
            pass
        
    def on_pressure_angle_change(self, event=None):
        # This method will be called whenever the pressure angle entry changes
        try:
            module = float(self.module_entry.get())
            num_teeth = int(self.num_teeth_entry.get())
            pressure_angle = float(self.pressure_angle_entry.get())

            # Recalculate gear geometry
            # This assumes that you have a method to recalculate gear geometry based on new parameters
            self.recalculate_gear_geometry(module, num_teeth, pressure_angle)

        except ValueError:
            # Handle the case where the entry values are not valid numbers
            pass
        
        
    def recalculate_gear_geometry(self, module, num_teeth, pressure_angle):
        # Placeholder for gear geometry recalculation logic
        # Update existing gears with new parameters or create a new default gear
        pass
    
    def create_default_gear(self):
        # Create the default gear with a position at the origin
        default_gear = Gear(
            num_teeth=self.DEFAULT_NUM_TEETH,
            module=self.DEFAULT_MODULE,
            tooth_width=self.DEFAULT_BASE_DIAMETER,  # Update this calculation as needed
            pressure_angle_deg=self.DEFAULT_PRESSURE_ANGLE_DEG,
            position=(0, 0),
            rotation_speed=1,
            connection_angle=0
        )
        default_gear.generate_gear_geometry()
        self.gears.append(default_gear)
        self.update_gear_display()
    
    def add_gear(self):
        # Calculate position for the new gear
        if self.gears:
            last_gear = self.gears[-1]
            # Calculate the position to place the new gear next to the last gear
            new_x_position = last_gear.position[0] + (last_gear.module * last_gear.num_teeth) + (self.DEFAULT_MODULE * self.DEFAULT_NUM_TEETH)
            new_position = (new_x_position, last_gear.position[1])
        else:
            new_position = (0, 0)  # Starting position for the first gear

        # Create the new gear with the calculated position
        new_gear = Gear(
            num_teeth=int(self.num_teeth_entry.get()),
            module=float(self.module_entry.get()),
            tooth_width=self.calculate_tooth_width(module=float(self.module_entry.get()), num_teeth=int(self.num_teeth_entry.get())),
            pressure_angle_deg=float(self.pressure_angle_entry.get()),
            position=new_position,
            rotation_speed=1,
            connection_angle=0
        )
        new_gear.generate_gear_geometry()
        self.gears.append(new_gear)
        self.update_gear_display()

    def calculate_next_gear_position(self, last_gear):
        # This is a placeholder for the calculation logic
        # You should implement the logic based on how the gears should be positioned relative to each other
        next_x = last_gear.position[0] + (last_gear.module * last_gear.num_teeth)  # Simple example for horizontal positioning
        next_y = last_gear.position[1]  # Keeping y the same for horizontal layout
        return (next_x, next_y)

    def calculate_tooth_width(self, module, num_teeth):
        # Placeholder logic for calculating tooth width, adjust as needed:
        pitch_diameter = module * num_teeth
        tooth_width = pitch_diameter * np.pi / num_teeth  # Example calculation
        return tooth_width

    def remove_gear(self):
        if self.gears:
            self.gears.pop()
            self.update_gear_display()

    def update_gear_display(self):
        self.canvas.delete("all")
        for gear in self.gears:
            gear.draw(self.canvas)

    def toggle_animation(self):
        self.animation_running = not self.animation_running
        self.animation_button.config(text="Stop Animation" if self.animation_running else "Start Animation")
        if self.animation_running:
            self.perform_animation()

    def perform_animation(self):
        if self.animation_running:
            # Placeholder for animation logic
            self.after(100, self.perform_animation)

    def stop_animation(self):
        self.animation_running = False
        
    # Placeholder methods for download functionality
    def download_dxf(self):
        # Implement the logic to generate and download DXF file
        pass

    def download_svg(self):
        # Implement the logic to generate and download SVG file
        pass

if __name__ == "__main__":
    app = GearGeneratorApp()
    app.mainloop()

unknown