# import os

# # get the absolute path of the src directory
# src_path = os.path.abspath('G:/Other computers/My Laptop/UMass_CS/CS326_WebProgramming/Live Dialogue Options/LIVE_DIALOGUE_OPTIONS/src')

# # get the absolute path of the misc directory
# misc_path = os.path.abspath('G:/Other computers/My Laptop/UMass_CS/CS326_WebProgramming/Live Dialogue Options/LIVE_DIALOGUE_OPTIONS/misc')

import os
import datetime

# get the absolute path of the src directory
src_path = os.path.abspath('G:/My Drive/Coding Projects/2023/Live Dialogue Assistant/src')

# get the absolute path of the misc directory
misc_path = os.path.abspath('G:/My Drive/Coding Projects/2023/Live Dialogue Assistant/development_utils')

# get the current date and time
now = datetime.datetime.now()

# create the combined source file in the misc directory
with open(os.path.join(misc_path, 'combined_src.py'), 'w') as combined_file:
    # write the date of creation at the top of the file
    combined_file.write(f'# Combined source file created on {now.strftime("%Y-%m-%d %H:%M:%S")}\n\n')
    # iterate through all the directories and files in the src directory
    for root, dirs, files in os.walk(src_path):
        # iterate through each .py file in the current directory
        for py_file in files:
            if py_file.endswith('.py'):
                # write the name of the file as a comment in the combined file
                combined_file.write(f'# {os.path.join(root, py_file)}\n')
                # open the .py file and write its contents to the combined file
                with open(os.path.join(root, py_file), 'r') as file:
                    contents = file.read()
                    if not contents.strip():
                        # write the message if the file is empty
                        combined_file.write('File contains nothing currently\n')
                    else:
                        combined_file.write(contents)
                    # write a blank line to the combined file
                    combined_file.write('\n')