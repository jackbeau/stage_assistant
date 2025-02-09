"""
Author: Jack Beaumont
Date: 06/06/2024

Description: This module implements a Tkinter-based UI for managing stage
zones using video input.
It includes functionalities for video capture, cropping, and homography
transformations.
"""

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import multiprocessing
import asyncio
import cv2
import numpy as np
from gui.core.constants.styles import text, colours
import gui.pages.shared.video_utils
import logging
from gui.pages.shared.settings_manager import (
    CameraSettingsManager,
    StageZoneSettingsManager,
)
from multiprocessing import Manager
from gui.pages.settings.shared.video_processing import video_loop
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class FloatEntry(ttk.Entry):
    """
    A custom Tkinter Entry widget that only accepts float input.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vcmd = (self.register(self.validate), "%P")
        self.config(validate="all", validatecommand=vcmd)

    def validate(self, text):
        """
        Validate the input to ensure it is a valid float number.

        Args:
            text (str): The input text to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        return (
            all(char in "0123456789.-" for char in text)
            and "-" not in text[1:]
            and text.count(".") <= 1
        )


class StageZonesPage(tk.Frame):
    NAME = "Stage Zones"

    def __init__(self, parent, settings_file="settings.json", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.resizing = False
        self.stop_event = multiprocessing.Event()
        self.frame_queue = multiprocessing.Queue(maxsize=1)
        self.hist_queue = multiprocessing.Queue(maxsize=1)
        self.manager = Manager()
        self.settings = self.manager.dict()
        self.scaling_factor = 1

        # Initialize settings managers
        self.camera_settings_manager = CameraSettingsManager(settings_file)
        self.stage_zone_settings_manager = StageZoneSettingsManager(
            settings_file
        )
        self.load_settings()

        # Get video device info and their maximum resolutions
        self.get_video_device_info()

        # Start video capture and processing
        self.start_processes()

        # Start asynchronous tasks for updating frame and plot
        self.start_async_tasks()

        # Initialize points for homography and cropping
        self.dragging_point = None
        self.current_frame = None

        # Render the UI
        self.render()

    def get_video_device_info(self):
        """Get information about the video device."""
        self.video_devices = gui.pages.shared.video_utils.get_video_devices()
        try:
            device = next(
                (
                    device
                    for device in self.video_devices
                    if device["uniqueID"] == self.video_device_id
                ),
                None,
            )

            if device:
                self.video_device_name = device["localizedName"]
                self.video_device_position = device["position"]
                self.update_settings_queue()
                return

            self.video_device_position = None
            self.video_device_name = None
            self.update_settings_queue()
        except ValueError:
            self.video_device_position = None
            self.video_device_name = None
            logging.error(f"Device with ID {self.video_device_id} not found.")

    def load_settings(self):
        """Load settings from the settings managers."""
        camera_settings = self.camera_settings_manager.get_camera_settings()
        self.video_device_id = camera_settings.get("video_device_id", 0)
        self.rotation = camera_settings.get("rotation", 0)
        self.res = camera_settings.get("resolution", ())
        self.mirror_x = tk.IntVar(value=camera_settings.get("mirror_x", 0))
        self.mirror_y = tk.IntVar(value=camera_settings.get("mirror_y", 0))
        self.hist_equalisation = tk.IntVar(
            value=camera_settings.get("hist_equalisation", 0)
        )
        self.brightness = tk.DoubleVar(
            value=camera_settings.get("brightness", 50)
        )
        self.exposure = tk.DoubleVar(value=camera_settings.get("exposure", 50))
        self.contrast = tk.DoubleVar(value=camera_settings.get("contrast", 50))
        self.saturation = tk.DoubleVar(
            value=camera_settings.get("saturation", 50)
        )

        stage_zone_settings = (
            self.stage_zone_settings_manager.get_stage_zone_settings()
        )
        self.scaling_factor = stage_zone_settings.get("scaling_factor", 1)
        self.src_points = [
            (
                int(point[0] * self.scaling_factor),
                int(point[1] * self.scaling_factor),
            )
            for point in stage_zone_settings.get("src_points", [])
        ]
        self.crop_points = [
            (
                int(point[0] * self.scaling_factor),
                int(point[1] * self.scaling_factor),
            )
            for point in stage_zone_settings.get("crop_points", [])
        ]
        self.enable_crop = tk.IntVar(
            value=stage_zone_settings.get("enable_crop", 0)
        )
        self.enable_homography = tk.IntVar(
            value=stage_zone_settings.get("enable_homography", 0)
        )
        self.homography_width = tk.StringVar(
            value=stage_zone_settings.get("homography_width", "")
        )
        self.homography_height = tk.StringVar(
            value=stage_zone_settings.get("homography_height", "")
        )

        self.homography_width.trace_add("write", self.save_settings)
        self.homography_height.trace_add("write", self.save_settings)

    def save_settings(self, *args):
        """Save current settings to the settings managers."""
        if not self.crop_points:
            self.reset_crop_points()

        unscaled_src_points = [
            (
                int(point[0] / self.scaling_factor),
                int(point[1] / self.scaling_factor),
            )
            for point in self.src_points
        ]
        unscaled_crop_points = [
            (
                int(point[0] / self.scaling_factor),
                int(point[1] / self.scaling_factor),
            )
            for point in self.crop_points
        ]

        camera_settings = {
            "video_device_id": self.video_device_id,
            "video_device_pos": self.video_device_position,
            "resolution": self.res,
            "rotation": self.rotation,
            "mirror_x": self.mirror_x.get(),
            "mirror_y": self.mirror_y.get(),
            "hist_equalisation": self.hist_equalisation.get(),
            "brightness": self.brightness.get(),
            "exposure": self.exposure.get(),
            "contrast": self.contrast.get(),
            "saturation": self.saturation.get(),
        }
        self.camera_settings_manager.save_camera_settings(camera_settings)
        self.update_settings_queue()

        stage_zone_settings = {
            "src_points": unscaled_src_points,
            "crop_points": unscaled_crop_points,
            "enable_crop": self.enable_crop.get(),
            "enable_homography": self.enable_homography.get(),
            "homography_width": self.homography_width.get(),
            "homography_height": self.homography_height.get(),
            "scaling_factor": self.scaling_factor,
        }
        self.stage_zone_settings_manager.save_stage_zone_settings(
            stage_zone_settings
        )

    def update_settings_queue(self):
        """Update the settings queue with current settings."""
        self.settings.update(
            {
                "video_device_id": self.video_device_id,
                "video_device_pos": self.video_device_position,
                "resolution": self.res,
                "rotation": self.rotation,
                "mirror_x": self.mirror_x.get(),
                "mirror_y": self.mirror_y.get(),
                "hist_equalisation": self.hist_equalisation.get(),
                "brightness": self.brightness.get(),
                "exposure": self.exposure.get(),
                "contrast": self.contrast.get(),
                "saturation": self.saturation.get(),
            }
        )

    def close(self):
        """Handle closing of the camera page."""
        self.stop_event.set()
        self.video_process.terminate()
        self.video_process.join()

    def start_processes(self):
        """Start video and plot processing in separate processes."""
        self.stop_event.clear()
        self.video_process = multiprocessing.Process(
            target=video_loop,
            args=(self.frame_queue, self.stop_event, self.settings),
        )
        self.video_process.start()

    def start_async_tasks(self):
        """Start asynchronous tasks for updating frame and plot."""
        asyncio.create_task(self.update_frames())

    def reset_homography(self):
        """Reset homography points."""
        self.src_points = []
        self.update_frame_display(self.current_frame, draw_points=True)
        self.save_settings()

    def reset_crop(self):
        """Reset crop points to default."""
        self.reset_crop_points()
        self.update_frame_display(self.current_frame, draw_points=True)
        self.save_settings()

    def reset_crop_points(self):
        """Initialize crop points to default state."""
        if self.current_frame is not None:
            h, w = self.current_frame.shape[:2]
            margin = 20
            self.crop_points = [
                (margin, margin),
                (w - margin, margin),
                (w - margin, h - margin),
                (margin, h - margin),
            ]
        else:
            self.crop_points = [(20, 20), (480, 20), (480, 320), (20, 320)]

    def render(self):
        """Render the GUI."""
        lbl_description = text(
            self,
            text=(
                "Use this interface to enable cropping and homography "
                "transformation. Drag the green points to set the source "
                "quadrilateral and the red points to set the destination "
                "quadrilateral. This only works for a plane of constant "
                "height.",
            ),
            style="PageText",
        )
        lbl_description.pack(fill="x", pady=(0, 4), anchor="w")

        frm_settings = tk.Frame(self, background=colours.off_black_80)
        frm_settings.pack(fill="x", pady=(0, 4))

        chk_crop = ttk.Checkbutton(
            frm_settings,
            text="Enable Crop",
            style="Label.TCheckbutton",
            variable=self.enable_crop,
            command=self.save_settings,
        )
        chk_crop.pack(side="left", padx=(0, 8))

        chk_homography = ttk.Checkbutton(
            frm_settings,
            text="Enable Homography Transform",
            style="Label.TCheckbutton",
            variable=self.enable_homography,
            command=self.save_settings,
        )
        chk_homography.pack(side="left", padx=(0, 8))

        btn_set_homography = ttk.Button(
            frm_settings,
            text="Set Homography Points",
            command=self.set_homography_points,
            style="Label.TButton",
        )
        btn_set_homography.pack(side="left", padx=(0, 8))

        btn_rst_homography = ttk.Button(
            frm_settings,
            text="Reset Homography Points",
            command=self.reset_homography,
            style="Label.TButton",
        )
        btn_rst_homography.pack(side="left", padx=(0, 8))

        btn_rst_crop = ttk.Button(
            frm_settings,
            text="Reset Crop Points",
            command=self.reset_crop,
            style="Label.TButton",
        )
        btn_rst_crop.pack(side="left", padx=(0, 8))

        btn_capture_frame = ttk.Button(
            frm_settings,
            text="Capture New Frame",
            command=lambda: asyncio.create_task(self.apply_transformations()),
            style="Label.TButton",
        )
        btn_capture_frame.pack(side="left", padx=(0, 8))

        frm_size_inputs = tk.Frame(self, background=colours.off_black_80)
        frm_size_inputs.pack(fill="x", pady=(0, 8))

        lbl_width = text(frm_size_inputs, text="Width (mm)", style="PageText")
        lbl_width.pack(side="left", padx=(0, 4))
        self.width_entry = FloatEntry(
            frm_size_inputs, textvariable=self.homography_width
        )
        self.width_entry.pack(side="left", padx=(0, 8))

        lbl_height = text(
            frm_size_inputs, text="Height (mm)", style="PageText"
        )
        lbl_height.pack(side="left", padx=(0, 4))
        self.height_entry = FloatEntry(
            frm_size_inputs, textvariable=self.homography_height
        )
        self.height_entry.pack(side="left", padx=(0, 8))

        frm_video_and_result = tk.Frame(self, background=colours.off_black_80)
        frm_video_and_result.pack(fill="both", expand=True, pady=(0, 0))

        frm_video = tk.Frame(
            frm_video_and_result, background=colours.off_black_80
        )
        frm_video.pack(side="left", expand=True, fill="both", padx=(0, 8))

        lbl_vid_input = text(
            frm_video, text="Camera Feed", style="PageHeading2"
        )
        lbl_vid_input.pack(fill="x", pady=(0, 4))

        self.frm_video = ttk.Label(
            frm_video,
            image=None,
            anchor="center",
            justify="center",
            text="Loading video...",
            background="black",
            foreground="white",
        )
        self.frm_video.pack(expand=False)

        frm_bottom = tk.Frame(
            frm_video_and_result, background=colours.off_black_80
        )
        frm_bottom.pack(side="left", expand=True, fill="both", padx=(0, 0))

        lbl_homography_result = text(
            frm_bottom,
            text="Homography Transform Result",
            style="PageHeading2",
        )
        lbl_homography_result.pack(fill="x", pady=(0, 4))

        self.frm_transformed = ttk.Label(
            frm_bottom,
            image=None,
            anchor="center",
            justify="center",
            text="Loading transform...",
            background="black",
            foreground="white",
        )
        self.frm_transformed.pack(expand=False)

        self.frm_video.bind("<Button-1>", self.on_mouse_click)
        self.frm_video.bind("<B1-Motion>", self.on_mouse_drag)
        self.frm_video.bind("<ButtonRelease-1>", self.on_mouse_release)

    def set_homography_points(self):
        """Set homography points."""
        self.enable_homography.set(True)

    def on_mouse_click(self, event):
        """Handle mouse click to select or start dragging points for
        homography and crop."""
        widget = event.widget
        if widget == self.frm_video:
            widget_width = widget.winfo_width()
            widget_height = widget.winfo_height()
            image_width, image_height = (
                self.current_frame.shape[1],
                self.current_frame.shape[0],
            )

            scale_x = image_width / widget_width
            scale_y = image_height / widget_height
            offset_x = (widget_width - image_width / scale_x) / 2
            offset_y = (widget_height - image_height / scale_y) / 2

            point = (
                int((event.x - offset_x) * scale_x),
                int((event.y - offset_y) * scale_y),
            )

            if self.enable_homography.get():
                if len(self.src_points) < 4:
                    self.src_points.append(point)
                    self.save_settings()
                else:
                    for i, src_point in enumerate(self.src_points):
                        if self.is_close(point, src_point):
                            self.dragging_point = i
                            break
            if self.enable_crop.get():
                for i, crop_point in enumerate(self.crop_points):
                    if self.is_close(point, crop_point):
                        self.dragging_point = i + 4
                        break
            self.update_frame_display(self.current_frame, draw_points=True)

    def on_mouse_drag(self, event):
        """Handle mouse drag to move points for homography and crop."""
        widget = event.widget
        if self.dragging_point is not None and widget == self.frm_video:
            widget_width = widget.winfo_width()
            widget_height = widget.winfo_height()
            image_width, image_height = (
                self.current_frame.shape[1],
                self.current_frame.shape[0],
            )

            scale_x = image_width / widget_width
            scale_y = image_height / widget_height
            offset_x = (widget_width - image_width / scale_x) / 2
            offset_y = (widget_height - image_height / scale_y) / 2

            point = (
                int((event.x - offset_x) * scale_x),
                int((event.y - offset_y) * scale_y),
            )

            point = (
                max(0, min(point[0], image_width - 1)),
                max(0, min(point[1], image_height - 1)),
            )

            if self.dragging_point < 4:
                self.src_points[self.dragging_point] = point
            else:
                self.crop_points[self.dragging_point - 4] = point

            current_time = time.time()
            if current_time - getattr(self, "_last_update_time", 0) > 0.1:
                self.update_frame_display(self.current_frame, draw_points=True)
                self._last_update_time = current_time

    def on_mouse_release(self, event):
        """Handle mouse release to stop dragging points for homography and
        crop."""
        self.dragging_point = None
        self.update_frame_display(self.current_frame, draw_points=True)
        self.save_settings()
        asyncio.create_task(self.apply_transformations())

    def update_frame_display(self, frame, draw_points=False):
        """Update the displayed frame with optional points drawing."""
        frame_copy = frame.copy()
        if draw_points:
            for i, point in enumerate(self.src_points):
                cv2.circle(frame_copy, point, 5, (0, 255, 0), -1)
                if i > 0:
                    cv2.line(
                        frame_copy,
                        self.src_points[i - 1],
                        point,
                        (0, 255, 0),
                        2,
                    )
            if len(self.src_points) == 4:
                cv2.line(
                    frame_copy,
                    self.src_points[0],
                    self.src_points[3],
                    (0, 255, 0),
                    2,
                )

            if self.enable_crop.get():
                if len(self.crop_points) == 4:
                    for i, point in enumerate(self.crop_points):
                        cv2.circle(frame_copy, point, 5, (255, 0, 0), -1)
                        if i > 0:
                            cv2.line(
                                frame_copy,
                                self.crop_points[i - 1],
                                point,
                                (255, 0, 0),
                                2,
                            )
                    cv2.line(
                        frame_copy,
                        self.crop_points[0],
                        self.crop_points[3],
                        (255, 0, 0),
                        2,
                    )

        image = Image.fromarray(frame_copy)
        image = ImageTk.PhotoImage(image)
        self.frm_video.configure(image=image)
        self.frm_video.image = image
        self.frm_video.pack_propagate(False)
        self.frm_video.config(width=image.width())

    def is_close(self, point1, point2, threshold=10):
        """Check if two points are within a certain threshold distance."""
        return np.linalg.norm(np.array(point1) - np.array(point2)) < threshold

    def perform_homography(self, frame):
        """Perform homography transform and update the transformed image."""
        if len(self.src_points) == 4:
            if (
                not self.homography_width.get()
                or not self.homography_height.get()
            ):
                logging.error("Width and height must be set.")
                return frame

            try:
                target_width = float(self.homography_width.get())
                target_height = float(self.homography_height.get())
            except ValueError:
                logging.error("Width and height must be valid numbers.")
                return frame

            src_points = self.sort_points_clockwise(self.src_points)
            src = np.array(src_points, dtype=np.float32)
            dst = np.array(
                [
                    [0, 0],
                    [target_width, 0],
                    [target_width, target_height],
                    [0, target_height],
                ],
                dtype=np.float32,
            )

            h, status = cv2.findHomography(src, dst)

            transformed_frame = cv2.warpPerspective(
                frame, h, (int(target_width), int(target_height))
            )
            self.transformed_crop_points = cv2.perspectiveTransform(
                np.array([self.crop_points], dtype=np.float32), h
            )[0]

            return transformed_frame
        return frame

    def perform_crop(self, frame):
        """Perform cropping based on crop points and update the transformed
        image."""
        if (
            self.enable_homography.get()
            and hasattr(self, "transformed_crop_points")
            and len(self.transformed_crop_points) == 4
        ):
            crop_points = np.array(
                self.transformed_crop_points, dtype=np.float32
            )
        else:
            crop_points = np.array(self.crop_points, dtype=np.float32)

        crop_points[:, 0] = np.clip(crop_points[:, 0], 0, frame.shape[1] - 1)
        crop_points[:, 1] = np.clip(crop_points[:, 1], 0, frame.shape[0] - 1)

        rect = cv2.boundingRect(crop_points)
        x, y, w, h = rect
        cropped = frame[y: y + h, x: x + w].copy()

        crop_points = crop_points - crop_points.min(axis=0)
        mask = np.zeros(cropped.shape[:2], dtype=np.uint8)
        cv2.drawContours(
            mask,
            [crop_points.astype(np.int32)],
            -1,
            (255, 255, 255),
            -1,
            cv2.LINE_AA,
        )

        result = cv2.bitwise_and(cropped, cropped, mask=mask)

        return result

    def resize_to_original_frame(self, frame, original_width, original_height):
        """Resize the frame to fit within the original frame dimensions,
        maintaining aspect ratio."""
        result_height, result_width = frame.shape[:2]

        scale_x = original_width / result_width
        scale_y = original_height / result_height
        scale = min(scale_x, scale_y)

        result_resized = cv2.resize(
            frame,
            (int(result_width * scale), int(result_height * scale)),
            interpolation=cv2.INTER_LINEAR,
        )

        final_frame = np.zeros(
            (original_height, original_width, 3), dtype=np.uint8
        )
        offset_x = (original_width - result_resized.shape[1]) // 2
        offset_y = (original_height - result_resized.shape[0]) // 2

        final_frame[
            offset_y: offset_y + result_resized.shape[0],
            offset_x: offset_x + result_resized.shape[1],
        ] = result_resized

        return final_frame

    def update_transformed_display(self, frame):
        """Update the transformed frame displayed in the UI."""
        image = Image.fromarray(frame)
        image = ImageTk.PhotoImage(image)
        self.frm_transformed.configure(image=image)
        self.frm_transformed.image = image

    def sort_points_clockwise(self, pts):
        """Sort points in a clockwise order."""
        center = np.mean(pts, axis=0)

        def angle_from_center(pt):
            return np.arctan2(pt[1] - center[1], pt[0] - center[0])

        sorted_pts = sorted(pts, key=angle_from_center)
        return sorted_pts

    async def apply_transformations(self):
        """Apply homography and crop transformations,
        then update the display."""
        if self.current_frame is None:
            return

        temp_frame = self.current_frame.copy()

        original_width, original_height = (
            self.current_frame.shape[1],
            self.current_frame.shape[0],
        )

        if self.enable_homography.get() and len(self.src_points) == 4:
            temp_frame = self.perform_homography(temp_frame)

        if self.enable_crop.get() and len(self.crop_points) == 4:
            temp_frame = self.perform_crop(temp_frame)

        temp_frame = self.resize_to_original_frame(
            temp_frame, original_width, original_height
        )

        self.update_transformed_display(temp_frame)

    async def update_frames(self):
        """Update the frame displayed in the UI."""
        while not self.stop_event.is_set():
            try:
                if not self.frame_queue.empty():
                    frame, scaling_factor = self.frame_queue.get()
                    self.current_frame = frame.copy()
                    self.scaling_factor = scaling_factor
                    self.update_frame_display(frame, draw_points=True)

                await asyncio.sleep(0.033)  # Approx 30 FPS
            except Exception as e:
                logging.error(f"Error updating frame: {e}")
                await asyncio.sleep(1)
