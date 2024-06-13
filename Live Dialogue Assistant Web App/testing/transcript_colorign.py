import tkinter as tk
from tkinter import scrolledtext

# Function to update transcript
def update_transcript(transcript):
    transcript_text.delete(1.0, tk.END)
    lines = transcript.split('\n')
    for line in lines:
        line_end_index = tk.END
        transcript_text.insert(line_end_index, line + '\n')
        line_start_index = transcript_text.index(f"{line_end_index} -1 line linestart")
        line_end_index = transcript_text.index(f"{line_end_index} -1 line lineend")
        
        if "Person A" in line:
            transcript_text.tag_add("Person_A", line_start_index, line_end_index)
        elif "Person B" in line:
            transcript_text.tag_add("Person_B", line_start_index, line_end_index)

# Create main window
root = tk.Tk()
root.title("Text Coloring Test")

# Create a scrolled text widget
transcript_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10)
transcript_text.pack(pady=(10, 10), padx=10, fill=tk.BOTH, expand=True)

# Define tags for coloring
transcript_text.tag_configure("Person_A", foreground='#f00')
transcript_text.tag_configure("Person_B", foreground="red", background="yellow")

# Test data
test_transcript = "Person A: Hello!\nPerson B: Hi there!\nPerson A: How are you?\nPerson B: I'm good, thanks!"

# Update the transcript with test data
update_transcript(test_transcript)

# Run the application
root.mainloop()
# ///////////////////////////////////////////

# # import all functions from the tkinter 
# from tkinter import *

# # Create a GUI window 
# root = Tk() 

# # Create a text area box 
# # for filling or typing the information. 
# text = Text(root) 

# # insert given string in text area 
# text.insert(INSERT, "Hello, everyone!\n") 

# text.insert(END, "This is 2020.\n") 

# text.insert(END, "Pandemic has resulted in economic slowdown worldwide") 

# text.pack(expand=1, fill=BOTH) 

# # add tag using indices for the 
# # part of text to be highlighted 
# text.tag_add("start", "2.8", "1.13") 

# #configuring a tag called start 
# text.tag_config("start", background="black", 
# 				foreground="red") 

# # start the GUI 
# root.mainloop() 


# import all functions from the tkinter 
import tkinter as tk 
from tkinter.font import Font 

# create a Pad class 
# class Pad(tk.Frame): 

# 	# constructor to add buttons and text to the window 
# 	def __init__(self, parent, *args, **kwargs): 
# 		tk.Frame.__init__(self, parent, *args, **kwargs) 

# 		self.toolbar = tk.Frame(self, bg="#eee") 
# 		self.toolbar.pack(side="top", fill="x") 
		
# 		# this will add Highlight button in the window 
# 		self.bold_btn = tk.Button(self.toolbar, text="Highlight", 
# 								command=self.highlight_text) 
# 		self.bold_btn.pack(side="left") 

# 		# this will add Clear button in the window 
# 		self.clear_btn = tk.Button(self.toolbar, text="Clear", 
# 								command=self.clear) 
# 		self.clear_btn.pack(side="left") 

# 		# adding the text 
# 		self.text = tk.Text(self) 
# 		self.text.insert("end", "Pandemic has resulted in economic slowdown worldwide") 
# 		self.text.focus() 
# 		self.text.pack(fill="both", expand=True) 
		
# 		#configuring a tag called start 
# 		self.text.tag_configure("start", background="black", foreground="red") 

# 	# method to highlight the selected text 
# 	def highlight_text(self): 
		
# 		# if no text is selected then tk.TclError exception occurs 
# 		try: 
# 			self.text.tag_add("start", "sel.first", "sel.last")		 
# 		except tk.TclError: 
# 			pass

# 	# method to clear all contents from text widget. 
# 	def clear(self): 
# 		self.text.tag_remove("start", "1.0", 'end') 

# # function 
# def demo(): 

# 	# Create a GUI window 
# 	root = tk.Tk() 

# 	# place Pad object in the root window 
# 	Pad(root).pack(expand=1, fill="both") 

# 	# start the GUI 
# 	root.mainloop() 

# # Driver code 
# if __name__ == "__main__": 

# 	# function calling 
# 	demo() 
