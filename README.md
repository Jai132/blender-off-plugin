# blender-off-plugin
A simple script for off/coff file format support in Blender

## Installation
1. Download `off_support.py` from this repository.
2. In Blender, go to **Edit > Preferences > Add-ons > Install**(on the top right corner drop-down).
3. Select `off_support.py` and click **Install from Disk**.
4. Enable the add-on by checking the box next to "OFF/COFF Importer/Exporter".

## Usage
- **Import**: Go to **File > Import > OFF/COFF (.off/.coff)**, select a `.off` or `.coff` file.
- **Export**: Select a mesh object, then go to **File > Export > OFF/COFF (.off/.coff)**, choose `.off` or `.coff` format.
- **View Colors** (for `.coff`):
  - Select the imported object.
  - Switch to **Material Preview** or **Rendered** mode (Z key > Material Preview).
  - In **Shading Workspace**, add a **Vertex Color** node (set to "Col") and connect to **Base Color** of **Principled BSDF**.
  - Alternatively, use **Vertex Paint** mode to inspect colors.

## Requirements
- Blender 3.0 or higher.
- `.coff` files must have RGB values (0-255) after vertex coordinates.

## Notes
- Ensure `.coff` files include valid color data (e.g., `x y z r g b` per vertex).
- Check Blender Console for errors if import/export fails.
- Vertex colors are stored in a "Col" color attribute.
