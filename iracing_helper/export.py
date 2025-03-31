from gi.repository import Gimp, Gio
from const import *
import traceback

HIGH_LEVEL_LAYERS = [
    L_PAINTABLE_AREA,
    L_DECALS,
    L_MASKS,
    L_PIT_STUFF,
    L_CARBON_FIBER,
    L_CARBON_FIBER_PATTERN_LEFT,
    L_CARBON_FIBER_PATTERN_RIGHT,
    L_PAINT,
    L_CAR_PATTERNS,
    L_CUSTOM_PATTERN,
    L_SPEC_MAP,
    L_TURN_OFF_BEFORE_EXPORT
]

CHANNELS_TO_COLOR_TAGS = {
    C_RED: Gimp.ColorTag.RED, 
    C_GREEN: Gimp.ColorTag.GREEN,
    C_BLUE: Gimp.ColorTag.BLUE,
    C_DECAL_ALPHA: Gimp.ColorTag.YELLOW,
    C_CARBON_LEFT: Gimp.ColorTag.ORANGE,
    C_CARBON_RIGHT: Gimp.ColorTag.ORANGE,
}

def get_high_level_layer_visibility(image):
    visibility_dict = {}
    for layer_name in HIGH_LEVEL_LAYERS:
        layer = image.get_layer_by_name(layer_name)

        if layer is None:
            message = f'Missing required layer {layer_name}'
            Gimp.message(message)
            raise ExportException(message)

        visibility_dict[layer_name] = layer.get_visible()

    return visibility_dict



def set_high_level_layer_visibility(image, visibility_dict):
    for layer_name, visibility in visibility_dict.items():
        image.get_layer_by_name(layer_name).set_visible(visibility)


def show_paint(image):
    image.get_layer_by_name(L_SPEC_MAP).set_visible(False)
    image.get_layer_by_name(L_TURN_OFF_BEFORE_EXPORT).set_visible(False)
    image.get_layer_by_name(L_PAINTABLE_AREA).set_visible(True)

    image.get_layer_by_name(L_PAINT).set_visible(True)
    image.get_layer_by_name(L_DECALS).set_visible(True)
    image.get_layer_by_name(L_MASKS).set_visible(True)
    image.get_layer_by_name(L_PIT_STUFF).set_visible(True)
    image.get_layer_by_name(L_CARBON_FIBER).set_visible(True)

    image.get_layer_by_name(L_CAR_PATTERNS).set_visible(False)
    image.get_layer_by_name(L_CUSTOM_PATTERN).set_visible(False)

def show_spec(image):
    image.get_layer_by_name(L_SPEC_MAP).set_visible(True)
    image.get_layer_by_name(L_TURN_OFF_BEFORE_EXPORT).set_visible(False)
    image.get_layer_by_name(L_PAINTABLE_AREA).set_visible(False)

    image.get_layer_by_name(L_PAINT).set_visible(False)

    image.get_layer_by_name(L_CAR_PATTERNS).set_visible(False)
    image.get_layer_by_name(L_CUSTOM_PATTERN).set_visible(False)


def show_pattern(image):
    image.get_layer_by_name(L_SPEC_MAP).set_visible(False)
    image.get_layer_by_name(L_TURN_OFF_BEFORE_EXPORT).set_visible(False)
    image.get_layer_by_name(L_PAINTABLE_AREA).set_visible(True)

    image.get_layer_by_name(L_PAINT).set_visible(False)
    image.get_layer_by_name(L_CAR_PATTERNS).set_visible(True)
    image.get_layer_by_name(L_CUSTOM_PATTERN).set_visible(True)
    image.get_layer_by_name(L_CARBON_FIBER_PATTERN_LEFT).set_visible(False)
    image.get_layer_by_name(L_CARBON_FIBER_PATTERN_RIGHT).set_visible(False)

def show_decals(image):
    image.get_layer_by_name(L_SPEC_MAP).set_visible(False)
    image.get_layer_by_name(L_TURN_OFF_BEFORE_EXPORT).set_visible(False)
    image.get_layer_by_name(L_PAINTABLE_AREA).set_visible(True)

    image.get_layer_by_name(L_PAINT).set_visible(True)
    image.get_layer_by_name(L_DECALS).set_visible(True)
    image.get_layer_by_name(L_PIT_STUFF).set_visible(False)
    image.get_layer_by_name(L_CARBON_FIBER).set_visible(False)
    image.get_layer_by_name(L_MASKS).set_visible(False)

    image.get_layer_by_name(L_CAR_PATTERNS).set_visible(False)
    image.get_layer_by_name(L_CUSTOM_PATTERN).set_visible(False)
    image.get_layer_by_name(L_CARBON_FIBER_PATTERN_LEFT).set_visible(False)
    image.get_layer_by_name(L_CARBON_FIBER_PATTERN_RIGHT).set_visible(False)


def regenerate_channel_masks(image, channel_definition: dict):
    Gimp.message(str(channel_definition))
    for channel_name, channel_mask in channel_definition.items():
        Gimp.message(channel_name)
        channel = image.get_channel_by_name(channel_name)
        if channel:
            image.remove_channel(channel)
        channel = Gimp.Channel.new_from_component(image, channel_mask, channel_name)
        channel.set_color_tag(CHANNELS_TO_COLOR_TAGS[channel_name])
        image.insert_channel(channel, None, 0)


