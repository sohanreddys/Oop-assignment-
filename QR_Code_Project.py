import tkinter as tk
from ttkbootstrap import ttk
import qrcode
import os
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog
import base64
import re
# from roboflow_access import RoboflowHelper
import cv2
from pyzbar.pyzbar import decode as qr_decode
from roboflow import Roboflow
import numpy as np
import webbrowser


rf = Roboflow(api_key="y5zU37hfUfMNhr3EQxvN")
project = rf.workspace("qr-code-detection").project("qr-detection-5qieq")
version = project.version(4)
dataset = version.download("yolov7")



model = project.version(4).model



def convert_png_to_jpg(file_path):
    """
    Converts a PNG file to JPG format if the file is in PNG format.

    Parameters:
    - file_path (str): The path to the image file.

    Returns:
    - new_file_path (str): The path to the converted JPG file, or the original path if not converted.
    """
    # Check if the file is a PNG
    if file_path.lower().endswith('.png'):
        # Open the PNG image
        png_image = Image.open(file_path)
        
        # Convert the image to RGB mode (necessary for JPG format)
        rgb_image = png_image.convert('RGB')
        
        # Create the new file path with a .jpg extension
        new_file_path = file_path[:-4] + '.jpg'
        
        # Save the image in JPG format
        rgb_image.save(new_file_path, 'JPEG')
        
        print(f"Converted {file_path} to {new_file_path}")
        return new_file_path
    else:
        print(f"{file_path} is not a PNG file. No conversion needed.")
        return file_path


def read_qr(path):
    file_path = convert_png_to_jpg(path)

    image = Image.open(file_path)
    img = np.array(image)


    result=model.predict(file_path, confidence=40, overlap=30).json()
    prediction=result['predictions'][0]
    roi_x = int(prediction['x'] - prediction['width'] / 2)
    roi_y = int(prediction['y'] - prediction['height'] / 2)
    roi_width = int(prediction['width'])
    roi_height = int(prediction['height'])

    roi = img[roi_y:roi_y+roi_height, roi_x:roi_x+roi_width]

    global output_text

    output_text = ['QR Data:', decoder(roi)]

    display_output(output_text)

    messagebox.showinfo('QR Data:' , output_text[1])

def on_enter(event):
    output_textbox.config(foreground="blue", cursor="hand2")

def on_leave(event):
    output_textbox.config(foreground="black", cursor="")

def on_click(event):

    if is_link(output_text[1]):
        
        open_link(output_text[1])
    else:
        copy_to_clipboard(output_text[1])

def is_link(text):
    # Regex pattern for matching URLs
    pattern = r'\b((?:(https?|ftp)://)?(?:[\w\-]+\.)+[a-z]{2,6}(?:/[\w\-./?%&=]*)?)\b'
    if re.match(pattern, text):
        return True
    else:
        return False

def copy_to_clipboard(event):
    # Clear the clipboard
    scrollable_frame.clipboard_clear()
    # Append the label's text to the clipboard
    scrollable_frame.clipboard_append(output_text[1])
    # Notify the user (optional)
    messagebox.showinfo('Link/Text copied', "Text copied to clipboard!")

def open_link(link):

    webbrowser.open_new(link)

def decoder(image):
    gray_img = cv2.cvtColor(image,0)
    qr = qr_decode(gray_img)[0]

    qrCodeData = qr.data.decode("utf-8")
    return qrCodeData

def display_output(output):
    output_textbox.config(state=tk.NORMAL)
    output_textbox.delete("1.0", tk.END)
    output_textbox.insert(tk.END, output)
    output_textbox.config(state=tk.DISABLED)

def convert(file):
    # Define the regex patterns for text and image files
    text_file_pattern = re.compile(r'.*\.txt$', re.IGNORECASE)
    image_file_pattern = re.compile(r'.*\.png$', re.IGNORECASE)
    image_file_pattern1 = re.compile(r'.*\.jpg$', re.IGNORECASE)
   
    if text_file_pattern.match(file):
        return text_to_string(content1.get())
    elif image_file_pattern.match(file) or image_file_pattern1.match(file):
        return image_to_base64(content1.get())
    else:
        return file
    
def text_to_string(filename):
    try:
        # Open the file in read mode
        with open(filename, 'rb') as file:
            # Read the file contents and store in a string
            file_contents = file.read()
    except FileNotFoundError:
        messagebox.showerror('Error', 'File Not found')
    except IOError:
        messagebox.showerror('Error',"Error reading file.")
    return file_contents
    

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        base64_str = base64.b64encode(image_file.read()).decode('utf-8')
    return base64_str

