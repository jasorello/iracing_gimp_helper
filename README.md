# Jason's iRacing Paint Helper for Gimp
This is a Gimp 3.x plugin that has two major functions:

1. Enable quick-exports to iRacing from a paint template, including spec mapping
2. Initialization of an iRacing-supplied template into a format supported by the export step


## Installation
This plugin requires Gimp 3.x. If you're on 2.x, you can try to stumble through using the previous version in [legacy](legacy/iracing_helper.py).

### Steps:

1. Add this directory as a plugin directory in Gimp
    - Edit -> Preferences -> Folders -> Plugin Directories
1. This will add the two functions of the plugin under Tools -> iRacing
1. Optional: Add keyboard shortcuts for the functions (I recommend the export function, at least).
    - Edit -> Keyboard Shortcuts
1. Download the paint template from iRacing for the car you wish to paint.
1. Run the Initialize function from the plugin, which will import the template layers/channels from template.zip
1. Update the META group contents for your environment, this includes values that tell the script where to export your paint so it's found correctly by iRacing

## Usage and How it Works

### Designing a pattern, choosing a color and spec map.
This plugin enables a specific workflow when painting. You design the car's pattern using Red, Green, and Blue colors in the "Livery -> Car Pattern -> Custom Pattern" layer group. 

The Color channels for these will be used to generate Channels which are used to mask the Colors you specify in "Livery -> Paint -> Masks" for each color.

Likewise, these patterns will leverage the spec map for each color channel specified in "Spec Map"

To adjust the pattern, adjust it in RGB. To change the colors, adjust the layers in Masks. To change the reflective properties of each color in the pattern, adjust the layers in the appropriate Spec Map group.

### Decals
Decals should go in "Livery -> Paint -> Decals". They will automatically have a spec layer updated for them so that they stand out from the base design

### Carbon Fiber
Optionally, you can add Blue to "Livery -> Car Pattern -> Carbon Fiber". Anything Blue in these layers will apply a Carbon Fiber pattern to the car.