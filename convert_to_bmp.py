"""
Convert PNG images to BMP format and replace the original PNG files.

This script allows you to select a folder containing PNG images and converts
all of them to BMP format. The original PNG files are deleted after successful conversion.

Author: GitHub Copilot
Date: 2026-01-27
"""

from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_png_to_bmp():
    """
    Convert all PNG images in a selected folder to BMP format.
    """
    
    # Create root window for file dialogs
    root = tk.Tk()
    root.withdraw()
    
    # Ask user to select folder
    image_folder = filedialog.askdirectory(title="Select folder containing PNG images")
    
    if not image_folder:
        messagebox.showwarning("No Selection", "No folder was selected. Exiting.")
        return
    
    # Find all PNG files in the folder
    png_files = sorted(
        [f for f in os.listdir(image_folder) if f.lower().endswith('.png')],
        key=lambda x: x.lower()
    )
    
    if not png_files:
        messagebox.showwarning("No Images", f"No PNG images found in:\n{image_folder}")
        return
    
    print(f"Found {len(png_files)} PNG file(s) in: {image_folder}")
    print()
    
    # Convert each PNG to BMP
    converted_count = 0
    failed_files = []
    
    for png_file in png_files:
        png_path = os.path.join(image_folder, png_file)
        
        # Create BMP filename (replace .png with .bmp)
        bmp_file = os.path.splitext(png_file)[0] + '.bmp'
        bmp_path = os.path.join(image_folder, bmp_file)
        
        try:
            # Open PNG image
            img = Image.open(png_path)
            
            # Convert to grayscale if it's not already
            if img.mode != 'L' and img.mode != '1':
                img = img.convert('L')
            
            # Save as BMP
            img.save(bmp_path, 'BMP')
            
            # Delete the original PNG file after successful conversion
            os.remove(png_path)
            
            converted_count += 1
            print(f"✓ {png_file} → {bmp_file} (original PNG deleted)")
            
        except Exception as e:
            failed_files.append((png_file, str(e)))
            print(f"✗ {png_file} - Error: {e}")
    
    print()
    print("=" * 60)
    print(f"Conversion complete!")
    print(f"Successfully converted: {converted_count}/{len(png_files)} files")
    
    if failed_files:
        print(f"\nFailed conversions ({len(failed_files)}):")
        for filename, error in failed_files:
            print(f"  - {filename}: {error}")
    
    if converted_count == len(png_files):
        messagebox.showinfo("Success", 
            f"Successfully converted {converted_count} PNG image(s) to BMP format!\n"
            f"Original PNG files have been deleted.")
    else:
        messagebox.showwarning("Partial Success", 
            f"Converted {converted_count}/{len(png_files)} files.\n"
            f"Original PNG files were only deleted for successful conversions.\n"
            f"Check the console for details on failed conversions.")

if __name__ == "__main__":
    convert_png_to_bmp()
