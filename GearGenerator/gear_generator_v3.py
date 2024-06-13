import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt

# Involute curve function for a single tooth
def involute_curve(base_radius, num_points=100):
    # Generate the involute curve points
    t = np.linspace(0, np.pi / 4, num_points)  # Involute angle
    x = base_radius * (np.cos(t) + t * np.sin(t))
    y = base_radius * (np.sin(t) - t * np.cos(t))
    return x, y

# # Function to draw the complete gear
# def draw_gear(num_teeth, pitch_radius):
#     # Define the base circle radius
#     base_radius = pitch_radius * np.cos(np.pi / num_teeth)

#     # Create a figure and axis for drawing
#     fig, ax = plt.subplots()

#     # Angle between teeth in radians
#     tooth_angle = 2 * np.pi / num_teeth

#     # Draw each tooth
#     for i in range(num_teeth):
#         # Generate the involute curve for one side of the tooth
#         x, y = involute_curve(base_radius)

#         # Rotate the involute curve to the correct position
#         theta = i * tooth_angle
#         x_rot = x * np.cos(theta) - y * np.sin(theta)
#         y_rot = x * np.sin(theta) + y * np.cos(theta)

#         # Draw the involute curve for one side of the tooth
#         ax.plot(x_rot, y_rot, 'b')

#         # Reflect the involute across the Y-axis to get the other side of the tooth
#         ax.plot(x_rot, -y_rot, 'b')

#     # Draw the circle representing the pitch radius
#     circle = plt.Circle((0, 0), pitch_radius, fill=False, color='red', linestyle='--')
#     ax.add_artist(circle)

#     # Set equal aspect ratio
#     ax.set_aspect('equal')

#     # Set limits to get a better view
#     ax.set_xlim([-pitch_radius*1.5, pitch_radius*1.5])
#     ax.set_ylim([-pitch_radius*1.5, pitch_radius*1.5])

#     plt.grid(True)
#     plt.show()

# # Draw a gear with 10 teeth and a pitch radius of 20 units
# draw_gear(10, 20)

def generate_gear_tooth(num_teeth, pitch_radius, addendum, dedendum, num_points=100):
    # Base Circle Radius
    base_radius = pitch_radius * np.cos(np.pi / num_teeth)
    # Addendum and Dedendum Radius
    outside_radius = pitch_radius + addendum
    root_radius = max(pitch_radius - dedendum, 0)
    
    # Involute Function Definition
    def involute(base_radius, t):
        return base_radius * (np.cos(t) + t * np.sin(t)), base_radius * (np.sin(t) - t * np.cos(t))
    
    # Initialize Points
    angles = np.linspace(0, np.pi/4, num_points)
    x_vals, y_vals = involute(base_radius, angles)
    
    # Tooth Thickness Angle at Pitch Circle
    tooth_thickness_angle = 2 * np.pi / (2 * num_teeth)
    # Back Calculate to Base Circle
    tooth_thickness_angle_base = np.tan(tooth_thickness_angle) - tooth_thickness_angle
    
    # Find the points where the involute meets the pitch circle
    pitch_point_x, pitch_point_y = involute(base_radius, tooth_thickness_angle_base)
    
    # Calculate the angle where the tooth meets the outside circle
    outside_intersect_angle = np.sqrt((outside_radius**2 - base_radius**2) / base_radius**2)
    outside_x, outside_y = involute(base_radius, outside_intersect_angle)
    
    # Create the addendum circle segment
    addendum_angle = np.arctan2(outside_y, outside_x)  # Ending angle for the addendum segment
    addendum_angles = np.linspace(addendum_angle, tooth_thickness_angle, num_points//2)
    addendum_x = outside_radius * np.cos(addendum_angles)
    addendum_y = outside_radius * np.sin(addendum_angles)
    
    # Create the dedendum circle segment
    dedendum_angles = np.linspace(-tooth_thickness_angle, tooth_thickness_angle, num_points)
    dedendum_x = root_radius * np.cos(dedendum_angles)
    dedendum_y = root_radius * np.sin(dedendum_angles)
    
    # Combine points to form the tooth profile
    tooth_x = np.concatenate((dedendum_x, [pitch_point_x], x_vals, [outside_x], addendum_x))
    tooth_y = np.concatenate((dedendum_y, [pitch_point_y], y_vals, [outside_y], addendum_y))
    
    return tooth_x, tooth_y

def draw_gear(num_teeth, pitch_radius, addendum, dedendum):
    # Create a figure and axis for drawing
    fig, ax = plt.subplots()
    
    # Generate the points for a single tooth
    tooth_x, tooth_y = generate_gear_tooth(num_teeth, pitch_radius, addendum, dedendum)
    
    # Draw the full gear by rotating the tooth profile
    for i in range(num_teeth):
        angle = i * 2 * np.pi / num_teeth
        rot_matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        rotated_tooth = rot_matrix @ np.vstack((tooth_x, tooth_y))
        
        # Draw the tooth profile
        ax.plot(rotated_tooth[0], rotated_tooth[1], 'b-')
        ax.plot(rotated_tooth[0], -rotated_tooth[1], 'b-')  # Reflection for the other side
        
    # Set equal aspect ratio
    ax.set_aspect('equal')
    
    # Set limits to get a better view
    ax.set_xlim([-pitch_radius*2, pitch_radius*2])
    ax.set_ylim([-pitch_radius*2, pitch_radius*2])
    
    plt.grid(True)
    plt.show()

# Draw a gear with 10 teeth, pitch radius of 20, addendum of 1, and dedendum of 1.25
draw_gear(10, 20, 1, 1.25)

def on_draw_button_click():
    num_teeth = int(num_teeth_entry.get())
    pitch_radius = float(pitch_radius_entry.get())
    draw_gear(num_teeth, pitch_radius)

def save_gear_to_file(fig, filename):
    fig.savefig(filename)

# In the draw_gear function, before plt.show(), call:
# save_gear_to_file(fig, 'gear_design.png')



class GearGeneratorApp:
    def __init__(self, root):
        self.setup_gui(root)
        # Additional setup for gear calculations and drawing

    def setup_gui(self, root):
        # Create and place GUI widgets (buttons, entries, etc.)
        pass

    def calculate_gear(self):
        # Calculate gear tooth profiles and other parameters
        pass

    def draw_gear(self):
        # Use a drawing library to visualize the gear
        pass

    def animate_gear(self):
        # Animate the gear if needed
        pass

    def save_gear(self, format):
        # Save the gear design to a file
        pass

    # Additional methods as needed for callbacks and logic

root = tk.Tk()
root.title("Gear Generator")

# Number of teeth
tk.Label(root, text="Number of Teeth:").grid(row=0, column=0)
num_teeth_entry = tk.Entry(root)
num_teeth_entry.grid(row=0, column=1)
num_teeth_entry.insert(0, "10")  # Default value

# Pitch radius
tk.Label(root, text="Pitch Radius:").grid(row=1, column=0)
pitch_radius_entry = tk.Entry(root)
pitch_radius_entry.grid(row=1, column=1)
pitch_radius_entry.insert(0, "20.0")  # Default value

# Draw button
draw_button = tk.Button(root, text="Draw Gear", command=on_draw_button_click)
draw_button.grid(row=2, column=0, columnspan=2)

root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = GearGeneratorApp(root)
    root.mainloop()
