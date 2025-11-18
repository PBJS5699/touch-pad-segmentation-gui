# Setup Instructions

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python cell_segmentation_tool.py
```

### 3. Try the Example

Drag the example file onto the canvas:
```
example-io/20250805_UTX265_midplane_1_MMStack_Pos0_GP30003.tif
```

This will also load the existing masks from:
```
example-io/20250805_UTX265_midplane_1_MMStack_Pos0_GP30003_seg.npy
```

## Dependencies

The tool requires the following Python packages:

- **numpy** - Array operations for mask storage
- **PyQt5** - GUI framework with drag-and-drop support
- **scikit-image** - TIFF image loading
- **opencv-python** - Polygon filling and image processing
- **scipy** - Binary operations on masks
- **pillow** - Additional image format support

## Troubleshooting

### Module Not Found Error

If you see `ModuleNotFoundError`, install the dependencies:

```bash
pip install numpy PyQt5 scikit-image opencv-python scipy pillow
```

### macOS Permissions

On macOS, you may need to grant permissions for the application to access files. When prompted, allow file access.

### Apple Pencil Setup

1. Connect your iPad to your Mac
2. Enable Sidecar: System Preferences > Displays > Add Display
3. Use your iPad as a second display
4. Move the application window to the iPad display
5. Draw with Apple Pencil!

### Display Issues

If masks don't display properly, try adjusting the mask opacity slider at the bottom of the window.

## Virtual Environment (Recommended)

For cleaner dependency management:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python cell_segmentation_tool.py
```


