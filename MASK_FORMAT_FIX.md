# Mask Loading Fix - November 18, 2025

## Issues Fixed

### 1. ✅ Masks Now Load Automatically with Overlays

**Problem:** When loading an image with a corresponding `.npy` file, the masks weren't appearing as overlays.

**Solution:** The code was already correct for loading, but now enhanced to handle multiple file formats and provide better feedback.

### 2. ✅ Compatible with CellPose Format

**Problem:** The example `.npy` file uses CellPose format (dictionary with metadata), which is different from a simple array.

**Solution:** Updated the loading code to handle both formats:
- **CellPose format**: Dictionary/object with a `'masks'` key (like the example)
- **Simple array format**: Direct numpy array (what this tool saves)

## File Format Details

### Example File Format (CellPose)

```python
{
    'masks': array([[0, 0, ...], [0, 1, ...]], dtype=uint16),  # The actual masks
    'filename': '/path/to/image.tif',
    'flows': [...],
    'ismanual': array([True]),
    'manual_changes': [...],
    # ... more metadata
}
```

**Structure:**
- Wrapped in a dictionary
- Contains metadata and history
- Masks stored under `'masks'` key
- Shape: `(height, width)`
- Values: `0` = background, `1, 2, 3...` = individual masks

### This Tool's Format (Simple Array)

```python
array([[0, 0, 0, ...],
       [0, 1, 1, ...],
       [0, 1, 1, ...]], dtype=int32)
```

**Structure:**
- Direct numpy array (no wrapping)
- No metadata (lightweight)
- Shape: `(height, width)`
- Values: `0` = background, `1, 2, 3...` = individual masks

**Both formats work!** The tool auto-detects which format is being loaded.

## How It Works

### Loading Masks (Updated Code)

```python
loaded_masks = np.load(mask_path, allow_pickle=True)

# Handle CellPose format (dictionary with 'masks' key)
if isinstance(loaded_masks, dict) or (hasattr(loaded_masks, 'item') and isinstance(loaded_masks.item(), dict)):
    masks_dict = loaded_masks.item() if hasattr(loaded_masks, 'item') else loaded_masks
    if 'masks' in masks_dict:
        loaded_masks = masks_dict['masks']
        print(f"Loaded CellPose format masks from {mask_path}")

# Use the extracted array
if isinstance(loaded_masks, np.ndarray):
    self.masks = loaded_masks.astype(np.int32)
    print(f"Loaded {len(np.unique(self.masks)) - 1} masks")
```

### Saving Masks

```python
# Always saves as simple array format
np.save(mask_path, self.masks)
```

This tool saves in simple format for efficiency, but can load both formats.

## Testing

### Test with Example File

```bash
# Load the example image
python cell_segmentation_tool.py
# Drag: example-io/20250805_UTX265_midplane_1_MMStack_Pos0_GP30003.tif

# You should see:
# - Filename appears at top
# - Console prints: "Loaded CellPose format masks"
# - Console prints: "Loaded 1 masks from ..."
# - Colored overlay appears on the image
# - Mask count shows "Mask Count: 1"
```

### Test with Your Own Files

1. Create masks with this tool
2. Close the application
3. Reopen the same TIFF file
4. Masks should automatically load and display

## Verification Checklist

When loading an image with existing masks, you should see:

- ✅ Filename updates in top left
- ✅ Console message: "Loaded X masks from ..."
- ✅ Colored overlays appear on the image
- ✅ Mask count updates at bottom ("Mask Count: X")
- ✅ Can delete existing masks with CMD+click
- ✅ Can add new masks
- ✅ New mask IDs continue from the highest existing ID

## File Format Compatibility

| Feature | This Tool Output | CellPose Format | Compatible? |
|---------|-----------------|-----------------|-------------|
| **Load** | ✅ Yes | ✅ Yes | Fully compatible |
| **Save** | ✅ Simple array | ❌ No metadata | Tool uses simple format |
| **Display** | ✅ Colored overlays | ✅ Same | Identical display |
| **Edit** | ✅ Full editing | ✅ Full editing | Same functionality |

## Common Issues

### "No overlays appear"

**Check:**
1. Is the `.npy` file in the same directory as the `.tif`?
2. Does it have the correct naming: `{image_name}_seg.npy`?
3. Check console for error messages

**Solution:**
- The mask file must be in the same folder
- Use exact naming convention
- Look for console output when loading

### "Wrong number of masks"

**Possible causes:**
1. Multiple masks have the same ID (shouldn't happen)
2. Mask IDs are not consecutive (this is OK!)

**Note:** Mask IDs don't have to be consecutive (1, 2, 3...). They can be (1, 5, 8...) after deletions.

### "Can't load masks from other software"

**Supported:**
- ✅ CellPose `.npy` files with `'masks'` key
- ✅ Simple numpy arrays saved with `np.save()`

**Not supported:**
- ❌ Text files
- ❌ Images (PNG/TIFF masks)
- ❌ Other proprietary formats

**Solution:** Convert to simple numpy array format

---

## Summary

✅ **Masks auto-load**: When opening a TIFF with matching `_seg.npy`  
✅ **Overlays display**: Colored overlays appear immediately  
✅ **CellPose compatible**: Reads CellPose format masks  
✅ **Simple saves**: Saves lightweight array format  
✅ **Consistent IDs**: Mask IDs preserved across sessions  

**The tool now works seamlessly with both its own format and CellPose format!**


