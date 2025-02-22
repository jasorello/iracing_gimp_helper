#!/usr/bin/env python

import gtk
from gimpfu import *

def remask_layers_from_channel(image, layers, channel):
    for layer_name in layers:
        # check if the layer already has a mask and remove it
        layer = pdb.gimp_image_get_layer_by_name(image, layer_name)
        if pdb.gimp_layer_get_mask(layer):
            pdb.gimp_layer_remove_mask(layer, 1)
        # uses the currently active channel so we need to unset the current one
        pdb.gimp_image_unset_active_channel(image)
        # and then set the one we want that we just created
        pdb.gimp_image_set_active_channel(image, channel)
        mask = pdb.gimp_layer_create_mask(layer, ADD_MASK_CHANNEL)
        pdb.gimp_layer_add_mask(layer, mask)

def export_as_tga(image, path, filename):
    export_image = pdb.gimp_image_duplicate(image)
    layer = pdb.gimp_image_merge_visible_layers(export_image, CLIP_TO_IMAGE)
    pdb.gimp_file_save(export_image, layer, path + '/' + filename + '.tga', '?')
    pdb.gimp_image_delete(export_image)


def regenerate_from_pattern(image):
    # image = gimp.image_list()[0]
    # pdb.gimp_message("Hello World, This Message Looks Like An Error And/Or Warning")
    # Disable the undo history so we don't pollute the heck outta it
    pdb.gimp_image_undo_freeze(image)
    active_layer = pdb.gimp_image_get_active_layer(image)

    # Figure out what's already visible (helpful for having the wireframe on while building a pattern)
    visibility_dict = get_high_level_layer_visibility(image)

    # show pattern
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Paintable Area'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Car Patterns'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Custom Pattern'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Spec Map'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Turn Off Before Exporting TGA'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Paint'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Carbon Fiber Pattern Left'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Carbon Fiber Pattern Right'), False)
    
    red_channel = pdb.gimp_image_get_channel_by_name(image, 'Red Channel - Auto')
    if red_channel:
        pdb.gimp_image_remove_channel(image, red_channel)
        
    green_channel = pdb.gimp_image_get_channel_by_name(image, 'Green Channel - Auto')
    if green_channel:
        pdb.gimp_image_remove_channel(image, green_channel)

    blue_channel = pdb.gimp_image_get_channel_by_name(image, 'Blue Channel - Auto')
    if blue_channel:
        pdb.gimp_image_remove_channel(image, blue_channel)

    decal_channel = pdb.gimp_image_get_channel_by_name(image, 'Decal Alpha Channel - Auto')
    if decal_channel:
        pdb.gimp_image_remove_channel(image, decal_channel)

    cf_left_channel = pdb.gimp_image_get_channel_by_name(image, 'Carbon Fiber Left Channel - Auto')
    if cf_left_channel:
        pdb.gimp_image_remove_channel(image, cf_left_channel)

    cf_right_channel = pdb.gimp_image_get_channel_by_name(image, 'Carbon Fiber Right Channel - Auto')
    if cf_right_channel:
        pdb.gimp_image_remove_channel(image, cf_right_channel)

    # recreate color channels
    red_channel = pdb.gimp_channel_new_from_component(image, 0, "Red Channel - Auto")
    pdb.gimp_image_insert_channel(image, red_channel, None, 0)
    pdb.gimp_item_set_color_tag(red_channel, 6)

    green_channel = pdb.gimp_channel_new_from_component(image, 1, "Green Channel - Auto")
    pdb.gimp_image_insert_channel(image, green_channel, None, 0)
    pdb.gimp_item_set_color_tag(green_channel, 2)

    blue_channel = pdb.gimp_channel_new_from_component(image, 2, "Blue Channel - Auto")
    pdb.gimp_image_insert_channel(image, blue_channel, None, 0)
    pdb.gimp_item_set_color_tag(blue_channel, 1)

    # recreate carbon fiber alpha channels
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Custom Pattern'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Carbon Fiber Pattern Left'), True)

    cf_left_channel = pdb.gimp_channel_new_from_component(image, 2, "Carbon Fiber Left Channel - Auto")
    pdb.gimp_image_insert_channel(image, cf_left_channel, None, 0)
    pdb.gimp_item_set_color_tag(cf_left_channel, 4)

    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Carbon Fiber Pattern Left'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Carbon Fiber Pattern Right'), True)

    cf_right_channel = pdb.gimp_channel_new_from_component(image, 2, "Carbon Fiber Right Channel - Auto")
    pdb.gimp_image_insert_channel(image, cf_right_channel, None, 0)
    pdb.gimp_item_set_color_tag(cf_right_channel, 4)

    # Get decal alpha channel
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Car Patterns'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Paint'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Decals'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Pit Stuff'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Carbon Fiber'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Masks'), False)

    decal_channel = pdb.gimp_channel_new_from_component(image, 5, "Decal Alpha Channel - Auto")
    pdb.gimp_image_insert_channel(image, decal_channel, None, 0)
    pdb.gimp_item_set_color_tag(decal_channel, 3)


    # update layer masks based on updated channels
    red_layers = ['Paint Red Mask', 'Spec Red Mask']
    if pdb.gimp_image_get_layer_by_name(image, 'Spec Red Mask Pattern Base') is not None:
        red_layers.append('Spec Red Mask Pattern Base')
    remask_layers_from_channel(image, red_layers, red_channel)

    green_layers = ['Paint Green Mask', 'Spec Green Mask']
    if pdb.gimp_image_get_layer_by_name(image, 'Spec Green Mask Pattern Base') is not None:
        green_layers.append('Spec Green Mask Pattern Base')
    remask_layers_from_channel(image, green_layers, green_channel)

    blue_layers = ['Paint Blue Mask', 'Spec Blue Mask']
    if pdb.gimp_image_get_layer_by_name(image, 'Spec Blue Mask Pattern Base') is not None:
        blue_layers.append('Spec Blue Mask Pattern Base')
    remask_layers_from_channel(image, blue_layers, blue_channel)

    decal_layers = ['Spec Decal Mask']
    remask_layers_from_channel(image, decal_layers, decal_channel)

    left_cf_layers = ['Spec Left Carbon Fiber', 'Left Carbon Fiber']
    remask_layers_from_channel(image, left_cf_layers, cf_left_channel)

    right_cf_layers = ['Spec Right Carbon Fiber', 'Right Carbon Fiber']
    remask_layers_from_channel(image, right_cf_layers, cf_right_channel)

    # Get iracing paint directory and car number from META group
    # (these are just expected to exist)
    meta_layer = pdb.gimp_image_get_layer_by_name(image, 'META')
    _, child_ids = pdb.gimp_item_get_children(meta_layer)
    path = gimp.Item.from_id(child_ids[0]).name
    number = gimp.Item.from_id(child_ids[1]).name
  
    show_paint(image)
    export_as_tga(image, path, 'car_' + number)

    pdb.gimp_message('updated paint .tga')

    show_spec(image)
    export_as_tga(image, path, 'car_spec_' + number)

    pdb.gimp_message('updated spec .tga')

    set_high_level_layer_visibility(image, visibility_dict)

    pdb.gimp_image_set_active_layer(image, active_layer)
    pdb.gimp_image_undo_thaw(image)
    # show_pattern(image)

