from gi.repository import Gimp, Gio
from const import *
import util

REQUIRED_HIGH_LEVEL_LAYERS = [
    L_PAINTABLE_AREA,
    L_DECALS,
    L_MASKS,
    L_PIT_STUFF,
    L_PAINT,
    L_CAR_PATTERNS,
    L_CUSTOM_PATTERN,
    L_SPEC_MAP,
    L_TURN_OFF_BEFORE_EXPORT
]
OPTIONAL_HIGH_LEVEL_LAYERS = [
    L_CARBON_FIBER,
    L_CARBON_FIBER_PATTERN_LEFT,
    L_CARBON_FIBER_PATTERN_RIGHT,
]

CHANNELS_TO_COLOR_TAGS = {
    C_RED: Gimp.ColorTag.RED,
    C_GREEN: Gimp.ColorTag.GREEN,
    C_BLUE: Gimp.ColorTag.BLUE,
    C_DECAL_ALPHA: Gimp.ColorTag.YELLOW,
    C_CARBON_LEFT: Gimp.ColorTag.ORANGE,
    C_CARBON_RIGHT: Gimp.ColorTag.ORANGE,
}

def get_high_level_layer_visibility(lm:util.LayerManager):
    """
    Gets the top level layer group visibility so it can be returned to the original state
    after export
    """
    visibility_dict = {}
    for layer_name in REQUIRED_HIGH_LEVEL_LAYERS:
        layer = lm.layer(layer_name)
        if layer:
            visibility_dict[layer_name] = layer.get_visible()

    return visibility_dict



def set_high_level_layer_visibility(lm: util.LayerManager, visibility_dict):
    for layer_name, visibility in visibility_dict.items():
        lm.set_visible(layer_name, visibility)


def show_paint(lm: util.LayerManager):
    """
    Enable/disable layers so that only paint-specific layers are visible
    """
    lm.set_visible(L_SPEC_MAP, False)
    lm.set_visible(L_TURN_OFF_BEFORE_EXPORT, False)
    lm.set_visible(L_PAINTABLE_AREA, True)

    lm.set_visible(L_PAINT, True)
    lm.set_visible(L_DECALS, True)
    lm.set_visible(L_MASKS, True)
    lm.set_visible(L_PIT_STUFF, True)
    lm.set_visible(L_CARBON_FIBER, True, required=False)

    lm.set_visible(L_CAR_PATTERNS, False)
    lm.set_visible(L_CUSTOM_PATTERN, False)

def show_spec(lm: util.LayerManager):
    """
    Enable/disable layers so that only spec-map layers are visible
    """
    lm.set_visible(L_SPEC_MAP, True)
    lm.set_visible(L_TURN_OFF_BEFORE_EXPORT, False)
    lm.set_visible(L_PAINTABLE_AREA, False)

    lm.set_visible(L_PAINT, False)

    lm.set_visible(L_CAR_PATTERNS, False)
    lm.set_visible(L_CUSTOM_PATTERN, False)


def show_pattern(lm: util.LayerManager):
    """
    Enable/disable layers so that only pattern layers are visible
    """

    lm.set_visible(L_SPEC_MAP, False)
    lm.set_visible(L_TURN_OFF_BEFORE_EXPORT, False)
    lm.set_visible(L_PAINTABLE_AREA, True)

    lm.set_visible(L_PAINT, False)

    lm.set_visible(L_CAR_PATTERNS, True)
    lm.set_visible(L_CUSTOM_PATTERN, True)

    lm.set_visible(L_CARBON_FIBER_PATTERN_LEFT, False, required=False)
    lm.set_visible(L_CARBON_FIBER_PATTERN_RIGHT, False, required=False)

def show_decals(lm: util.LayerManager):
    """
    Enable/disable layers so that only decal layers are visible
    """
    lm.set_visible(L_SPEC_MAP, False)
    lm.set_visible(L_TURN_OFF_BEFORE_EXPORT, False)
    lm.set_visible(L_PAINTABLE_AREA, True)

    lm.set_visible(L_PAINT, True)
    lm.set_visible(L_DECALS, True)
    lm.set_visible(L_MASKS, False)
    lm.set_visible(L_PIT_STUFF, False)

    lm.set_visible(L_CARBON_FIBER, False, required=False)

    lm.set_visible(L_CAR_PATTERNS, False)
    lm.set_visible(L_CUSTOM_PATTERN, False)
    lm.set_visible(L_CARBON_FIBER_PATTERN_LEFT, False, required=False)

    lm.set_visible(L_CARBON_FIBER_PATTERN_RIGHT, False, required=False)


def regenerate_channel_masks(image: Gimp.Image, channel_definition: dict):
    for channel_name, channel_mask in channel_definition.items():
        channel = image.get_channel_by_name(channel_name)
        if channel:
            image.remove_channel(channel)
        channel = Gimp.Channel.new_from_component(image, channel_mask, channel_name)
        channel.set_color_tag(CHANNELS_TO_COLOR_TAGS[channel_name])
        image.insert_channel(channel, None, 0)


