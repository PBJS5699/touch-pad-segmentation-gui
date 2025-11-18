# Cell Segmentation Tool

A manual cell segmentation application with Apple Pencil support for drawing precise polygon masks on TIFF images.

## 📁 Project Files

- **cell_segmentation_tool.py** - Main application
- **mask_utils.py** - Utility functions for mask analysis and conversion
- **requirements.txt** - Python dependencies
- **run.sh / run.bat** - Launcher scripts
- **README.md** - This file
- **SETUP.md** - Installation instructions
- **USAGE_GUIDE.md** - Comprehensive usage manual
- **QUICK_REFERENCE.md** - Quick reference card
- **example-io/** - Example TIFF image and mask files

## Features

- **Drag-and-drop** TIFF file loading
- **Draw polygon masks** with left click + drag (Apple Pencil compatible)
- **Delete masks** with CMD/CTRL + click
- **Auto-save** masks after each change
- **Multi-channel TIFF support** with channel selector
- **Zoom and pan** controls
- **Undo functionality** (CMD+Z)
- **Colored mask overlays** with adjustable transparency

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python cell_segmentation_tool.py
```

### Controls

| Action | Control |
|--------|---------|
| **Draw mask** | Left Click + Drag |
| **Delete mask** | CMD/CTRL + Click on mask |
| **Zoom in/out** | Mouse Wheel or CTRL + Vertical Drag |
| **Pan image** | Space + Drag or CTRL + Horizontal Drag |
| **Undo** | CMD+Z (Mac) or CTRL+Z (Windows/Linux) |
| **Open image** | Drag TIFF onto canvas or use "Open Image" button |

### Workflow

1. **Load Image**: Drag a TIFF file onto the canvas or click "Open Image"
2. **Draw Masks**: 
   - Click and hold left mouse button
   - Drag to trace cell boundary
   - Release to complete the polygon (auto-closes)
   - Mask is automatically saved
3. **Delete Masks**: Hold CMD/CTRL and click on any mask
4. **Adjust View**: Use mouse wheel to zoom, space+drag to pan
5. **Multi-channel Images**: Use the channel selector dropdown to switch between channels

### File Naming Convention

The tool automatically generates mask files with the following naming:

- **Input**: `{filename}.tif`
- **Output**: `{filename}_seg.npy`

**Example**:
- Input: `20250805_UTX265_midplane_1_MMStack_Pos0_GP30003.tif`
- Output: `20250805_UTX265_midplane_1_MMStack_Pos0_GP30003_seg.npy`

### Auto-Save Behavior

- Masks are automatically saved after each new mask is drawn
- Masks are automatically saved after deletion
- Existing `_seg.npy` files are automatically loaded when opening an image

### Mask Data Format

Masks are stored as a labeled numpy array where:
- Background = 0
- Each mask has a unique integer ID (1, 2, 3, ...)
- Array shape matches the image dimensions

## Apple Pencil Support

The tool works seamlessly with Apple Pencil on Mac via Sidecar:

1. Connect your iPad to your Mac using Sidecar
2. Launch the application
3. Use Apple Pencil to draw precise polygon masks
4. Left click + drag works natively with Apple Pencil touch

## Utility Functions

The included `mask_utils.py` provides command-line tools for working with mask files:

### Inspect Masks
```bash
python mask_utils.py inspect image_seg.npy
```

### Export to PNG (for visualization)
```bash
python mask_utils.py export image_seg.npy
```

### Calculate Statistics
```bash
python mask_utils.py stats image_seg.npy
```

### Merge Multiple Mask Files
```bash
python mask_utils.py merge output.npy file1_seg.npy file2_seg.npy
```

### Split Masks into Individual Files
```bash
python mask_utils.py split image_seg.npy -o output_dir/
```

## Requirements

- Python 3.7+
- numpy
- PyQt5
- scikit-image
- opencv-python
- scipy
- pillow

## Tips

- **Zoom before drawing** for more precise mask boundaries
- **Use undo** if you make a mistake (up to 50 steps)
- **Adjust mask opacity** using the slider for better visibility
- **Close polygons carefully** - release the mouse when you return to the starting point
- The current polygon being drawn is shown in **bright yellow**
- Completed masks are shown with **colored overlays**

