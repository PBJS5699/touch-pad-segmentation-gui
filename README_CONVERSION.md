# Converting Existing Mask Files to CellPose Format

## Quick Start

### Test First (Dry Run)
```bash
python convert_masks_to_cellpose.py --dry-run
```

### Convert with Backups
```bash
python convert_masks_to_cellpose.py --backup
```

### Convert Without Backups
```bash
python convert_masks_to_cellpose.py
```

---

## What This Script Does

The conversion script:

1. **Finds** all `*_seg.npy` files in `/Volumes/T7/Alchemy images/Dr. Dickenson`
2. **Checks** if they're already in CellPose format
3. **Converts** simple arrays to CellPose format
4. **Preserves** all mask data (no loss of information)
5. **Associates** each mask with its corresponding TIFF file

---

## Command Options

### Default (Convert Files)
```bash
python convert_masks_to_cellpose.py
```
Converts all files in the default directory.

### Dry Run (Preview Only)
```bash
python convert_masks_to_cellpose.py --dry-run
```
Shows what would be converted **without actually changing files**.

### With Backups
```bash
python convert_masks_to_cellpose.py --backup
```
Creates `.backup` files before converting (safer option).

### Custom Directory
```bash
python convert_masks_to_cellpose.py "/path/to/your/directory" --backup
```

### Combine Options
```bash
python convert_masks_to_cellpose.py --dry-run --backup
```

---

## Output Examples

### Dry Run Output:
```
Searching for mask files in: /Volumes/T7/Alchemy images/Dr. Dickenson
DRY RUN MODE - No files will be modified

Found 127 mask files
--------------------------------------------------------------------------------
[1/127] ✓ Converted: image1_seg.npy (3 masks)
[2/127] ○ Already CellPose format: image2_seg.npy
[3/127] ✓ Converted: image3_seg.npy (5 masks)
...

================================================================================
SUMMARY
================================================================================
Total files found:       127
Converted:               95
Already CellPose format: 30
No TIFF file found:      2
Unknown format:          0
Errors:                  0

Run without --dry-run to actually convert the files
```

### Actual Conversion:
```
Searching for mask files in: /Volumes/T7/Alchemy images/Dr. Dickenson
BACKUP MODE - Creating .backup files

Found 127 mask files
--------------------------------------------------------------------------------
[1/127] ✓ Converted: image1_seg.npy (3 masks)
[2/127] ○ Already CellPose format: image2_seg.npy
...

================================================================================
SUMMARY
================================================================================
Total files found:       127
Converted:               95
Already CellPose format: 30
No TIFF file found:      2
Unknown format:          0
Errors:                  0

✓ Successfully converted 95 files!
  Backups saved with .backup extension
```

---

## Status Symbols

| Symbol | Meaning |
|--------|---------|
| **✓** | Successfully converted |
| **○** | Already in CellPose format (skipped) |
| **✗** | Error or no TIFF file found |
| **?** | Unknown format |

---

## Safety Features

### 1. Dry Run Mode
Test the conversion without modifying files:
```bash
python convert_masks_to_cellpose.py --dry-run
```

### 2. Automatic Backups
Create backups before conversion:
```bash
python convert_masks_to_cellpose.py --backup
```
Each file gets a `.backup` copy (e.g., `image_seg.npy.backup`)

### 3. Format Detection
- Skips files already in CellPose format
- Only converts simple arrays
- Reports any unknown formats

### 4. Error Handling
- Continues if one file fails
- Reports all errors at the end
- Doesn't corrupt existing files

---

## What Gets Converted

### Before (Simple Array):
```python
# Just a 2D numpy array
array([[0, 0, 1, ...],
       [0, 1, 1, ...]], dtype=int32)
```

### After (CellPose Format):
```python
# Dictionary wrapped in 0-d array
{
    'masks': array([[0, 0, 1, ...]], dtype=uint16),
    'filename': '/path/to/image.tif',
    'flows': [],
    'ismanual': array([True]),
    'manual_changes': [],
    # ... CellPose metadata
}
```

---

## Troubleshooting

### "No TIFF file found"
**Cause:** The corresponding `.tif` file is missing.

**Solution:** 
- The mask file needs its original TIFF image
- Make sure both files are in the same directory
- File names must match (e.g., `image.tif` and `image_seg.npy`)

### "Unknown format"
**Cause:** The .npy file is in an unexpected format.

**Solution:**
- Check the file manually
- May need custom handling

### Permission Errors
**Solution:**
```bash
# Make sure you have write access
chmod u+w /Volumes/T7/Alchemy\ images/Dr.\ Dickenson
```

---

## Recommended Workflow

### Step 1: Test First
```bash
python convert_masks_to_cellpose.py --dry-run
```
Review what will be converted.

### Step 2: Convert with Backups
```bash
python convert_masks_to_cellpose.py --backup
```
Safe conversion with backups.

### Step 3: Verify
Open a few files in CellPose to confirm they work.

### Step 4: Clean Up (Optional)
```bash
# Remove backup files after verifying
find "/Volumes/T7/Alchemy images/Dr. Dickenson" -name "*_seg.npy.backup" -delete
```

---

## After Conversion

Your mask files will be:
- ✓ Compatible with CellPose GUI
- ✓ Compatible with this tool
- ✓ Standard format for sharing
- ✓ Include all metadata

You can now:
- Load them in CellPose without errors
- Continue editing in either tool
- Share them with collaborators
- Use them for training models

---

## Notes

- **No data loss:** All mask information is preserved
- **Reversible:** Backup files allow reverting if needed
- **Safe:** Dry-run mode lets you preview changes
- **Fast:** Processes hundreds of files in seconds
- **Recursive:** Searches all subdirectories automatically

---

## Questions?

Run with `--help` for more information:
```bash
python convert_masks_to_cellpose.py --help
```

