import atexit
import os
import shutil
import sys


# The script assumes that is in running inside a Blender environment
import addon_utils
import bpy

if __name__ == "__main__":
    print("\nBOOTLOADING...")

    # Install and enable addons in Blender
    for i in range(len(sys.argv)):
        modpath = sys.argv[i]
        modname, _ = os.path.splitext(os.path.basename(modpath))
        bpy.ops.preferences.addon_install(filepath=modpath)
        bpy.ops.preferences.addon_enable(module=modname)

        # Find the place that Blender copied the module into when the addon was installed
        bl_modpath: str = None
        for mod in addon_utils.modules():
            if mod.__name__ == modname:
                bl_modpath = mod.__file__
                break

        atexit.register(lambda path: shutil.rmtree(os.path.dirname(path)), bl_modpath)

    print("\n############ LOAD SUCCESSFUL ############\n")
