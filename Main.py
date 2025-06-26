import os
import random
import threading
from tkinter import filedialog

import customtkinter as ctk
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageTk
from tensorflow import keras
from keras import layers
from ultralytics import YOLO

# Global variable for the trained YOLO model
trained_model = None

# Simple CNN Model for Vehicle Classification
def create_cnn_model(input_shape=(64, 64, 3)):
    model = keras.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(3, activation='softmax')  # Adjust based on the number of vehicle classes
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# Function to determine the lane based on vehicle position
def determine_lane(box):
    x_min, _, x_max, _ = box
    x_center = (x_min + x_max) / 2
    if x_center < 320:
        return 0
    elif x_center < 640:
        return 1
    elif x_center < 960:
        return 2
    else:
        return 3

# Predefined colors for bounding boxes
def random_color():
    return tuple(random.randint(0, 255) for _ in range(3))

# GUI Class for Traffic Control System
class TrafficControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DriveGuard Pro")
        self.root.geometry("1920x1080")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Initialize vehicle counts
        self.lane_vehicles = [0, 0, 0, 0]
        self.video_paths = []
        self.is_analyzing = False
        self.analysis_speed = 1

        # Load YOLOv8 model
        self.model = YOLO('yolov8n.pt')

        # Load CNN model
        self.cnn_model = create_cnn_model()

        # Setup GUI layout
        self.video_labels = []
        self.setup_controls()

    def setup_controls(self):
        """Setup control panel, sliders, and buttons."""
        self.controls_frame = ctk.CTkFrame(self.root)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Lane status and counts
        self.lane_labels = []
        for i in range(4):
            frame = ctk.CTkFrame(self.controls_frame)
            frame.grid(row=i, column=0, pady=5, sticky="ew")

            label = ctk.CTkLabel(frame, text=f"Lane {i + 1}", font=("Helvetica", 14, "bold"))
            label.pack(side="left")

            vehicle_count_label = ctk.CTkLabel(frame, text=f"Vehicles: 0", font=("Helvetica", 12))
            vehicle_count_label.pack(side="left", padx=10)
            self.lane_labels.append(vehicle_count_label)

        # Video display panels
        for i in range(4):
            label = ctk.CTkLabel(self.root, text=f"Lane {i + 1}", width=400, height=400)
            label.grid(row=i // 2 + 1, column=i % 2, padx=10, pady=10)
            self.video_labels.append(label)

        # Button controls
        button_frame = ctk.CTkFrame(self.root)
        button_frame.grid(row=3, column=0, pady=10, columnspan=2)

        self.train_button = ctk.CTkButton(button_frame, text="Train Model", command=self.train_model)
        self.train_button.pack(side="left", padx=10)

        self.upload_button = ctk.CTkButton(button_frame, text="Upload Footages", command=self.upload_footages)
        self.upload_button.pack(side="left", padx=10)

        self.analyze_button = ctk.CTkButton(button_frame, text="Analyze Traffic", command=self.start_traffic_analysis)
        self.analyze_button.pack(side="left", padx=10)

        self.stop_button = ctk.CTkButton(button_frame, text="Stop Analyze", command=self.stop_analysis)
        self.stop_button.pack(side="left", padx=10)

        # Prediction Label
        self.prediction_label = ctk.CTkLabel(self.root, text="", font=("Helvetica", 14, "bold"), text_color="green")
        self.prediction_label.grid(row=4, column=0, pady=10, columnspan=2)

    def train_model(self):
        global trained_model
        dataset_path = filedialog.askopenfilename(
            title="Select dataset.yaml file",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if dataset_path:
            results = YOLO('yolov8n.pt').train(data=dataset_path, epochs=50)
            trained_model = results
            self.prediction_label.configure(text="Model trained successfully.", text_color="green")

    def upload_footages(self):
        self.video_paths = filedialog.askopenfilenames(
            title="Select Traffic Footages",
            filetypes=(("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("All files", "*.*"))
        )
        if self.video_paths:
            self.prediction_label.configure(text="Footages uploaded successfully.", text_color="green")

    def start_traffic_analysis(self):
        if not self.video_paths:
            self.prediction_label.configure(text="Please upload footages first!", text_color="red")
            return

        self.is_analyzing = True
        for i, video_path in enumerate(self.video_paths):
            threading.Thread(target=self.analyze_video, args=(video_path, i)).start()

    def analyze_video(self, video_path, panel_index):
        cap = cv2.VideoCapture(video_path)
        frame_counter = 0

        while cap.isOpened() and self.is_analyzing:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_counter % self.analysis_speed != 0:
                frame_counter += 1
                continue

            results = self.model(frame)[0]
            frame_with_boxes = self.draw_bounding_boxes(frame, results)
            img_tk = ImageTk.PhotoImage(frame_with_boxes)

            self.root.after(0, lambda: self.video_labels[panel_index].configure(image=img_tk))
            self.video_labels[panel_index].image = img_tk
            frame_counter += 1

        cap.release()

    def draw_bounding_boxes(self, frame, results):
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(frame_pil)

        for result in results.boxes.xyxy:
            box = result[:4]
            lane = determine_lane(box)
            self.lane_vehicles[lane] += 1
            color = random_color()
            draw.rectangle(box.tolist(), outline=color, width=2)

        return frame_pil

    def stop_analysis(self):
        self.is_analyzing = False

# Main function to run the application
if __name__ == "__main__":
    root = ctk.CTk()
    app = TrafficControlApp(root)
    root.mainloop()
