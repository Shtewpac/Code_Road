import os
import logging
from panda3d.core import Shader

class ShaderLoader:
    @staticmethod
    def load_shader(vertex_path, fragment_path):
        try:
            if not os.path.exists(vertex_path) or not os.path.exists(fragment_path):
                raise FileNotFoundError(f"Shader file not found: {vertex_path} or {fragment_path}")
            shader = Shader.load(Shader.SL_GLSL, vertex=vertex_path, fragment=fragment_path)
            logging.info(f"Shader loaded successfully: {vertex_path}, {fragment_path}")
            return shader
        except Exception as e:
            logging.error(f"Error loading shader: {e}")
            raise