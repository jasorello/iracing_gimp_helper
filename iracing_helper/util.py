from gi.repository import Gimp

def get_layer(image, layer_name) -> Gimp.Layer:
    """
    Gets the expected layer or throws an exception. Use this for situations
    where the layer's presence is required
    """
    layer = image.get_layer_by_name(layer_name)
    if layer is None:
        message = f'Missing required layer {layer_name}'
        Gimp.message(message)
        raise ConfigurationException(message)
    return layer
    

class ConfigurationException(Exception):
    pass