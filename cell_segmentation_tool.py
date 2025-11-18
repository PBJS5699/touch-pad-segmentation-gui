"""
Cell Segmentation Tool
A manual cell segmentation application with Apple Pencil support.

Features:
- Drag-and-drop or file dialog to load TIFF images
- Draw polygon masks with left click + drag
- Delete masks with CMD/CTRL + click
- Auto-save masks after each change
- Zoom/pan controls
- Undo functionality
"""

import sys
import os
from pathlib import Path
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QComboBox, QSlider, QMessageBox)
from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QPolygonF
from skimage import io
from skimage.measure import label
from scipy.ndimage import binary_fill_holes
import cv2


class ImageCanvas(QWidget):
    """Canvas widget for displaying image and drawing segmentation masks."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # Image data
        self.image = None  # Original image (grayscale or RGB)
        self.image_path = None
        self.masks = None  # Labeled array with unique IDs for each mask
        
        # Drawing state
        self.current_polygon = []  # Points being drawn for current mask
        self.is_drawing = False
        self.is_panning = False
        self.is_ctrl_dragging = False  # CTRL key for zoom/pan
        self.is_cmd_pressed = False  # CMD key for delete
        self.space_pressed = False  # Track if space bar is held down
        
        # View transform (for zoom/pan)
        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1.0
        self.last_mouse_pos = None
        
        # Mask display settings
        self.mask_alpha = 0.4  # Transparency of mask overlays
        self.next_mask_id = 1  # Next available mask ID
        
        # Enable mouse tracking and drag-and-drop
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Minimum size for the canvas
        self.setMinimumSize(800, 600)
    
    def load_image(self, filepath):
        """Load TIFF image and associated mask file if it exists."""
        try:
            # Load TIFF image using skimage
            img = io.imread(filepath)
            
            # Store original path
            self.image_path = filepath
            
            # Build list of TIFF files in the same directory for navigation
            self.parent_window.build_file_list(filepath)
            
            # Store original image data in parent window for channel switching
            self.parent_window.original_image_data = img
            
            # Handle multi-channel images
            if len(img.shape) == 3 and img.shape[2] > 3:
                # Multi-channel image - use first channel by default
                self.image = img[:, :, 0]
                self.parent_window.update_channel_selector(img.shape[2])
            elif len(img.shape) == 3:
                # RGB image
                self.image = img
            else:
                # Grayscale image
                self.image = img
            
            # Initialize masks array (same size as image, all zeros)
            self.masks = np.zeros(self.image.shape[:2], dtype=np.int32)
            
            # Try to load existing masks
            mask_path = self._get_mask_path(filepath)
            if os.path.exists(mask_path):
                try:
                    loaded_masks = np.load(mask_path, allow_pickle=True)
                    
                    # Handle different mask file formats
                    # CellPose format: numpy array containing a dictionary
                    if loaded_masks.ndim == 0 and loaded_masks.dtype == object:
                        # This is a 0-d object array, extract the dict
                        masks_dict = loaded_masks.item()
                        if isinstance(masks_dict, dict) and 'masks' in masks_dict:
                            loaded_masks = masks_dict['masks']
                            print(f"Loaded CellPose format masks from {mask_path}")
                    
                    # Simple array format: direct array
                    if isinstance(loaded_masks, np.ndarray) and loaded_masks.ndim >= 2:
                        if loaded_masks.shape[:2] == self.masks.shape:
                            self.masks = loaded_masks.astype(np.int32)
                            # Update next_mask_id to be one more than the max existing ID
                            if self.masks.max() > 0:
                                self.next_mask_id = int(self.masks.max()) + 1
                            print(f"Loaded {len(np.unique(self.masks)) - 1} masks from {mask_path}")
                        else:
                            print(f"Warning: Mask shape {loaded_masks.shape} doesn't match image shape {self.masks.shape}")
                except Exception as e:
                    print(f"Warning: Could not load masks from {mask_path}: {str(e)}")
            
            # Reset view transform
            self.offset_x = 0
            self.offset_y = 0
            self.scale = 1.0
            
            # Clear drawing state
            self.current_polygon = []
            self.is_drawing = False
            
            self.update()
            self.parent_window.update_status()
            
            # Update filename label in parent window
            self.parent_window.update_filename(filepath)
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
            return False
    
    def _get_mask_path(self, image_path):
        """Generate the mask file path from the image path."""
        path = Path(image_path)
        mask_filename = path.stem + "_seg.npy"
        return str(path.parent / mask_filename)
    
    def save_masks(self):
        """Save masks to .npy file in CellPose-compatible format, or delete if empty."""
        if self.image_path is None or self.masks is None:
            return
        
        try:
            mask_path = self._get_mask_path(self.image_path)
            num_masks = len(np.unique(self.masks)) - 1  # Exclude background
            
            if num_masks > 0:
                # Generate outlines for CellPose
                outlines = self._generate_outlines()
                
                # Generate colors for each mask
                colors = self._generate_colors()
                
                # Save masks in CellPose format (dictionary wrapped in 0-d array)
                # This ensures compatibility with CellPose GUI
                cellpose_data = {
                    'outlines': outlines,
                    'colors': colors,
                    'masks': self.masks.astype(np.uint16),
                    'filename': self.image_path,
                    'flows': [],
                    'ismanual': np.array([True]),
                    'manual_changes': [],
                    'model_path': 0,
                    'flow_threshold': 0.4,
                    'cellprob_threshold': 0.0,
                    'normalize_params': {
                        'lowhigh': None,
                        'percentile': [1.0, 99.0],
                        'normalize': True,
                        'norm3D': True,
                        'sharpen_radius': 0.0,
                        'smooth_radius': 0.0,
                        'tile_norm_blocksize': 0.0,
                        'tile_norm_smooth3D': 0.0,
                        'invert': False
                    },
                    'restore': None,
                    'ratio': 1.0,
                    'diameter': None
                }
                
                # Save as 0-dimensional object array (CellPose format)
                np.save(mask_path, np.array(cellpose_data, dtype=object))
                print(f"Saved {num_masks} masks to {mask_path} (CellPose format)")
            else:
                # Delete the .npy file if it exists and there are no masks
                if os.path.exists(mask_path):
                    os.remove(mask_path)
                    print(f"Deleted empty mask file: {mask_path}")
                else:
                    print(f"No masks to save")
        except Exception as e:
            print(f"Failed to save masks: {str(e)}")
    
    def set_channel(self, channel_idx, img_data):
        """Update displayed channel for multi-channel images."""
        if channel_idx < img_data.shape[2]:
            self.image = img_data[:, :, channel_idx]
            self.update()
    
    def screen_to_image_coords(self, screen_x, screen_y):
        """Convert screen coordinates to image coordinates."""
        img_x = (screen_x - self.offset_x) / self.scale
        img_y = (screen_y - self.offset_y) / self.scale
        return int(img_x), int(img_y)
    
    def image_to_screen_coords(self, img_x, img_y):
        """Convert image coordinates to screen coordinates."""
        screen_x = img_x * self.scale + self.offset_x
        screen_y = img_y * self.scale + self.offset_y
        return screen_x, screen_y
    
    def paintEvent(self, event):
        """Render the image, masks, and current polygon."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)
        
        if self.image is None:
            # Display instructions when no image is loaded
            painter.setPen(QColor(200, 200, 200))
            painter.drawText(self.rect(), Qt.AlignCenter, 
                           "Drag and drop a TIFF file here\nor use File > Open")
            return
        
        # Convert numpy image to QImage for display
        qimage = self._numpy_to_qimage(self.image)
        
        # Apply transform (scale and offset)
        painter.translate(self.offset_x, self.offset_y)
        painter.scale(self.scale, self.scale)
        
        # Draw image
        painter.drawImage(0, 0, qimage)
        
        # Draw existing masks with colored overlays
        if self.masks is not None and self.masks.max() > 0:
            mask_overlay = self._create_mask_overlay()
            painter.setOpacity(self.mask_alpha)
            painter.drawImage(0, 0, mask_overlay)
            painter.setOpacity(1.0)
        
        # Draw current polygon being drawn (in bright yellow)
        if len(self.current_polygon) > 0:
            painter.setPen(QPen(QColor(255, 255, 0), 2.0 / self.scale))
            qpolygon = QPolygonF([QPointF(x, y) for x, y in self.current_polygon])
            painter.drawPolyline(qpolygon)
            
            # Draw small circles at each point for visibility
            for x, y in self.current_polygon:
                painter.drawEllipse(QPointF(x, y), 3.0 / self.scale, 3.0 / self.scale)
    
    def _numpy_to_qimage(self, img):
        """Convert numpy array to QImage."""
        # Normalize to 8-bit if necessary
        if img.dtype != np.uint8:
            img_min, img_max = img.min(), img.max()
            if img_max > img_min:
                img = ((img - img_min) / (img_max - img_min) * 255).astype(np.uint8)
            else:
                img = np.zeros_like(img, dtype=np.uint8)
        
        # Handle grayscale vs RGB
        if len(img.shape) == 2:
            height, width = img.shape
            bytes_per_line = width
            return QImage(img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        elif len(img.shape) == 3 and img.shape[2] == 3:
            height, width, _ = img.shape
            bytes_per_line = 3 * width
            return QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        else:
            # Fallback to grayscale
            return self._numpy_to_qimage(img[:, :, 0] if len(img.shape) == 3 else img)
    
    def _create_mask_overlay(self):
        """Create a colored overlay image showing all masks."""
        height, width = self.masks.shape
        overlay = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Generate unique colors for each mask ID
        unique_ids = np.unique(self.masks)
        unique_ids = unique_ids[unique_ids > 0]  # Exclude background (0)
        
        for mask_id in unique_ids:
            # Generate consistent color from mask ID using HSV
            hue = (mask_id * 137) % 180  # Golden angle for color distribution
            color = cv2.cvtColor(np.uint8([[[hue, 255, 255]]]), cv2.COLOR_HSV2RGB)[0, 0]
            
            # Apply color to mask region
            mask_region = (self.masks == mask_id)
            overlay[mask_region, 0] = color[0]
            overlay[mask_region, 1] = color[1]
            overlay[mask_region, 2] = color[2]
            overlay[mask_region, 3] = 255  # Full opacity in overlay, will be blended
        
        # Convert to QImage
        bytes_per_line = 4 * width
        return QImage(overlay.data, width, height, bytes_per_line, QImage.Format_RGBA8888)
    
    def mousePressEvent(self, event):
        """Handle mouse button press."""
        if self.image is None:
            return
        
        # Get image coordinates
        img_x, img_y = self.screen_to_image_coords(event.x(), event.y())
        
        # Check for SPACE + drag (pan) - highest priority when space is held
        if event.button() == Qt.LeftButton and self.space_pressed:
            self.is_panning = True
            self.last_mouse_pos = event.pos()
            return
        
        # Check for CMD (Meta) or CTRL + click/drag for delete
        # On Mac, CMD is MetaModifier; on Windows/Linux, use ControlModifier
        if event.button() == Qt.LeftButton and (event.modifiers() & (Qt.MetaModifier | Qt.ControlModifier)):
            self.is_cmd_pressed = True
            self.last_mouse_pos = event.pos()
            print(f"Delete mode activated at ({img_x}, {img_y})")
            return
        
        # Start drawing polygon
        if event.button() == Qt.LeftButton:
            self.is_drawing = True
            self.current_polygon = [(img_x, img_y)]
            self.update()
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement."""
        if self.image is None:
            return
        
        # Handle CMD + drag (track movement for delete)
        # This allows both click and drag to delete
        if self.is_cmd_pressed and self.last_mouse_pos is not None:
            # Just track movement - delete happens on mouse release or during drag
            return
        
        # Handle panning
        if self.is_panning and self.last_mouse_pos is not None:
            delta = event.pos() - self.last_mouse_pos
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.last_mouse_pos = event.pos()
            self.update()
            return
        
        # Continue drawing polygon
        if self.is_drawing:
            img_x, img_y = self.screen_to_image_coords(event.x(), event.y())
            
            # Add point if it's far enough from the last point
            if len(self.current_polygon) == 0 or \
               np.sqrt((img_x - self.current_polygon[-1][0])**2 + 
                      (img_y - self.current_polygon[-1][1])**2) > 2:
                self.current_polygon.append((img_x, img_y))
                self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse button release."""
        if self.image is None:
            return
        
        # Get image coordinates for delete check
        img_x, img_y = self.screen_to_image_coords(event.x(), event.y())
        
        # Handle CMD/CTRL + click/drag for delete
        if self.is_cmd_pressed and self.last_mouse_pos is not None:
            # Delete mask at release position (works for both click and drag)
            print(f"Attempting to delete mask at ({img_x}, {img_y})")
            self._delete_mask_at(img_x, img_y)
            
            # Reset state
            self.is_cmd_pressed = False
            self.last_mouse_pos = None
            return
        
        # Finalize panning
        if self.is_panning:
            self.is_panning = False
            self.last_mouse_pos = None
            return
        
        # Finalize polygon drawing
        if self.is_drawing and event.button() == Qt.LeftButton:
            self.is_drawing = False
            
            # Only create mask if we have enough points
            if len(self.current_polygon) >= 3:
                self._create_mask_from_polygon()
                self.save_masks()  # Auto-save
                self.parent_window.update_status()
            
            self.current_polygon = []
            self.update()
    
    def _create_mask_from_polygon(self):
        """Create a new mask from the current polygon, avoiding overlap with existing masks."""
        if len(self.current_polygon) < 3:
            return
        
        # Create a binary mask from the polygon
        height, width = self.masks.shape
        polygon_array = np.array(self.current_polygon, dtype=np.int32)
        
        # Create empty mask
        new_mask = np.zeros((height, width), dtype=np.uint8)
        
        # Fill polygon using OpenCV
        cv2.fillPoly(new_mask, [polygon_array], 1)
        
        # Remove pixels that already belong to existing masks
        # This ensures new masks go "behind" existing masks and don't overlap
        existing_mask_pixels = (self.masks > 0)
        new_mask[existing_mask_pixels] = 0
        
        # Only add the mask if there are pixels left after removing overlaps
        if np.sum(new_mask) > 0:
            # Add to masks with unique ID
            self.masks[new_mask == 1] = self.next_mask_id
            self.next_mask_id += 1
            
            # Add to undo stack
            self.parent_window.add_to_undo_stack()
            print(f"Created mask {self.next_mask_id - 1} with {np.sum(new_mask)} pixels (overlaps removed)")
        else:
            print("New mask completely overlaps existing masks - not created")
    
    def _generate_outlines(self):
        """Generate outline array for CellPose format (boundaries of masks)."""
        # Create outline array (same shape as masks)
        outlines = np.zeros_like(self.masks, dtype=np.uint16)
        
        # For each mask, find its boundary pixels
        unique_ids = np.unique(self.masks)
        unique_ids = unique_ids[unique_ids > 0]  # Exclude background
        
        for mask_id in unique_ids:
            # Get binary mask for this ID
            binary_mask = (self.masks == mask_id).astype(np.uint8)
            
            # Find contours (boundaries)
            contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            
            # Draw outlines
            cv2.drawContours(outlines, contours, -1, int(mask_id), 1)
        
        return outlines
    
    def _generate_colors(self):
        """Generate color array for CellPose format (RGB colors for each mask)."""
        unique_ids = np.unique(self.masks)
        unique_ids = unique_ids[unique_ids > 0]  # Exclude background
        
        if len(unique_ids) == 0:
            return np.array([[0, 0, 0]], dtype=np.int64)
        
        # Generate colors for each mask (same HSV scheme as display)
        colors = []
        for mask_id in unique_ids:
            hue = (mask_id * 137) % 180
            color = cv2.cvtColor(np.uint8([[[hue, 255, 255]]]), cv2.COLOR_HSV2RGB)[0, 0]
            colors.append([int(color[0]), int(color[1]), int(color[2])])
        
        return np.array(colors, dtype=np.int64)
    
    def _delete_mask_at(self, img_x, img_y):
        """Delete the mask at the given image coordinates."""
        if self.masks is None:
            print("No masks loaded")
            return
        
        # Check bounds
        height, width = self.masks.shape
        if 0 <= img_x < width and 0 <= img_y < height:
            mask_id = self.masks[img_y, img_x]
            print(f"Mask ID at ({img_x}, {img_y}): {mask_id}")
            
            if mask_id > 0:
                # Add to undo stack before deletion
                self.parent_window.add_to_undo_stack()
                
                # Remove this mask
                self.masks[self.masks == mask_id] = 0
                print(f"Deleted mask {mask_id}")
                self.save_masks()  # Auto-save
                self.parent_window.update_status()
                self.update()
            else:
                print("No mask at this location")
        else:
            print(f"Coordinates out of bounds: ({img_x}, {img_y})")
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        if self.image is None:
            return
        
        # Zoom in/out with mouse wheel
        zoom_factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        old_scale = self.scale
        self.scale *= zoom_factor
        self.scale = max(0.1, min(10.0, self.scale))  # Clamp zoom
        
        # Adjust offset to zoom towards mouse position
        mouse_x = event.x()
        mouse_y = event.y()
        self.offset_x = mouse_x - (mouse_x - self.offset_x) * (self.scale / old_scale)
        self.offset_y = mouse_y - (mouse_y - self.offset_y) * (self.scale / old_scale)
        
        self.update()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Track space bar for panning
        if event.key() == Qt.Key_Space:
            self.space_pressed = True
            self.setCursor(Qt.OpenHandCursor)
        
        # Navigate to previous file with Left Arrow
        elif event.key() == Qt.Key_Left:
            print("Left arrow pressed in canvas")
            self.parent_window.load_previous_file()
        
        # Navigate to next file with Right Arrow
        elif event.key() == Qt.Key_Right:
            print("Right arrow pressed in canvas")
            self.parent_window.load_next_file()
        
        # Zoom in with + or =
        elif event.key() in (Qt.Key_Plus, Qt.Key_Equal):
            if self.image is not None:
                # Zoom towards center of view
                center_x = self.width() / 2
                center_y = self.height() / 2
                old_scale = self.scale
                self.scale *= 1.1
                self.scale = max(0.1, min(10.0, self.scale))
                # Adjust offset to zoom towards center
                self.offset_x = center_x - (center_x - self.offset_x) * (self.scale / old_scale)
                self.offset_y = center_y - (center_y - self.offset_y) * (self.scale / old_scale)
                self.update()
        
        # Zoom out with - or _
        elif event.key() in (Qt.Key_Minus, Qt.Key_Underscore):
            if self.image is not None:
                # Zoom towards center of view
                center_x = self.width() / 2
                center_y = self.height() / 2
                old_scale = self.scale
                self.scale *= 0.9
                self.scale = max(0.1, min(10.0, self.scale))
                # Adjust offset to zoom towards center
                self.offset_x = center_x - (center_x - self.offset_x) * (self.scale / old_scale)
                self.offset_y = center_y - (center_y - self.offset_y) * (self.scale / old_scale)
                self.update()
    
    def keyReleaseEvent(self, event):
        """Handle key release events."""
        # Release space bar
        if event.key() == Qt.Key_Space:
            self.space_pressed = False
            self.setCursor(Qt.ArrowCursor)
    
    def dragEnterEvent(self, event):
        """Handle drag enter event for drag-and-drop."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Handle drop event for drag-and-drop."""
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            filepath = url.toLocalFile()
            
            # Check if it's a TIFF file
            if filepath.lower().endswith(('.tif', '.tiff')):
                # Save current masks before switching images
                if self.masks is not None and self.image_path is not None:
                    self.save_masks()
                
                # Load new image
                self.load_image(filepath)
                event.acceptProposedAction()


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Undo stack (stores previous mask states)
        self.undo_stack = []
        self.max_undo_steps = 50
        
        # Original multi-channel image data (for channel switching)
        self.original_image_data = None
        
        # File navigation
        self.tiff_files = []  # List of TIFF files in current directory
        self.current_file_index = -1  # Index of currently loaded file
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Cell Segmentation Tool")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Top bar with filename and controls
        top_bar = QHBoxLayout()
        
        # Filename label
        self.filename_label = QLabel("No image loaded")
        self.filename_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        top_bar.addWidget(self.filename_label)
        
        top_bar.addStretch()
        
        # Channel selector (for multi-channel images)
        self.channel_label = QLabel("Channel:")
        self.channel_selector = QComboBox()
        self.channel_selector.currentIndexChanged.connect(self.on_channel_changed)
        self.channel_selector.setVisible(False)
        self.channel_label.setVisible(False)
        top_bar.addWidget(self.channel_label)
        top_bar.addWidget(self.channel_selector)
        
        # Open button
        open_btn = QPushButton("Open Image")
        open_btn.clicked.connect(self.open_image_dialog)
        top_bar.addWidget(open_btn)
        
        main_layout.addLayout(top_bar)
        
        # Canvas for image display
        self.canvas = ImageCanvas(self)
        main_layout.addWidget(self.canvas)
        
        # Bottom bar with status info
        bottom_bar = QHBoxLayout()
        
        self.status_label = QLabel("Mask Count: 0")
        self.status_label.setStyleSheet("font-size: 12px;")
        bottom_bar.addWidget(self.status_label)
        
        bottom_bar.addStretch()
        
        # Mask opacity slider
        opacity_label = QLabel("Mask Opacity:")
        bottom_bar.addWidget(opacity_label)
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(40)
        self.opacity_slider.setMaximumWidth(150)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        bottom_bar.addWidget(self.opacity_slider)
        
        # Undo button
        undo_btn = QPushButton("Undo (Cmd+Z)")
        undo_btn.clicked.connect(self.undo)
        bottom_bar.addWidget(undo_btn)
        
        main_layout.addLayout(bottom_bar)
        
        # Instructions
        instructions = QLabel(
            "Left Click+Drag=Draw | Cmd+Click=Delete | +/-=Zoom | ←/→=Prev/Next File | Space+Drag=Pan"
        )
        instructions.setStyleSheet("font-size: 8px; color: gray;")
        instructions.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(instructions)
    
    def open_image_dialog(self):
        """Open file dialog to select a TIFF image."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open TIFF Image", "", 
            "TIFF Images (*.tif *.tiff);;All Files (*)"
        )
        
        if filepath:
            # Save current masks before switching images
            if self.canvas.masks is not None and self.canvas.image_path is not None:
                self.canvas.save_masks()
            
            # Load the full image data
            try:
                img = io.imread(filepath)
                self.original_image_data = img
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
                return
            
            # Load into canvas (canvas will update filename)
            self.canvas.load_image(filepath)
            
            # Clear undo stack
            self.undo_stack = []
    
    def update_filename(self, filepath):
        """Update the filename label with the loaded image name."""
        self.filename_label.setText(os.path.basename(filepath))
    
    def update_channel_selector(self, num_channels):
        """Update channel selector for multi-channel images."""
        if num_channels > 1:
            self.channel_selector.clear()
            for i in range(num_channels):
                self.channel_selector.addItem(f"Channel {i+1}")
            self.channel_selector.setVisible(True)
            self.channel_label.setVisible(True)
        else:
            self.channel_selector.setVisible(False)
            self.channel_label.setVisible(False)
    
    def on_channel_changed(self, index):
        """Handle channel selection change."""
        if self.original_image_data is not None and len(self.original_image_data.shape) == 3:
            self.canvas.set_channel(index, self.original_image_data)
    
    def on_opacity_changed(self, value):
        """Handle mask opacity slider change."""
        self.canvas.mask_alpha = value / 100.0
        self.canvas.update()
    
    def update_status(self):
        """Update status label with current mask count."""
        if self.canvas.masks is not None:
            mask_count = len(np.unique(self.canvas.masks)) - 1  # Exclude background
            self.status_label.setText(f"Mask Count: {mask_count}")
    
    def add_to_undo_stack(self):
        """Add current mask state to undo stack."""
        if self.canvas.masks is not None:
            # Store a copy of the current masks
            self.undo_stack.append(self.canvas.masks.copy())
            
            # Limit undo stack size
            if len(self.undo_stack) > self.max_undo_steps:
                self.undo_stack.pop(0)
    
    def undo(self):
        """Undo the last mask change."""
        if len(self.undo_stack) > 0:
            # Restore previous state
            self.canvas.masks = self.undo_stack.pop()
            self.canvas.save_masks()
            self.canvas.update()
            self.update_status()
    
    def build_file_list(self, current_filepath):
        """Build a list of TIFF files in the same directory as the current file."""
        from pathlib import Path
        
        current_path = Path(current_filepath)
        directory = current_path.parent
        
        # Find all TIFF files in the directory
        tiff_extensions = ['.tif', '.tiff', '.TIF', '.TIFF']
        self.tiff_files = []
        
        for ext in tiff_extensions:
            self.tiff_files.extend(directory.glob(f'*{ext}'))
        
        # Sort files alphabetically
        self.tiff_files = sorted(self.tiff_files)
        
        # Find current file index
        try:
            self.current_file_index = self.tiff_files.index(current_path)
        except ValueError:
            self.current_file_index = -1
        
        print(f"Found {len(self.tiff_files)} TIFF files in directory")
        if self.current_file_index >= 0:
            print(f"Current file: {self.current_file_index + 1}/{len(self.tiff_files)}")
    
    def load_previous_file(self):
        """Load the previous TIFF file in the directory."""
        if len(self.tiff_files) == 0:
            print("No file list available")
            return
        
        if self.current_file_index <= 0:
            print("Already at first file")
            return
        
        # Save current masks
        if self.canvas.masks is not None and self.canvas.image_path is not None:
            self.canvas.save_masks()
        
        # Load previous file
        self.current_file_index -= 1
        next_file = str(self.tiff_files[self.current_file_index])
        print(f"Loading previous file: {self.current_file_index + 1}/{len(self.tiff_files)}")
        
        # Load the image
        try:
            img = io.imread(next_file)
            self.original_image_data = img
            self.canvas.load_image(next_file)
            self.undo_stack = []
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def load_next_file(self):
        """Load the next TIFF file in the directory."""
        if len(self.tiff_files) == 0:
            print("No file list available")
            return
        
        if self.current_file_index >= len(self.tiff_files) - 1:
            print("Already at last file")
            return
        
        # Save current masks
        if self.canvas.masks is not None and self.canvas.image_path is not None:
            self.canvas.save_masks()
        
        # Load next file
        self.current_file_index += 1
        next_file = str(self.tiff_files[self.current_file_index])
        print(f"Loading next file: {self.current_file_index + 1}/{len(self.tiff_files)}")
        
        # Load the image
        try:
            img = io.imread(next_file)
            self.original_image_data = img
            self.canvas.load_image(next_file)
            self.undo_stack = []
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        # Undo with Cmd+Z or Ctrl+Z
        if event.key() == Qt.Key_Z and (event.modifiers() & (Qt.ControlModifier | Qt.MetaModifier)):
            self.undo()
        
        # Navigate to previous file with Left Arrow
        elif event.key() == Qt.Key_Left:
            self.load_previous_file()
        
        # Navigate to next file with Right Arrow
        elif event.key() == Qt.Key_Right:
            self.load_next_file()


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

