"""
Convert existing mask files to CellPose-compatible format.

This script finds all _seg.npy files in a directory and converts them
from simple array format to CellPose format.

Usage:
    python convert_masks_to_cellpose.py [--dry-run] [--backup]
"""

import os
import sys
from pathlib import Path
import numpy as np
import shutil
import argparse


def is_cellpose_format(data):
    """Check if the loaded data is already in complete CellPose format."""
    # CellPose format is a 0-d object array containing a dict
    if isinstance(data, np.ndarray) and data.ndim == 0 and data.dtype == object:
        item = data.item()
        if isinstance(item, dict) and 'masks' in item:
            # Check if it has the required fields (including outlines and colors)
            required_fields = ['masks', 'outlines', 'colors']
            has_all = all(field in item for field in required_fields)
            return has_all
    return False


def generate_outlines(masks):
    """Generate outline array for CellPose format."""
    import cv2
    
    outlines = np.zeros_like(masks, dtype=np.uint16)
    unique_ids = np.unique(masks)
    unique_ids = unique_ids[unique_ids > 0]
    
    for mask_id in unique_ids:
        binary_mask = (masks == mask_id).astype(np.uint8)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(outlines, contours, -1, int(mask_id), 1)
    
    return outlines


def generate_colors(masks):
    """Generate color array for CellPose format."""
    import cv2
    
    unique_ids = np.unique(masks)
    unique_ids = unique_ids[unique_ids > 0]
    
    if len(unique_ids) == 0:
        return np.array([[0, 0, 0]], dtype=np.int64)
    
    colors = []
    for mask_id in unique_ids:
        hue = (mask_id * 137) % 180
        color = cv2.cvtColor(np.uint8([[[hue, 255, 255]]]), cv2.COLOR_HSV2RGB)[0, 0]
        colors.append([int(color[0]), int(color[1]), int(color[2])])
    
    return np.array(colors, dtype=np.int64)