def remask_layers_from_channel(image: Gimp.Image, layer_names: list, channel_name: str):
    channel = image.get_channel_by_name(channel_name)
    for layer_name in layer_names:
        layer = image.get_layer_by_name(layer_name)
        if layer.get_mask():
            layer.remove_mask(1)
        image.unset_active_channel()
        image.set_selected_channels([channel])
        mask = layer.create_mask(Gimp.AddMaskType.CHANNEL)
        layer.add_mask(mask)

def regenerate_channels(image):
    # Regenerate channels for pattern based on color in patterns
    Gimp.message('regenerating Pattern')
    show_pattern(image)
    pattern_channels_to_mask = {
        C_RED: Gimp.ChannelType.RED,
        C_GREEN: Gimp.ChannelType.GREEN,
        C_BLUE: Gimp.ChannelType.BLUE,
    }
    regenerate_channel_masks(image, pattern_channels_to_mask)

    # Regenerate channels for carbon fiber from blue channel in patterns
    Gimp.message('regenerating CF')
    image.get_layer_by_name(L_CUSTOM_PATTERN).set_visible(False)
    image.get_layer_by_name(L_CARBON_FIBER_PATTERN_LEFT).set_visible(True)
    regenerate_channel_masks(
        image,
        {C_CARBON_LEFT: Gimp.ChannelType.BLUE},
    )

    image.get_layer_by_name(L_CARBON_FIBER_PATTERN_LEFT).set_visible(False)
    image.get_layer_by_name(L_CARBON_FIBER_PATTERN_RIGHT).set_visible(True)
    regenerate_channel_masks(
        image,
        {C_CARBON_RIGHT: Gimp.ChannelType.BLUE},
    )

    # Regenerate channels for decals from alpha channel in decals
    Gimp.message('regenerating Decals')
    show_decals(image)
    regenerate_channel_masks(
        image,
        {C_DECAL_ALPHA: Gimp.ChannelType.ALPHA}, # alpha
    )

    # Update layer masks based on updated channels
    red_layers = [L_RED_MASK, L_RED_SPEC]
    if image.get_layer_by_name(L_RED_SPEC_PATTERN) is not None:
        red_layers.append(L_RED_SPEC_PATTERN)
    remask_layers_from_channel(image, red_layers, C_RED)

    green_layers = [L_GREEN_MASK, L_GREEN_SPEC]
    if image.get_layer_by_name(L_GREEN_SPEC_PATTERN) is not None:
        green_layers.append(L_GREEN_SPEC_PATTERN)
    remask_layers_from_channel(image, green_layers, C_GREEN)

    blue_layers = [L_BLUE_MASK, L_BLUE_SPEC]
    if image.get_layer_by_name(L_BLUE_SPEC_PATTERN) is not None:
        blue_layers.append(L_BLUE_SPEC_PATTERN)
    remask_layers_from_channel(image, blue_layers, C_BLUE)

    remask_layers_from_channel(image, [L_DECAL_SPEC], C_DECAL_ALPHA)
    remask_layers_from_channel(image, [L_CF_LEFT_MASK, L_CF_LEFT_SPEC], C_CARBON_LEFT)
    remask_layers_from_channel(image, [L_CF_RIGHT_MASK, L_CF_RIGHT_SPEC], C_CARBON_RIGHT)


def export_as_tga(image, path, filename):
    export_image = image.duplicate()
    export_image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
    full_path = path + '\\' + filename + '.tga'
    output_file = Gio.File.new_for_path(full_path)
    Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, export_image, output_file)
    export_image.delete()


def export_to_iracing(image):
    # Pull export info from META layer
    meta_layer = image.get_layer_by_name(L_META)
    children = meta_layer.get_children()
    path = children[0].get_name()
    number = children[1].get_name()
    Gimp.message(f'{path=}, {number=}')

    Gimp.message('exporting car paint')
    show_paint(image)
    export_as_tga(image, path, f'car_{number}')

    Gimp.message('exporting car specmap')
    show_spec(image)
    export_as_tga(image, path, f'car_spec_{number}')


def regenerate_from_pattern(image):
    step = 'init'
    try:
        # Disable the undo history so we don't pollute the heck outta it
        step = 'freezing'
        image.undo_freeze()

        step = 'getting active layers'
        active_layers = image.get_selected_layers()

        step = 'getting current layer visibility'
        visibility_dict = get_high_level_layer_visibility(image)

        step = 'regenerating channel masks and applying to layers'
        regenerate_channels(image)

        step = 'exporting'
        export_to_iracing(image)

        step = 'resetting layer visibility'
        set_high_level_layer_visibility(image, visibility_dict)

        step = 'resetting active layers'
        if active_layers:
            image.set_selected_layers(active_layers)

        step ='thawing'
        image.undo_thaw()

        Gimp.message('done!')

    except Exception as e:
        Gimp.message(f'died in {step}')
        Gimp.message(str(e))
        Gimp.message(traceback.format_exc())

class ExportException(Exception):
    pass