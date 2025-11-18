# Quick Reference Card - Cell Segmentation Tool

## Installation & Launch

```bash
# Install dependencies
pip install -r requirements.txt

# Launch application
python cell_segmentation_tool.py

# OR use launcher scripts
./run.sh           # Mac/Linux
run.bat            # Windows
```

---

## Essential Controls

| Action | Control |
|--------|---------|
| **Open Image** | Drag TIFF onto canvas OR "Open Image" button |
| **Draw Mask** | Left Click + Drag around cell |
| **Delete Mask** | CMD/CTRL + Click on mask |
| **Undo** | CMD/CTRL + Z |
| **Zoom In/Out** | Mouse Wheel or CTRL + Drag Vertical |
| **Pan** | Space + Drag |

---

## File Naming

```
Input:  image_name.tif
Output: image_name_seg.npy  (auto-saved)
```

---

## Workflow

1. **Load** image (drag or open)
2. **Zoom** to target cell (mouse wheel)
3. **Draw** mask (left click + drag)
4. **Auto-saves** immediately
5. **Repeat** for next cell

---

## Utilities

### Inspect Masks
```bash
python mask_utils.py inspect my_cells_seg.npy
```

### Export to PNG
```bash
python mask_utils.py export my_cells_seg.npy
```

### Calculate Statistics
```bash
python mask_utils.py stats my_cells_seg.npy
```

### Merge Mask Files
```bash
python mask_utils.py merge output.npy file1_seg.npy file2_seg.npy
```

---

## Mask File Format

**NumPy Array (.npy)**
- Shape: `(height, width)`
- Type: `int32`
- Values:
  - `0` = background
  - `1, 2, 3...` = individual masks

**Loading in Python:**
```python
import numpy as np
masks = np.load("image_seg.npy")
num_cells = len(np.unique(masks)) - 1
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't see masks | Increase opacity slider |
| Polygon won't close | Release mouse near start point |
| Drag-drop fails | Drag onto black canvas area |
| Packages missing | `pip install -r requirements.txt` |

---

## Tips

✓ **Zoom in** before drawing (2-4x recommended)  
✓ **Draw slowly** for smooth boundaries  
✓ **Use undo** immediately if you make a mistake  
✓ **Check mask count** at bottom to track progress  
✓ **Apple Pencil** works great via Sidecar on Mac  

---

## Documentation

- **README.md** - Overview and features
- **SETUP.md** - Installation instructions
- **USAGE_GUIDE.md** - Comprehensive manual
- **QUICK_REFERENCE.md** - This file

---

## Example Session

```bash
# 1. Launch
python cell_segmentation_tool.py

# 2. Drag image onto window
#    example-io/20250805_UTX265_midplane_1_MMStack_Pos0_GP30003.tif

# 3. Draw masks with left click + drag

# 4. Delete mistakes with CMD+Click

# 5. Close when done (auto-saved throughout)
```

---

## Keyboard Shortcuts Summary

| Key | Action |
|-----|--------|
| CMD/CTRL + Z | Undo |
| CMD/CTRL + Click | Delete |
| Shift + Drag | Pan |
| Mouse Wheel | Zoom |

---

## Support

For detailed information, see **USAGE_GUIDE.md**

For code modification, see comments in **cell_segmentation_tool.py**