def get_high_level_layer_visibility(image):
    high_level_layers = [
        'Paintable Area', 
        'Decals',
        'Masks',
        'Pit Stuff',
        'Carbon Fiber',
        'Carbon Fiber Pattern Left',
        'Carbon Fiber Pattern Right',
        'Paint',
        'Car Patterns',
        'Custom Pattern',
        'Spec Map',
        'Turn Off Before Exporting TGA'
    ]
    visibility_dict = dict()
    for layer_name in high_level_layers:
        visibility_dict[layer_name] = pdb.gimp_item_get_visible(pdb.gimp_image_get_layer_by_name(image, layer_name))

    return visibility_dict

def set_high_level_layer_visibility(image, visibility_dict):
    for layer_name, visibility in visibility_dict.viewitems():
        pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, layer_name), visibility)
      


def show_paint(image):
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Paintable Area'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Decals'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Masks'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Pit Stuff'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Carbon Fiber'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Paint'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Car Patterns'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Custom Pattern'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Spec Map'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Turn Off Before Exporting TGA'), False)

def show_spec(image):
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Paintable Area'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Car Patterns'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Custom Pattern'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Spec Map'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Turn Off Before Exporting TGA'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Paint'), False)

def show_pattern(image):
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Paintable Area'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Car Patterns'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Custom Pattern'), True)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Spec Map'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Turn Off Before Exporting TGA'), False)
    pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, 'Paint'), False)


# see -> http://www.gimp.org/docs/python/
register(
    #name
    "iracing_reset_channels",

    #blurb
    "Resets paint based on the RGB pattern",

    #help
    "Resets paint based on the RGB pattern",

    #author
    "jason <jasonrbreen@gmail.com>",

    #copyright
    "jason <jasonrbreen@gmail.com>",

    #date
    "2023",

    #menupath
    "Update Paint From Pattern",

    #imagetypes (use * for all, leave blank for none)
    "",

    #params
    [
        (PF_IMAGE, "image", "Input image", None),

    ],

    #results
    [],

    #function (to call)
    regenerate_from_pattern,
 
    #this can be included this way or the menu value can be directly prepended to the menupath
    menu = "<Image>/Tools/iRacing/")

main()