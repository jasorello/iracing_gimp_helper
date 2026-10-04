from gi.repository import Gimp

def get_layer(image, layer_name, required=True) -> Gimp.Layer:
    """
    Gets the expected layer or throws an exception. Use this for situations
    where the layer's presence is required
    """
    layer = image.get_layer_by_name(layer_name)
    if layer is None and required:
        message = f'Missing required layer {layer_name}'
        Gimp.message(message)
        raise ConfigurationException(message)
    return layer

class LayerManager:
    """
    simple abstraction layer for pulling layers from the image
    """
    def __init__(self, image):
        self.image = image

    def layer(self, layer_name:str, required=True) -> Gimp.Layer:
        """
        Gets the expected layer. Throws an exception if it's required and not found
        """
        layer = self.image.get_layer_by_name(layer_name)
        if layer is None and required:
            message = f'Missing required layer {layer_name}'
            Gimp.message(message)
            raise ConfigurationException(message)
        return layer

    def set_visible(self, layer_name: str, visible: bool, required=True):
        """
        helper method for setting visibility for non-required layers
        """
        if layer := self.layer(layer_name=layer_name, required=required):
            layer.set_visible(visible)

    

class ConfigurationException(Exception):
    pass