def remask_layers_from_channel(image: Gimp.Image,
                               lm: util.LayerManager,
                               layer_names: list,
                               channel_name: str):
    """
    Updates the layer mask for each in layer_names based on the channel_name
    """
    channel = image.get_channel_by_name(channel_name)
    for layer_name in layer_names:
        layer = lm.layer(layer_name)
        if layer.get_mask():
            layer.remove_mask(1)
        image.unset_active_channel()
        image.set_selected_channels([channel])
        mask = layer.create_mask(Gimp.AddMaskType.CHANNEL)
        layer.add_mask(mask)

def regenerate_channels(image: Gimp.Image, lm: util.LayerManager):
    """
    Regenerates the mask channels based on the content in your design layers
    """
    # Regenerate channels for pattern based on color in patterns
    Gimp.message('regenerating Pattern')
    show_pattern(lm)
    pattern_channels_to_mask = {
        C_RED: Gimp.ChannelType.RED,
        C_GREEN: Gimp.ChannelType.GREEN,
        C_BLUE: Gimp.ChannelType.BLUE,
    }
    regenerate_channel_masks(image, pattern_channels_to_mask)

    # Regenerate channels for carbon fiber from blue channel in patterns
    if lm.layer(L_CARBON_FIBER_PATTERN_LEFT, required=False):
        Gimp.message('regenerating CF')
        lm.layer(L_CUSTOM_PATTERN).set_visible(False)
        lm.layer(L_CARBON_FIBER_PATTERN_LEFT).set_visible(True)
        regenerate_channel_masks(
            image,
            {C_CARBON_LEFT: Gimp.ChannelType.BLUE},
        )

        lm.layer(L_CARBON_FIBER_PATTERN_LEFT).set_visible(False)
        lm.layer(L_CARBON_FIBER_PATTERN_RIGHT).set_visible(True)
        regenerate_channel_masks(
            image,
            {C_CARBON_RIGHT: Gimp.ChannelType.BLUE},
        )

    # Regenerate channels for decals from alpha channel in decals
    Gimp.message('regenerating Decals')
    show_decals(lm)
    regenerate_channel_masks(
        image,
        {C_DECAL_ALPHA: Gimp.ChannelType.ALPHA}, # alpha
    )

    # Update layer masks based on updated channels
    red_layers = [L_RED_MASK, L_RED_SPEC]
    if image.get_layer_by_name(L_RED_SPEC_PATTERN) is not None:
        red_layers.append(L_RED_SPEC_PATTERN)
    remask_layers_from_channel(image, lm, red_layers, C_RED)

    green_layers = [L_GREEN_MASK, L_GREEN_SPEC]
    if image.get_layer_by_name(L_GREEN_SPEC_PATTERN) is not None:
        green_layers.append(L_GREEN_SPEC_PATTERN)
    remask_layers_from_channel(image, lm, green_layers, C_GREEN)

    blue_layers = [L_BLUE_MASK, L_BLUE_SPEC]
    if image.get_layer_by_name(L_BLUE_SPEC_PATTERN) is not None:
        blue_layers.append(L_BLUE_SPEC_PATTERN)
    remask_layers_from_channel(image, lm, blue_layers, C_BLUE)

    Gimp.message('we gonna make it?')
    remask_layers_from_channel(image, lm, [L_DECAL_SPEC], C_DECAL_ALPHA)
    if lm.layer(L_CF_LEFT_MASK, required=False):
        Gimp.message('Made it here')
        remask_layers_from_channel(image, lm, [L_CF_LEFT_MASK, L_CF_LEFT_SPEC], C_CARBON_LEFT)
    if lm.layer(L_CF_RIGHT_MASK, required=False):
        remask_layers_from_channel(image, lm, [L_CF_RIGHT_MASK, L_CF_RIGHT_SPEC], C_CARBON_RIGHT)


def export_as_tga(image: Gimp.Image, path, filename):
    """
    Exports the image to the path/filename in tga format
    """
    export_image = image.duplicate()
    export_image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
    full_path = path + '\\' + filename + '.tga'
    output_file = Gio.File.new_for_path(full_path)
    Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, export_image, output_file)
    export_image.delete()


def export_to_iracing(image: Gimp.Image, lm: util.LayerManager):
    """
    Exports the paint and spec layer to .tga for iracing
    """
    # Pull export info from META layer
    meta_layer = lm.layer(L_META)
    children = meta_layer.get_children()
    path = children[0].get_name()
    number = children[1].get_name()

    Gimp.message('exporting car paint')
    show_paint(lm)
    export_as_tga(image, path, f'car_{number}')

    Gimp.message('exporting car specmap')
    show_spec(lm)
    export_as_tga(image, path, f'car_spec_{number}')


def regenerate_from_pattern(image: Gimp.Image):
    """
    Regenerates pattern and layer masks based on your design and then exports
    to iRacing based on the configuration specified in the META layer
    """
    # Disable the undo history so we don't pollute the heck outta it
    image.undo_freeze()

    active_layers = image.get_selected_layers()
    lm = util.LayerManager(image=image)

    visibility_dict = get_high_level_layer_visibility(lm)

    regenerate_channels(image, lm)

    export_to_iracing(image, lm)

    set_high_level_layer_visibility(lm, visibility_dict)

    if active_layers:
        image.set_selected_layers(active_layers)

    image.undo_thaw()

