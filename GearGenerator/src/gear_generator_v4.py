import tkinter as tk
from tkinter import simpledialog
import matplotlib.pyplot as plt
from pymadcad import gearprofile, repeat_circular, web2mesh
import numpy as np

def generate_gear(z, pitch_radius):
    # Calculate the step based on the pitch radius and number of teeth
    step = (2 * np.pi * pitch_radius) / z
    
    # Generate the gear profile
    profile = gearprofile(step=step, z=z)
    
    # Repeat the profile circularly to create the gear
    gear = repeat_circular(profile, z)
    
    # Convert to mesh for visualization (optional, depends on pymadcad version and capabilities)
    mesh = web2mesh(gear)
    
    return mesh

def visualize_gear(mesh):
    # Use matplotlib to visualize the gear
    # This section needs to be adapted based on how mesh data is structured and how you wish to display it
    plt.figure(figsize=(6,6))
    for face in mesh.faces:
        # Assuming `mesh.faces` gives you the vertices of each face
        # Adapt this code block to match the actual data structure
        x, y = zip(*[(vertex.x, vertex.y) for vertex in face])
        plt.plot(x, y, 'k-')
    plt.axis('equal')
    plt.show()

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    # Input dialog to get the number of teeth and pitch radius
    z = simpledialog.askinteger("Input", "Number of teeth:", parent=root)
    pitch_radius = simpledialog.askfloat("Input", "Pitch radius:", parent=root)
    
    if z and pitch_radius:
        mesh = generate_gear(z, pitch_radius)
        visualize_gear(mesh)
    else:
        print("Invalid input")

if __name__ == "__main__":
    main()

unknown