import subprocess
import logging
import os

class FFmpegDatamosh:
    @staticmethod
    def remove_iframes(input_file, output_file):
        try:
            command = [
                'ffmpeg', '-y', '-i', input_file, '-an', '-c:v', 'copy', output_file
            ]
            subprocess.run(command, check=True)
            logging.info(f"I-frames removed successfully from {input_file} and saved to {output_file}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error removing I-frames: {e}")
            raise

    @staticmethod
    def duplicate_pframes(input_file, output_file, times=3):
        try:
            command = [
                'ffmpeg', '-y', '-i', input_file, '-vf', f'loop={times}:1:0', output_file
            ]
            subprocess.run(command, check=True)
            logging.info(f"P-frames duplicated {times} times successfully for {input_file} and saved to {output_file}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error duplicating P-frames: {e}")
            raise

    @staticmethod
    def add_noise(input_file, output_file, noise_level=0.1):
        try:
            command = [
                'ffmpeg', '-y', '-i', input_file, '-vf', f'lutyuv=y=val+random({noise_level})', output_file
            ]
            subprocess.run(command, check=True)
            logging.info(f"Noise added successfully to {input_file} and saved to {output_file}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error adding noise: {e}")
            raise

    @staticmethod
    def preprocess_texture(input_file, output_file):
        try:
            temp_file1 = "temp_no_iframes.mp4"
            temp_file2 = "temp_duplicated_pframes.mp4"

            FFmpegDatamosh.remove_iframes(input_file, temp_file1)
            FFmpegDatamosh.duplicate_pframes(temp_file1, temp_file2)
            FFmpegDatamosh.add_noise(temp_file2, output_file)

            os.remove(temp_file1)
            os.remove(temp_file2)

            logging.info(f"Texture preprocessing completed successfully for {input_file} and saved to {output_file}")
        except Exception as e:
            logging.error(f"Error in texture preprocessing: {e}")
            raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    input_texture = "assets/textures/chaos.png"  # INPUT_REQUIRED {path to input texture file}
    output_texture = "assets/textures/chaos_moshed.png"  # INPUT_REQUIRED {path to output texture file}
    FFmpegDatamosh.preprocess_texture(input_texture, output_texture)