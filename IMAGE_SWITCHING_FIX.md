# Image Switching & Mask Loading Fix - November 18, 2025

## Issues Fixed

### 1. ✅ Fixed Error When Dragging New Images

**Error:**
```
Failed to load image: can only convert an array of size 1 to a Python scalar
```

**Cause:** The code was calling `.item()` on large numpy arrays, which only works on scalar (size 1) arrays.

**Solution:** Updated the logic to properly detect 0-dimensional object arrays (CellPose format) before calling `.item()`:

```python
# Only call .item() on 0-d object arrays
if loaded_masks.ndim == 0 and loaded_masks.dtype == object:
    masks_dict = loaded_masks.item()  # Safe now!
    if isinstance(masks_dict, dict) and 'masks' in masks_dict:
        loaded_masks = masks_dict['masks']
```

### 2. ✅ Auto-Save Before Switching Images

**Problem:** When dragging a new image or opening via dialog, the current masks weren't being saved.

**Solution:** Added auto-save before loading new images in both methods:
- Drag-and-drop: Saves current masks before loading
- File dialog: Saves current masks before loading

### 3. ✅ Automatic Mask Overlay Loading

**Confirmed Working:** When loading an image with a corresponding `.npy` file:
- ✅ Masks load automatically
- ✅ Overlays display immediately
- ✅ Mask count updates
- ✅ Filename updates
- ✅ Works with both CellPose and simple array formats

---

## How It Works Now

### Loading a New Image (Drag & Drop)

```
1. User drags new TIFF onto canvas
2. Current masks auto-saved (if any)
3. New image loads
4. Looks for {filename}_seg.npy
5. If found, loads and displays masks
6. Overlays appear automatically
```

### Loading a New Image (File Dialog)

```
1. User clicks "Open Image"
2. Current masks auto-saved (if any)
3. User selects TIFF file
4. Image loads
5. Looks for {filename}_seg.npy
6. If found, loads and displays masks
7. Overlays appear automatically
```

---

## File Format Detection

The tool automatically detects which format your `.npy` file is in:

### CellPose Format (0-d Object Array)
```python
# What gets loaded from CellPose files
array({
    'masks': array([[0, 1, ...]], dtype=uint16),
    'filename': '...',
    # ... metadata
}, dtype=object)
```

**Detection:** `ndim == 0` and `dtype == object`

### Simple Array Format
```python
# What this tool saves
array([[0, 1, 1, ...],
       [0, 1, 1, ...]], dtype=int32)
```

**Detection:** `ndim >= 2` (2D or higher)

---

## Testing Checklist

### Test 1: Loading Example File
```bash
# Drag this onto canvas:
example-io/20250805_UTX265_midplane_1_MMStack_Pos0_GP30003.tif

Expected results:
✅ No errors
✅ Console: "Loaded CellPose format masks"
✅ Console: "Loaded 1 masks from ..."
✅ Colored overlay appears
✅ Mask count shows "1"
✅ Filename shows at top
```

### Test 2: Switching Between Images
```bash
# 1. Load first image
#    - Draw some masks
#    - Should auto-save

# 2. Drag second image onto canvas
#    - First image masks should auto-save
#    - Second image loads
#    - If second image has masks, they load
#    - No errors

# 3. Drag first image back
#    - Second image masks auto-saved
#    - First image loads with its masks
#    - All masks preserved
```

### Test 3: Creating New Masks
```bash
# 1. Load any TIFF
# 2. Draw masks
# 3. Drag different TIFF
# 4. Drag first TIFF back
# Expected: First image shows your masks ✅
```

---

## Error Handling

The tool now gracefully handles errors:

```python
try:
    loaded_masks = np.load(mask_path, allow_pickle=True)
    # ... loading logic
except Exception as e:
    print(f"Warning: Could not load masks from {mask_path}: {str(e)}")
    # Continues with empty masks
```

**Benefits:**
- Won't crash if mask file is corrupted
- Shows warning in console
- Continues loading the image with empty masks

---

## Workflow Example

### Complete Session

```
1. Open app
   → Status: "No image loaded"

2. Drag: image1.tif
   → Loads with existing masks (if any)
   → Status: "Mask Count: 2" (example)
   
3. Add more masks
   → Auto-saved after each draw
   → Status: "Mask Count: 4"

4. Drag: image2.tif
   → image1 masks auto-saved
   → image2 loads with its masks
   → Status: "Mask Count: 0" (new image)

5. Draw masks on image2
   → Auto-saved
   → Status: "Mask Count: 3"

6. Drag: image1.tif (back to first)
   → image2 masks auto-saved
   → image1 loads with all 4 masks
   → Status: "Mask Count: 4"

7. Close app
   → All changes saved automatically
```

---

## Console Output Examples

### Loading CellPose Format
```
Loaded CellPose format masks from example-io/file_seg.npy
Loaded 1 masks from example-io/file_seg.npy
```

### Loading Simple Format
```
Loaded 5 masks from my_image_seg.npy
```

### Auto-Save on Switch
```
Saved 5 masks to my_image_seg.npy
Loaded 2 masks from other_image_seg.npy
```

### Error Handling
```
Warning: Could not load masks from corrupted_seg.npy: Invalid file format
```

---

## Files Modified

**cell_segmentation_tool.py:**
- **Lines 97-120:** Fixed mask loading logic (proper .item() usage)
- **Lines 514-516:** Added auto-save on drag-and-drop
- **Lines 622-624:** Added auto-save on file dialog open

---

## Summary

✅ **Fixed error** when dragging new images  
✅ **Auto-saves** current masks before switching  
✅ **Auto-loads** masks for new images  
✅ **Displays overlays** immediately  
✅ **Handles errors** gracefully  
✅ **Works with** both CellPose and simple formats  

**You can now seamlessly switch between images without any errors!** 🎉


