# Cell Segmentation Tool - Usage Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Basic Workflow](#basic-workflow)
3. [Drawing Techniques](#drawing-techniques)
4. [Navigation Controls](#navigation-controls)
5. [Editing Masks](#editing-masks)
6. [Working with Multi-Channel Images](#working-with-multi-channel-images)
7. [Keyboard Shortcuts](#keyboard-shortcuts)
8. [Tips and Best Practices](#tips-and-best-practices)
9. [File Format Details](#file-format-details)

---

## Getting Started

### Opening an Image

**Method 1: Drag and Drop**
- Drag a TIFF file from Finder/Explorer directly onto the canvas
- The image will load automatically with any existing masks

**Method 2: File Dialog**
- Click the "Open Image" button
- Select a TIFF file from the file browser

### First Time Setup

When you open an image for the first time:
1. The image appears centered in the window
2. If a matching `_seg.npy` file exists, masks are loaded automatically
3. The filename is displayed at the top
4. The mask count shows "Mask Count: 0" (or the number of existing masks)

---

## Basic Workflow

### 1. Load Your Image
```
File: my_cells.tif
```

### 2. Zoom to the Cell
- Use **mouse wheel** to zoom in
- Use **Shift + Drag** to pan to your target cell

### 3. Draw the Mask
- **Click and hold** the left mouse button at the cell boundary
- **Drag** around the cell perimeter
- **Release** when you return to the starting point
- The polygon auto-closes and the mask is created

### 4. Mask is Auto-Saved
```
Saved: my_cells_seg.npy
```

### 5. Continue with Next Cell
- Repeat steps 2-4 for each cell
- Each mask gets a unique ID automatically

---

## Drawing Techniques

### Freehand Drawing (Recommended for Apple Pencil)

1. **Zoom in close** to the cell (use mouse wheel)
2. **Click at a starting point** on the cell boundary
3. **Drag smoothly** around the perimeter
4. **Release near the start** to complete

**Tips:**
- The current polygon appears in **bright yellow**
- Points are added automatically as you drag
- Move slowly for more points (smoother boundary)
- Move faster for fewer points (faster drawing)

### Precise Point-by-Point Drawing

For more control, you can place points carefully:
1. Click at the starting point
2. Drag a tiny bit to place the next point
3. Continue around the cell boundary
4. Release to complete

---

## Navigation Controls

### Zooming

| Action | Control |
|--------|---------|
| Zoom in | Mouse wheel up |
| Zoom out | Mouse wheel down |
| Zoom via drag | CTRL + Drag vertically |

**Zoom Range:** 0.1x to 10x

### Panning

| Action | Control |
|--------|---------|
| Pan any direction | Space + Drag |
| Pan horizontally | CTRL + Drag horizontally |

### Reset View

To reset zoom and pan:
- Close and reopen the image

---

## Editing Masks

### Deleting a Mask

1. Hold **CMD** (Mac) or **CTRL** (Windows/Linux)
2. **Click** on the mask you want to delete
3. The mask disappears immediately
4. Changes auto-saved

### Undo Last Action

- Press **CMD + Z** (Mac) or **CTRL + Z** (Windows/Linux)
- Or click the **"Undo"** button at the bottom

**Undo Stack:**
- Stores up to 50 previous states
- Works for both new masks and deletions
- Cannot redo after undo (limitation)

### Modifying an Existing Mask

Currently, you cannot directly edit a mask. To modify:
1. **Delete** the incorrect mask (CMD + Click)
2. **Redraw** the corrected mask

---

## Working with Multi-Channel Images

### Viewing Different Channels

When you load a multi-channel TIFF:
1. A **"Channel"** dropdown appears at the top
2. Select any channel from the list
3. The display updates immediately
4. **Masks remain the same** across all channels

### Drawing on Multi-Channel Images

- Masks are **shared across all channels**
- They are stored as a 2D array (height × width)
- Drawing on one channel affects all channels
- Switch channels to verify your masks align properly

### RGB Composite vs Individual Channels

- If your TIFF has 3 channels, it may display as RGB
- If it has more than 3 channels, it displays channel 1 by default
- Use the channel selector to view individual channels

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **CMD + Z** (Mac) | Undo last mask change |
| **CTRL + Z** (Windows) | Undo last mask change |
| **CMD + Click** | Delete mask at cursor |
| **CTRL + Click** | Delete mask at cursor |
| **Space + Drag** | Pan the image |
| **Mouse Wheel** | Zoom in/out |

---

## Tips and Best Practices

### For Accurate Segmentation

1. **Zoom in** before drawing (2x-4x magnification)
2. **Draw slowly** for smoother boundaries
3. **Start and end at the same point** for clean closure
4. **Use consistent lighting/contrast** - adjust your display if needed

### For Faster Workflow

1. **Learn the shortcuts** - especially Undo and Delete
2. **Use Apple Pencil** if available for smoother drawing
3. **Adjust mask opacity** if overlays are too bright/dim
4. **Pan with Space+Drag** to quickly move between cells

### For Multi-Channel Data

1. **Draw on the clearest channel** first
2. **Switch channels** to verify boundaries align
3. **Use the same mask set** for all channels (automatic)

### Avoiding Common Mistakes

❌ **Don't:**
- Draw too fast (creates jagged edges)
- Zoom out too far (hard to see boundaries)
- Forget to check mask count (might duplicate)

✅ **Do:**
- Use undo immediately if you make a mistake
- Save frequently (auto-save does this for you!)
- Check mask overlays for gaps or overlaps

---

## File Format Details

### Input: TIFF Files

**Supported formats:**
- Single-channel grayscale TIFF
- RGB TIFF (3 channels)
- Multi-channel TIFF (any number of channels)
- 8-bit, 16-bit, or 32-bit depth

**Naming:**
- Any filename ending in `.tif` or `.tiff`

### Output: NPY Files

**Format:** NumPy array saved with `numpy.save()`

**Structure:**
```python
# Shape: (height, width)
# Data type: int32
# Values:
#   0 = background (no mask)
#   1 = first mask
#   2 = second mask
#   N = Nth mask
```

**Example:**
```python
import numpy as np

# Load masks
masks = np.load("my_cells_seg.npy")

# Check how many masks
num_masks = len(np.unique(masks)) - 1  # Exclude background (0)

# Get mask IDs
mask_ids = np.unique(masks)[1:]  # Skip 0

# Extract a specific mask
mask_3 = (masks == 3).astype(np.uint8)

# Count pixels in mask 5
mask_5_area = np.sum(masks == 5)
```

### Auto-Save Timing

Masks are automatically saved:
1. ✅ After drawing a new mask
2. ✅ After deleting a mask
3. ❌ NOT when just viewing or panning
4. ❌ NOT when changing channels (no changes to masks)

### File Pairing

The tool automatically pairs files:

```
Original file:  image_name.tif
Mask file:      image_name_seg.npy
```

**Rules:**
- Mask files are always in the **same directory** as the image
- The `_seg.npy` suffix is **automatically added**
- You cannot manually choose a different mask file name

---

## Advanced Usage

### Batch Processing (Command Line)

You can load mask files in Python for batch analysis:

```python
import numpy as np
from pathlib import Path

# Find all mask files
mask_files = Path("data/").glob("*_seg.npy")

for mask_file in mask_files:
    masks = np.load(mask_file)
    num_cells = len(np.unique(masks)) - 1
    print(f"{mask_file.name}: {num_cells} cells")
```

### Exporting Masks to Other Formats

```python
import numpy as np
from PIL import Image

# Load masks
masks = np.load("my_cells_seg.npy")

# Convert to colored image (for visualization)
colored = np.zeros((*masks.shape, 3), dtype=np.uint8)
for mask_id in range(1, masks.max() + 1):
    color = [(mask_id * 50) % 255, (mask_id * 100) % 255, (mask_id * 150) % 255]
    colored[masks == mask_id] = color

# Save as PNG
Image.fromarray(colored).save("my_cells_masks.png")
```

### Combining Masks from Multiple Sessions

```python
import numpy as np

# Load two mask files
masks1 = np.load("session1_seg.npy")
masks2 = np.load("session2_seg.npy")

# Offset IDs in second mask to avoid conflicts
max_id1 = masks1.max()
masks2_offset = np.where(masks2 > 0, masks2 + max_id1, 0)

# Combine (keeping non-overlapping masks)
combined = np.where(masks1 > 0, masks1, masks2_offset)

# Save
np.save("combined_seg.npy", combined)
```

---

## Troubleshooting

### "Mask overlays don't show"
- Check the **mask opacity slider** at the bottom
- Increase opacity to 60-80%

### "Polygon doesn't close properly"
- Make sure you **release the mouse** near the starting point
- Try drawing slower for better control

### "Undo doesn't work"
- Undo only works for the current session
- Once you close the app, undo history is lost

### "Drag and drop doesn't work"
- Make sure you're dragging **directly onto the canvas** (black area)
- Try using "Open Image" button instead

### "Multi-channel selector doesn't appear"
- Your TIFF may be single-channel or RGB (3-channel)
- Selector only appears for 4+ channel images

---

## Keyboard and Mouse Reference

### Mouse Button States

| Button State | Action | Result |
|-------------|--------|--------|
| Left Click | Start | Begin drawing polygon |
| Left Hold | Drag | Add points to polygon |
| Left Release | End | Close polygon and create mask |
| Wheel Up | Scroll | Zoom in |
| Wheel Down | Scroll | Zoom out |

### Modifier Keys

| Modifier | + Mouse | Action |
|----------|---------|--------|
| **CMD/CTRL** | Click | Delete mask |
| **CTRL** | Drag Vertical | Zoom in/out |
| **CTRL** | Drag Horizontal | Pan horizontally |
| **Space** | Drag | Pan any direction |
| **CMD/CTRL** | Z key | Undo |

---

## Example Session

Here's a complete workflow example:

```
1. Launch: python cell_segmentation_tool.py
2. Drag: my_experiment_001.tif onto canvas
3. Status: "my_experiment_001.tif" appears at top
4. Zoom: Mouse wheel to 3x magnification
5. Pan: Space+Drag to first cell
6. Draw: Left-click and drag around cell boundary
7. Release: Mask appears with random color
8. Status: "Mask Count: 1"
9. Auto-saved: my_experiment_001_seg.npy created
10. Pan: Space+Drag to next cell
11. Draw: Create second mask
12. Status: "Mask Count: 2"
13. Oops: Made a mistake on mask 2
14. Undo: CMD+Z to remove it
15. Redraw: Create mask 2 correctly
16. Continue: Draw remaining cells...
17. Done: Close application
18. Result: All masks saved in my_experiment_001_seg.npy
```

---

## Support and Modification

This tool is designed to be easily modified. Key sections to customize:

- **`ImageCanvas.paintEvent()`** - Change how masks are displayed
- **`ImageCanvas._create_mask_overlay()`** - Modify mask colors
- **`ImageCanvas.mousePressEvent()`** - Add new mouse interactions
- **`MainWindow.init_ui()`** - Add new UI controls

For questions or modifications, refer to the inline code comments.

