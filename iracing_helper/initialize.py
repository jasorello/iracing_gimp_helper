from gi.repository import Gimp, Gio
import os
import sys
from pathlib import Path

from const import *
import util
import zipfile
import tempfile

ARCHIVE_NAME = 'template.zip'
TEMPLATE_NAME = 'template.xcf'

def get_plugin_directory_path() -> str:
    #https://www.gimp-forum.net/Thread-Python-fu-path-of-the-plug-ins-folder
    current_plugin_path = Path(os.path.abspath(sys.argv[0]))
    return current_plugin_path.parent

def load_layers_to_image_from_template(image):
    zf = zipfile.ZipFile(os.path.join(get_plugin_directory_path(), ARCHIVE_NAME))
    with tempfile.TemporaryDirectory() as tempdir:
        zf.extractall(tempdir)
        template_file = get_template_file(tempdir)
        # https://lazka.github.io/pgi-docs/#Gimp-3.0/functions.html#Gimp.file_load_layers
        loaded_layers = Gimp.file_load_layers(Gimp.RunMode.NONINTERACTIVE, image, template_file)
        if not loaded_layers:
            raise util.ConfigurationException(f'Error loading template layers from {tempdir}')
        
        for layer in reversed(loaded_layers):  # Reverse because I want to retain the order but wasn't sure how
            image.insert_layer(layer, None, 0)


def get_template_file(directory):
    parent_dir = get_plugin_directory_path()
    path = os.path.join(parent_dir, directory, TEMPLATE_NAME)
    template_file = Gio.File.new_for_path(path)
    return template_file

def copy_layer(image, layer, layer_group, position):
    layer_copy = layer.copy()
    image.insert_layer(layer_copy, layer_group, position)

def move_spec_parts(image):
    # Move metallic parts
    iracing_layer_group = util.get_layer(image, L_IRACING_METALLIC)
    our_layer_group = util.get_layer(image, L_PARTS_METALLIC)

    copy_layer(image, iracing_layer_group.get_children()[0], our_layer_group, 0)

    # Move roughness parts
    iracing_layer_group = util.get_layer(image, L_IRACING_ROUGHNESS)
    our_layer_group = util.get_layer(image, L_PARTS_ROUGHNESS)
    copy_layer(image, iracing_layer_group.get_children()[0], our_layer_group, 0)
    

def prepare_paint_from_template(image):
    """
    1. Load required layers from Template
    2. Move decals to appropriate paint layer group
    3. Move parts to appropriate spec layer group
    """
    image.undo_freeze()

    load_layers_to_image_from_template(image)

    move_spec_parts(image)


    image.undo_thaw()
    return None