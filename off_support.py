bl_info = {
    "name": "OFF/COFF Importer/Exporter",
    "author": "Jai Tyagi (2025)",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "category": "Import-Export",
    "description": "Import and export OFF and COFF files",
}




import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper

class ImportOFF(Operator, ImportHelper):
    """Import OFF file"""
    bl_idname = "import_mesh.off"
    bl_label = "Import OFF"
    filename_ext = ".off"
    filter_glob: StringProperty(default="*.off;*.coff", options={'HIDDEN'})

    def execute(self, context):
        try:
            self.import_off(self.filepath)
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to import OFF: {str(e)}")
            return {'CANCELLED'}

    def import_off(self, filepath):
        vertices = []
        faces = []
        colors = []  # For COFF files
        is_coff = filepath.lower().endswith('.coff')

        with open(filepath, 'r') as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]

            # Check header
            if not lines[0].startswith(('OFF', 'COFF')):
                raise ValueError("Invalid OFF/COFF file format")
            
            # Read vertex, face, and edge counts
            counts = lines[1].split()
            if len(counts) < 3:
                raise ValueError("Invalid vertex/face/edge counts")
            num_vertices, num_faces, _ = map(int, counts)

            # Read vertices and optional colors
            offset = 2
            for i in range(num_vertices):
                data = lines[offset + i].split()
                if len(data) < 3:
                    raise ValueError("Invalid vertex data")
                vertices.append(tuple(map(float, data[:3])))
                if is_coff and len(data) >= 6:
                    # Normalize RGB to 0-1
                    colors.append(tuple(map(lambda x: float(x)/255.0, data[3:6])))

            # Read faces
            offset += num_vertices
            for i in range(num_faces):
                data = lines[offset + i].split()
                if len(data) < 1:
                    raise ValueError("Invalid face data")
                face_len = int(data[0])
                if face_len < 3:
                    raise ValueError("Face with less than 3 vertices")
                faces.append(tuple(map(int, data[1:face_len+1])))

        # Create mesh
        mesh = bpy.data.meshes.new(name=os.path.basename(filepath))
        mesh.from_pydata(vertices, [], faces)
        mesh.update()

        # Create object
        obj = bpy.data.objects.new(os.path.basename(filepath), mesh)
        bpy.context.collection.objects.link(obj)

        # Add vertex colors for COFF
        if is_coff and colors:
            vcol_layer = mesh.vertex_colors.new(name="Col")
            for poly in mesh.polygons:
                for loop_idx in poly.loop_indices:
                    vertex_idx = mesh.loops[loop_idx].vertex_index
                    if vertex_idx < len(colors):
                        vcol_layer.data[loop_idx].color = (*colors[vertex_idx], 1.0)

class ExportOFF(Operator, ExportHelper):
    """Export OFF file"""
    bl_idname = "export_mesh.off"
    bl_label = "Export OFF"
    filename_ext = ".off"
    filter_glob: StringProperty(default="*.off;*.coff", options={'HIDDEN'})

    def execute(self, context):
        try:
            self.export_off(self.filepath, context)
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to export OFF: {str(e)}")
            return {'CANCELLED'}

    def export_off(self, filepath, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            raise ValueError("No active mesh object selected")

        mesh = obj.data
        is_coff = filepath.lower().endswith('.coff')
        
        # Get vertex colors if COFF
        vcol_layer = None
        if is_coff and mesh.vertex_colors:
            vcol_layer = mesh.vertex_colors.active

        with open(filepath, 'w') as f:
            # Write header
            f.write("COFF\n" if is_coff else "OFF\n")
            
            # Count vertices and faces
            f.write(f"{len(mesh.vertices)} {len(mesh.polygons)} 0\n")

            # Write vertices
            for vert in mesh.vertices:
                if is_coff and vcol_layer:
                    # Get average color for vertex
                    color = [0, 0, 0]
                    count = 0
                    for poly in mesh.polygons:
                        for loop_idx in poly.loop_indices:
                            if mesh.loops[loop_idx].vertex_index == vert.index:
                                col = vcol_layer.data[loop_idx].color
                                color = [c + col[i] for i, c in enumerate(color)]
                                count += 1
                    if count > 0:
                        color = [c/count * 255 for c in color]
                    f.write(f"{vert.co.x} {vert.co.y} {vert.co.z} {int(color[0])} {int(color[1])} {int(color[2])}\n")
                else:
                    f.write(f"{vert.co.x} {vert.co.y} {vert.co.z}\n")

            # Write faces
            for poly in mesh.polygons:
                indices = [str(loop.vertex_index) for loop in mesh.loops[poly.loop_start:poly.loop_start + poly.loop_total]]
                f.write(f"{len(indices)} {' '.join(indices)}\n")

def menu_func_import(self, context):
    self.layout.operator(ImportOFF.bl_idname, text="OFF/COFF (.off/.coff)")

def menu_func_export(self, context):
    self.layout.operator(ExportOFF.bl_idname, text="OFF/COFF (.off/.coff)")

def register():
    bpy.utils.register_class(ImportOFF)
    bpy.utils.register_class(ExportOFF)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ImportOFF)
    bpy.utils.unregister_class(ExportOFF)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
