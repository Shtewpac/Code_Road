import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import random
import os
import logging

logging.basicConfig(level=logging.INFO)

class ProceduralTextureGenerator:
    @staticmethod
    def generate_texture(width=512, height=512):
        try:
            logging.info("Starting procedural texture generation.")
            
            # Create a new image with white background
            image = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(image)

            # Generate random patterns, photos, digital art, and pixel art
            for _ in range(100):  # Number of random elements
                x0, y0 = random.randint(0, width), random.randint(0, height)
                x1, y1 = random.randint(0, width), random.randint(0, height)
                color = tuple(np.random.randint(0, 256, size=3))
                draw.line((x0, y0, x1, y1), fill=color, width=3)

            # Apply a blur filter to create a collage effect
            image = image.filter(ImageFilter.GaussianBlur(2))

            # Save the texture
            output_path = 'assets/textures/procedural_texture.png'
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path)

            logging.info(f"Procedural texture generated and saved to {output_path}.")
            return output_path
        except Exception as e:
            logging.error("Error generating procedural texture: %s", str(e), exc_info=True)
            raise