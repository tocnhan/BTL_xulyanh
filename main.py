import tkinter as tk
from tkinter import filedialog, Text, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import csv
# Thay thế phần giao diện hiển thị ảnh bằng Canvas


# Hàm hiển thị ảnh trên Canvas
def display_image_on_canvas(canvas, image_path):
    img = Image.open(image_path)
    
    # Lấy kích thước canvas
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    # Resize ảnh sao cho vừa với kích thước canvas, giữ tỷ lệ
    img.thumbnail((canvas_width, canvas_height))
    img_tk = ImageTk.PhotoImage(img)
    
    # Clear canvas trước khi vẽ ảnh mới
    canvas.delete("all")
    
    # Tính toán để căn giữa ảnh trên canvas
    x_offset = (canvas_width - img_tk.width()) // 2
    y_offset = (canvas_height - img_tk.height()) // 2
    canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=img_tk)
    
    # Lưu tham chiếu ảnh để tránh bị garbage collected
    canvas.image = img_tk
# Hàm phát hiện đối tượng
def detect_objects(image_path):
    # Đọc mô hình YOLO
    net = cv2.dnn.readNet(r"D://@@vscode_lab//python//btl_xla//yolov4.weights", 
                          r"D://@@vscode_lab//python//btl_xla//yolov4.cfg")

    # Đọc các lớp đối tượng (classes)
    with open("D://@@vscode_lab//python//btl_xla//coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]
    
    # Mở ảnh
    img = cv2.imread(image_path)
    
    # Kiểm tra nếu ảnh không được mở thành công
    if img is None:
        messagebox.showerror("Error", "Failed to load image! Please check the file path.")
        return None, []

    height, width, channels = img.shape
    
    # Tiền xử lý ảnh cho YOLO
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    result_info = []

    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = confidences[i]
            result_info.append((label, confidence, x, y, w, h))
            color = (0, 255, 0)
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, f"{label} {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return img, result_info

# Hàm chọn ảnh
def open_image():
    global img_path, result_list
    img_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
    if img_path:
        display_image_on_canvas(canvas, img_path)
        result_list.delete(1.0, tk.END)

# Hàm phát hiện đối tượng và hiển thị
def detect_and_display():
    if not img_path:
        result_list.insert(tk.END, "Please select an image first!\n")
        return
    
    detected_img, result_info = detect_objects(img_path)
    
    if detected_img is not None:
        cv2.imwrite("detected_image_with_boxes.jpg", detected_img)
        display_image_on_canvas(canvas, "detected_image_with_boxes.jpg")
    
    # Hiển thị thông tin trong Text widget
    result_list.delete(1.0, tk.END)
    result_list.insert(tk.END, "Detected Objects:\n")
    for info in result_info:
        label, confidence, x, y, w, h = info
        result_list.insert(tk.END, f"{label} ({confidence:.2f}): x={x}, y={y}, w={w}, h={h}\n")
# Hàm lưu kết quả
def save_results():
    if not img_path:
        messagebox.showerror("Error", "No results to save!")
        return
    
    try:
        with open("results.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Label", "Confidence", "X", "Y", "Width", "Height"])
            for info in result_info:
                writer.writerow(info)
        messagebox.showinfo("Success", "Results saved to results.csv!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save results: {e}")

# Tạo giao diện chính
root = tk.Tk()
root.title("Object Detection System")
root.geometry("800x800")
root.resizable(True, True)

img_path = ""
#panel = tk.Label(root, bg="gray", text="Image Preview", width=60, height=15)
#panel.pack(side="top", padx=10, pady=10)

btn_frame = tk.Frame(root)
btn_frame.pack(side="top", padx=10, pady=10)

btn_select = tk.Button(btn_frame, text="Select Image", command=open_image, width=20, bg="lightblue", font=("Arial", 12))
btn_select.pack(pady=5)

btn_detect = tk.Button(btn_frame, text="Detect Objects", command=detect_and_display, width=20, bg="lightgreen", font=("Arial", 12))
btn_detect.pack(pady=5)

btn_save = tk.Button(btn_frame, text="Save Results", command=save_results, width=20, bg="orange", font=("Arial", 12))
btn_save.pack(pady=5)

result_list = tk.Text(root, height=10, width=60, font=("Arial", 10))
result_list.pack(side="top", padx=10, pady=10)

# Panel để hiển thị ảnh kết quả với nhãn và bounding boxes

canvas = tk.Canvas(root, bg="gray", width=500, height=500)
canvas.pack(side="top", padx=10, pady=10)
root.mainloop()
