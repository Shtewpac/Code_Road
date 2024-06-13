# Moshed: A Surreal Datamoshed Non-Euclidean Odyssey

## Project Description

Moshed is an experimental first-person exploration game set in a surreal, glitchy, non-euclidean world. The game's unique visual style is achieved through the use of datamoshing techniques, which distort and warp the textures and geometry of the game world in real-time, creating a constantly shifting, dreamlike environment.

### Gameplay Features
- First-person exploration gameplay
- Surreal, datamoshed visual style
- Non-euclidean level geometry
- Real-time texture distortion effects
- Ambient, glitchy soundscape

### Technical Features
- Built using Python and Panda3D game engine
- Custom datamoshing shaders and scripts using OpenGL
- Procedural generation of non-euclidean geometry using NumPy and SciPy
- Dynamic texture warping and distortion using Pillow and OpenCV
- Optimized for smooth performance on target platforms

### Datamoshing Effects
- Real-time texture distortion using pixel sorting, compression artifacts, and other glitch art techniques implemented in Python
- Textures are procedurally generated from a random collage of patterns, photos, digital art, and pixel art using Pillow
- Distortion effects are triggered whenever the player stops moving, creating a sense of temporal instability
- Glitchy, abstract visual style enhances the surreal atmosphere of the game world

### Non-Euclidean Level Design
- Impossible spaces that loop back on themselves, featuring rooms that are bigger on the inside than the outside
- Portals that connect distant parts of the map in unexpected ways, implemented using custom Python scripts
- Hyperbolic geometry used to create spaces where straight lines diverge and triangles have angle sums less than 180 degrees, using NumPy and SciPy
- Higher dimensional spaces hinted at through tessering rooms and 4D object cross-sections, rendered using Panda3D's advanced shader capabilities
- Fractal generation used to create endlessly detailed, self-similar structures, implemented using recursive Python functions
- Shifting geometry that subtly rearranges itself as the player moves through the space, using procedural generation techniques

The goal of Moshed is to create a truly unique and disorienting exploration experience that challenges players' perceptions of space and reality. By combining cutting-edge datamoshing techniques with mind-bending non-euclidean geometry, all implemented using the power and flexibility of Python and its rich ecosystem of libraries, the game aims to push the boundaries of what is possible in interactive visual design.

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/moshed.git
   cd moshed
   ```

2. **Set up a virtual environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Install FFmpeg:**
   ```sh
   sudo apt-get install ffmpeg
   ```

## Usage

1. **Run the game:**
   ```sh
   python main.py
   ```

2. **Controls:**
   - **W**: Move forward
   - **S**: Move backward
   - **A**: Move left
   - **D**: Move right
   - **Mouse**: Look around

## Technical Details

### Datamoshing Effects

The datamoshing effects in Moshed are achieved through a combination of custom shaders and FFmpeg preprocessing. The shaders apply pixel sorting and compression artifacts in real-time, while the FFmpeg script preprocesses textures to remove I-frames, duplicate P-frames, and add noise.

#### Shader Code

The shaders are located in the `assets/shaders` directory. The `datamosh_fragment.glsl` shader implements the pixel sorting and compression artifacts, while the `stop_datamosh_fragment.glsl` shader is used when the player stops moving.

#### FFmpeg Preprocessing

The `src/ffmpeg_datamosh.py` script preprocesses textures using FFmpeg. It removes I-frames, duplicates P-frames, and adds noise to create the datamoshing effect.

#### Example Commands
```sh
ffmpeg -i assets/textures/chaos.png -an -c:v copy temp_no_iframes.mp4
ffmpeg -i temp_no_iframes.mp4 -vf loop=3:1:0 -c:v copy temp_duplicated_pframes.mp4
ffmpeg -i temp_duplicated_pframes.mp4 -vf lutyuv=y=val+random(0.1) assets/textures/chaos_moshed.png
```

### Non-Euclidean Geometry

The non-euclidean geometry is procedurally generated using NumPy and SciPy. The `src/procedural_generation.py` script creates rooms that loop back on themselves, portals that connect distant parts of the map, and hyperbolic geometry.

### Dynamic Texture Warping

Dynamic texture warping and distortion are handled using Pillow and OpenCV. The textures are procedurally generated from a random collage of patterns, photos, digital art, and pixel art.

## Contribution Guidelines

1. **Fork the repository:**
   ```sh
   git fork https://github.com/yourusername/moshed.git
   ```

2. **Create a new branch:**
   ```sh
   git checkout -b feature-branch
   ```

3. **Make your changes and commit them:**
   ```sh
   git commit -m "Description of your changes"
   ```

4. **Push to the branch:**
   ```sh
   git push origin feature-branch
   ```

5. **Create a pull request:**
   - Go to the repository on GitHub and click on "New pull request".

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.