def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")])
    if file_path:
        load_image(file_path)
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)


# Function to load the image and display it
def load_image(file_path):
    img = Image.open(file_path)
    img_tk = ImageTk.PhotoImage(img)
    image_label.config(image=img_tk)
    image_label.image = img_tk  # Keep a reference to avoid garbage collection


def generate_qr():
     # Ensure the save location directory exists
    if not os.path.exists(str(location_var1.get())):
        os.makedirs(str(location_var1.get()))
    
    
    # Full path for the QR code image
    qr_path = os.path.join(str(location_var1.get()), str(created_file.get())+".png")
    
    # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    content  = convert(str(content1.get()))

    qr.add_data(content)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    
    # Save the image
    img.save(qr_path)
    messagebox.showinfo('Task Accomplished',f"QR code saved at {qr_path}")


# Main window setup
window = tk.Tk()
window.title('QR Code Framework')
window.geometry('800x500')
window.configure(bg='#f0f0f0')

# Style configuration
style = ttk.Style()
style.configure('TNotebook.Tab', font=('Calibri', 12, 'bold'))
style.configure('TLabel', background='#f0f0f0')
style.configure('TButton', font=('Calibri', 12))
style.configure('TFrame', background='#f0f0f0')

# Creating a notebook
notebook = ttk.Notebook(window)
notebook.pack(expand=True, fill='both', padx=10, pady=10)

# Tab 1: QR Code Generator
tab1 = ttk.Frame(notebook, relief=tk.GROOVE, padding=20)
tab1.configure(style='TFrame')

label1 = ttk.Label(tab1, text='QR Code Generator', font='Calibri 28 bold', background='#e6f7ff')
label1.pack(pady=10, padx=10, fill='x')

label2 = ttk.Label(tab1, text='Enter the Image/Text file location or some text', font='Calibri 15')
label2.pack(pady=5)
content_var1 = tk.StringVar()
content1 = ttk.Entry(tab1, textvariable=content_var1, width=50, font='Calibri 12')
content1.pack(pady=5)

label3 = ttk.Label(tab1, text='Enter memory location', font='Calibri 15')
label3.pack(pady=5)
location_var1 = tk.StringVar()
location1 = ttk.Entry(tab1, textvariable=location_var1, width=50, font='Calibri 12')
location1.pack(pady=5)

label4 = ttk.Label(tab1, text='Enter a name for QR', font='Calibri 15')
label4.pack(pady=5)
created_file = tk.StringVar()
file_name_creation = ttk.Entry(tab1, textvariable=created_file, width=50, font='Calibri 12')
file_name_creation.pack(pady=5)

generate_button = ttk.Button(tab1, text='Generate QR', command=generate_qr)
generate_button.pack(pady=20)

# Tab 2: QR Code Reader with scrollable content
tab2 = ttk.Frame(notebook, relief=tk.GROOVE, padding=20)
tab2.configure(style='TFrame')

# Create a canvas and a scrollbar
canvas = tk.Canvas(tab2)
scrollbar = ttk.Scrollbar(tab2, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Add the scrollable frame to the canvas
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

label2 = ttk.Label(scrollable_frame, text='QR Code Reader', font='Calibri 28 bold', background='#e6f7ff')
label2.pack(pady=10, padx=10, fill='x')

file_variable = tk.StringVar(value='Enter file path')

entry_frame = ttk.Frame(scrollable_frame)
file_entry = ttk.Entry(entry_frame, textvariable=file_variable, font='Calibri 15', width=40)
file_entry.pack(side='left', padx=5)
select_button = ttk.Button(entry_frame, text='Select', command=open_image)
select_button.pack(side='left', padx=5)
entry_frame.pack(pady=10)

image_label = ttk.Label(scrollable_frame)
image_label.pack(pady=10)

file_entry.bind('<Return>', lambda event: load_image(file_variable.get()))

read_button = ttk.Button(scrollable_frame, text='Read', command=lambda: read_qr(file_variable.get()))
read_button.pack(pady=20)

# Text widget for displaying output (multiline)
output_textbox = tk.Text(scrollable_frame, height=10, wrap="word", font='Calibri 12', borderwidth=2, relief="sunken")
output_textbox.pack(pady=10, fill='both', expand=True)
output_textbox.config(state=tk.DISABLED)

output_textbox.bind("<Enter>", on_enter)
output_textbox.bind("<Leave>", on_leave)
output_textbox.bind("<Button-1>", on_click)

# Add tabs to the notebook
notebook.add(tab1, text='Generate')
notebook.add(tab2, text='Read')

# Run the main loop
window.mainloop()
