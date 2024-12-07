
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# Resize image to fit within given dimensions while keeping the aspect ratio
def resize_image_to_fit(img, max_width, max_height):
    img_width, img_height = img.size
    ratio = min(max_width / img_width, max_height / img_height)
    return img.resize((int(img_width * ratio), int(img_height * ratio)), Image.Resampling.LANCZOS)

def open_image_with_canvas():
    global img_path, canvas_image
    img_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
    if img_path:
        img = Image.open(img_path)
        max_width, max_height = canvas.winfo_width(), canvas.winfo_height()
        img = resize_image_to_fit(img, max_width, max_height)
        img_tk = ImageTk.PhotoImage(img)
        canvas.delete("all")  # Clear previous image
        canvas_image = canvas.create_image(max_width // 2, max_height // 2, image=img_tk, anchor=tk.CENTER)
        canvas.img_tk = img_tk  # Keep a reference to prevent garbage collection

root = tk.Tk()
root.title("Canvas Image Display")
root.geometry("800x600")

canvas = tk.Canvas(root, width=800, height=400, bg="gray")
canvas.pack(side="top", padx=10, pady=10)

btn_select = tk.Button(root, text="Select Image", command=open_image_with_canvas, bg="lightblue", font=("Arial", 12))
btn_select.pack(pady=10)

root.mainloop()
