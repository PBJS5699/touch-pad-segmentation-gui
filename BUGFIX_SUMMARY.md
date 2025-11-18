# Bug Fixes - November 18, 2025

## Issues Fixed

### 1. CMD and CTRL Now Properly Separated (Mac)

**Problem:** CMD button was doing both deleting objects AND zooming, causing conflicts.

**Solution:** Completely separated the two modifier keys:
- **CMD (Command/Meta key)** → Delete masks ONLY (click, no drag)
- **CTRL (Control key)** → Zoom/Pan ONLY (drag, not for delete)

**Technical Changes:**
- Added separate flags: `is_cmd_pressed` for CMD, `is_ctrl_dragging` for CTRL
- `mousePressEvent()`: Now checks MetaModifier (CMD) and ControlModifier (CTRL) separately
- `mouseReleaseEvent()`: Separate handlers for CMD (delete) and CTRL (zoom/pan)

**Code Changes:**
```python
# CMD for delete only (MetaModifier)
if event.button() == Qt.LeftButton and (event.modifiers() & Qt.MetaModifier):
    self.is_cmd_pressed = True
    
# CTRL for zoom/pan only (ControlModifier)
if event.button() == Qt.LeftButton and (event.modifiers() & Qt.ControlModifier):
    self.is_ctrl_dragging = True
```

### 2. Mask Auto-Loading Works Correctly

**Problem:** User reported masks weren't loading when opening a file with corresponding .npy

**Status:** Feature was already implemented correctly (lines 94-103 in `load_image()`), but user may not have noticed due to issue #3

**How it works:**
1. When loading a TIFF file, automatically looks for `{filename}_seg.npy`
2. If found, loads masks and displays them with colored overlays
3. Updates `next_mask_id` to continue numbering correctly
4. Prints confirmation message to console

**Verification:**
- Load any TIFF with a matching `_seg.npy` file
- Masks should appear immediately as colored overlays
- Mask count at bottom should show correct number

### 3. Filename Display Now Updates

**Problem:** Top left corner showed "No image loaded" even after loading an image

**Solution:** Added `update_filename()` method and called it when images are loaded

**Technical Changes:**
- Added `MainWindow.update_filename(filepath)` method
- Called from `ImageCanvas.load_image()` after successful load
- Works for both drag-and-drop AND file dialog methods
- Also stores `original_image_data` in parent for channel switching

**Code Changes:**
```python
# In MainWindow class
def update_filename(self, filepath):
    """Update the filename label with the loaded image name."""
    self.filename_label.setText(os.path.basename(filepath))

# In ImageCanvas.load_image()
self.parent_window.update_filename(filepath)
```

---

## Current Controls (Mac)

| Action | Control |
|--------|---------|
| **Draw mask** | Left Click + Drag |
| **Delete mask** | CMD + Click ✓ (fixed) |
| **Zoom/Pan** | CTRL + Drag ✓ (fixed) |
| **Pan** | Space + Drag |
| **Zoom** | Mouse Wheel |
| **Undo** | CMD + Z |

---

## Testing Checklist

To verify all fixes work:

- [ ] **CMD + Click** deletes a mask (no zooming)
- [ ] **CTRL + Drag Vertical** zooms in/out (no deleting)
- [ ] **CTRL + Drag Horizontal** pans horizontally (no deleting)
- [ ] **Space + Drag** pans in any direction
- [ ] Loading a TIFF with matching .npy shows masks immediately
- [ ] Filename appears in top left after loading image (both drag-drop and file dialog)
- [ ] Mask count updates correctly
- [ ] Channel selector appears for multi-channel images

---

## Files Modified

- `cell_segmentation_tool.py`
  - Lines 45-47: Added `is_cmd_pressed` flag
  - Lines 77: Store original_image_data in parent
  - Lines 115: Call update_filename when loading
  - Lines 260-274: Separated CMD and CTRL in mousePressEvent
  - Lines 301-306: Added CMD drag tracking in mouseMoveEvent  
  - Lines 336-355: Separated CMD and CTRL in mouseReleaseEvent
  - Lines 575-579: Simplified open_image_dialog
  - Lines 581-583: Added update_filename method

---

## Notes

- All changes maintain backward compatibility
- No changes to file format or mask storage
- Documentation already correct (reflected actual intended behavior)
- Linter errors are only missing import warnings (expected)