def convert_to_cellpose_format(masks_array, image_path):
    """Convert a simple mask array to CellPose format."""
    # Generate outlines and colors
    outlines = generate_outlines(masks_array)
    colors = generate_colors(masks_array)
    
    cellpose_data = {
        'outlines': outlines,
        'colors': colors,
        'masks': masks_array.astype(np.uint16),
        'filename': str(image_path),
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
    
    # Return as 0-dimensional object array
    return np.array(cellpose_data, dtype=object)


def find_mask_files(directory):
    """Find all _seg.npy files in the directory and subdirectories."""
    directory = Path(directory)
    all_files = directory.rglob("*_seg.npy")
    
    # Filter out macOS resource fork files (starting with ._)
    mask_files = [f for f in all_files if not f.name.startswith('._')]
    
    return sorted(mask_files)


def get_corresponding_tif(mask_path):
    """Get the corresponding TIFF file path for a mask file."""
    mask_path = Path(mask_path)
    # Remove _seg.npy and try different extensions
    base_name = mask_path.stem.replace('_seg', '')
    
    for ext in ['.tif', '.tiff', '.TIF', '.TIFF']:
        tif_path = mask_path.parent / (base_name + ext)
        if tif_path.exists():
            return tif_path
    
    return None


def convert_file(mask_path, dry_run=False, backup=False):
    """Convert a single mask file to CellPose format."""
    try:
        # Load the mask file
        data = np.load(mask_path, allow_pickle=True)
        
        # Check if already in complete CellPose format
        if is_cellpose_format(data):
            return 'already_cellpose', None
        
        # Check if it's a CellPose dict but missing outlines/colors
        if isinstance(data, np.ndarray) and data.ndim == 0 and data.dtype == object:
            item = data.item()
            if isinstance(item, dict) and 'masks' in item:
                # Has dictionary structure but missing fields - extract masks
                masks_array = item['masks']
                tif_path = get_corresponding_tif(mask_path)
                if tif_path is None:
                    return 'no_tif', "No corresponding TIFF file found"
                
                num_masks = len(np.unique(masks_array)) - 1
                
                if not dry_run:
                    if backup:
                        backup_path = str(mask_path) + '.backup'
                        shutil.copy2(mask_path, backup_path)
                    
                    # Re-convert with complete format
                    cellpose_data = convert_to_cellpose_format(masks_array, tif_path)
                    np.save(mask_path, cellpose_data)
                
                return 'converted', f"{num_masks} masks (updated format)"
        
        # Check if it's a simple array
        if isinstance(data, np.ndarray) and data.ndim >= 2:
            # Get corresponding TIFF file
            tif_path = get_corresponding_tif(mask_path)
            if tif_path is None:
                return 'no_tif', "No corresponding TIFF file found"
            
            # Count masks
            num_masks = len(np.unique(data)) - 1
            
            if not dry_run:
                # Backup if requested
                if backup:
                    backup_path = str(mask_path) + '.backup'
                    shutil.copy2(mask_path, backup_path)
                
                # Convert to CellPose format
                cellpose_data = convert_to_cellpose_format(data, tif_path)
                
                # Save
                np.save(mask_path, cellpose_data)
            
            return 'converted', f"{num_masks} masks"
        else:
            return 'unknown_format', "Unknown format"
            
    except Exception as e:
        return 'error', str(e)


def main():
    parser = argparse.ArgumentParser(
        description='Convert mask files to CellPose format'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='/Volumes/T7/Alchemy images/Dr. Dickenson',
        help='Directory to search for mask files (default: /Volumes/T7/Alchemy images/Dr. Dickenson)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be converted without actually converting'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create .backup files before converting'
    )
    
    args = parser.parse_args()
    
    # Check if directory exists
    if not os.path.exists(args.directory):
        print(f"Error: Directory not found: {args.directory}")
        sys.exit(1)
    
    print(f"Searching for mask files in: {args.directory}")
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified")
    if args.backup:
        print("BACKUP MODE - Creating .backup files")
    print()
    
    # Find all mask files
    mask_files = find_mask_files(args.directory)
    
    if not mask_files:
        print("No mask files (*_seg.npy) found.")
        return
    
    print(f"Found {len(mask_files)} mask files")
    print("-" * 80)
    
    # Statistics
    stats = {
        'converted': 0,
        'already_cellpose': 0,
        'no_tif': 0,
        'unknown_format': 0,
        'error': 0
    }
    
    # Convert each file
    for i, mask_path in enumerate(mask_files, 1):
        status, info = convert_file(mask_path, args.dry_run, args.backup)
        stats[status] += 1
        
        # Print progress
        if status == 'converted':
            print(f"[{i}/{len(mask_files)}] ✓ Converted: {mask_path.name} ({info})")
        elif status == 'already_cellpose':
            print(f"[{i}/{len(mask_files)}] ○ Already CellPose format: {mask_path.name}")
        elif status == 'no_tif':
            print(f"[{i}/{len(mask_files)}] ✗ No TIFF found: {mask_path.name}")
        elif status == 'unknown_format':
            print(f"[{i}/{len(mask_files)}] ? Unknown format: {mask_path.name}")
        elif status == 'error':
            print(f"[{i}/{len(mask_files)}] ✗ Error: {mask_path.name} - {info}")
    
    # Print summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files found:       {len(mask_files)}")
    print(f"Converted:               {stats['converted']}")
    print(f"Already CellPose format: {stats['already_cellpose']}")
    print(f"No TIFF file found:      {stats['no_tif']}")
    print(f"Unknown format:          {stats['unknown_format']}")
    print(f"Errors:                  {stats['error']}")
    print()
    
    if args.dry_run and stats['converted'] > 0:
        print("Run without --dry-run to actually convert the files")
    elif not args.dry_run and stats['converted'] > 0:
        print(f"✓ Successfully converted {stats['converted']} files!")
        if args.backup:
            print(f"  Backups saved with .backup extension")


if __name__ == "__main__":
    main()

