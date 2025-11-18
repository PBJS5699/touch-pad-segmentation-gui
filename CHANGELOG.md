# Changelog

## Version 1.1 - November 18, 2025

### Fixed
- **CTRL + Drag** now properly works for zoom/pan
  - Previously: CTRL+click would immediately trigger delete, preventing drag
  - Now: System waits to see if mouse moves before treating as delete vs drag
  - Delete only triggers if mouse moves less than 5 pixels

- **Space + Drag** now properly works for panning
  - Previously: Used Shift key as proxy (didn't work well)
  - Now: Properly tracks Space key press/release
  - Cursor changes to open hand when Space is held

### Changed
- **Instructions text made smaller** (8px instead of 10px)
- **Instructions text simplified** for better readability
  - Before: "Controls: Left Click+Drag=Draw Mask | Cmd+Click=Delete Mask | Ctrl+Drag=Zoom/Pan | Wheel=Zoom | Shift+Drag=Pan"
  - After: "Left Click+Drag=Draw | Cmd+Click=Delete | Ctrl+Drag=Zoom/Pan | Wheel=Zoom | Space+Drag=Pan"

### Technical Details
- Added `space_pressed` flag to track Space key state
- Implemented `keyPressEvent()` and `keyReleaseEvent()` handlers
- Modified mouse event logic to distinguish clicks from drags
- Updated cursor to show open hand icon when Space is held

### Documentation Updated
- README.md
- QUICK_REFERENCE.md
- USAGE_GUIDE.md
- PROJECT_OVERVIEW.md

All documentation now correctly shows Space+Drag for panning (not Shift+Drag)

---

## Version 1.0 - November 18, 2025

### Initial Release
- Complete cell segmentation tool with PyQt5 GUI
- Drag-and-drop TIFF loading
- Freehand polygon mask drawing
- Auto-save functionality
- Multi-channel support
- Undo system
- Comprehensive documentation


