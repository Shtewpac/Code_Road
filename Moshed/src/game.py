from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, AmbientLight, DirectionalLight, LVector3, Shader
from .first_person_camera import FirstPersonCamera
from .procedural_generation import ProceduralGeneration
from .shader_loader import ShaderLoader
from .player_movement import PlayerMovement  # Import the PlayerMovement class
from .ffmpeg_datamosh import FFmpegDatamosh  # Import the FFmpeg datamosh preprocessing class
from .procedural_texture_generator import ProceduralTextureGenerator  # Import the ProceduralTextureGenerator class

class MoshedGame(ShowBase):
    def __init__(self):
        try:
            super().__init__()
            self.setup_window()
            self.setup_scene()
            self.setup_camera()
            self.setup_shaders()  # New function to set up shaders
            self.player_movement = PlayerMovement(self)  # Initialize PlayerMovement
            print("MoshedGame initialized successfully.")
        except Exception as e:
            print(f"Error initializing MoshedGame: {e}")
            raise

    def setup_window(self):
        try:
            # Set up the window title
            self.win_props = WindowProperties()
            self.win_props.setTitle("Moshed: A Surreal Datamoshed Non-Euclidean Odyssey")
            self.win.requestProperties(self.win_props)
            print("Window setup completed.")
        except Exception as e:
            print(f"Error setting up window: {e}")
            raise

    def setup_scene(self):
        try:
            # Load a simple model
            self.scene = self.loader.loadModel("models/environment")
            self.scene.reparentTo(self.render)
            self.scene.setScale(0.25, 0.25, 0.25)
            self.scene.setPos(-8, 42, 0)

            # Set up lighting
            ambient_light = AmbientLight("ambient_light")
            ambient_light.setColor((0.5, 0.5, 0.5, 1))
            directional_light = DirectionalLight("directional_light")
            directional_light.setDirection(LVector3(0, 8, -2))
            directional_light.setColor((1, 1, 1, 1))

            self.render.setLight(self.render.attachNewNode(ambient_light))
            self.render.setLight(self.render.attachNewNode(directional_light))
            print("Scene setup completed.")

            # Generate and render non-euclidean geometry
            self.setup_non_euclidean_geometry()
        except Exception as e:
            print(f"Error setting up scene: {e}")
            raise

    def setup_camera(self):
        try:
            self.camera_controller = FirstPersonCamera(self)
            print("Camera setup completed.")
        except Exception as e:
            print(f"Error setting up camera: {e}")
            raise

    def setup_non_euclidean_geometry(self):
        try:
            procedural_gen = ProceduralGeneration(self)
            print("Non-euclidean geometry setup completed.")
        except Exception as e:
            print(f"Error setting up non-euclidean geometry: {e}")
            raise

    def setup_shaders(self):
        try:
            self.normal_vertex_shader_path = 'assets/shaders/datamosh_vertex.glsl'
            self.normal_fragment_shader_path = 'assets/shaders/datamosh_fragment.glsl'
            self.stop_vertex_shader_path = 'assets/shaders/stop_datamosh_vertex.glsl'
            self.stop_fragment_shader_path = 'assets/shaders/stop_datamosh_fragment.glsl'
            
            self.normal_shader = ShaderLoader.load_shader(self.normal_vertex_shader_path, self.normal_fragment_shader_path)
            self.stop_shader = ShaderLoader.load_shader(self.stop_vertex_shader_path, self.stop_fragment_shader_path)
            
            # Generate the procedural texture
            procedural_texture_path = ProceduralTextureGenerator.generate_texture()
            
            # Preprocess the texture using FFmpeg datamosh script
            output_texture_path = 'assets/textures/chaos_moshed.png'
            FFmpegDatamosh.preprocess_texture(procedural_texture_path, output_texture_path)
            
            # Load the preprocessed texture to use with the shader
            tex = self.loader.loadTexture(output_texture_path)
            self.scene.set_shader_input('tex', tex)

            self.taskMgr.add(self.update_shader_time, 'update_shader_time')
            print("Shaders setup completed.")
        except Exception as e:
            print(f"Error setting up shaders: {e}")
            raise

    def update_shader_time(self, task):
        try:
            import time  # Importing time module here instead of at the top
            self.scene.set_shader_input('time', time.time() % 100)
            
            # Check player movement state and switch shaders if necessary
            if self.player_movement.is_stopped():
                self.scene.set_shader(self.stop_shader)
            else:
                self.scene.set_shader(self.normal_shader)
                
            return task.cont
        except Exception as e:
            print(f"Error updating shader time: {e}")
            raise