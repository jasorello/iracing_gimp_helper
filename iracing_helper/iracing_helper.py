#!/usr/bin/env python3
import sys

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi

from gi.repository import GLib

import export

EXPORT = "export-to-iracing"
INITIALIZE = "initialize-from-template"

class IracingHelper (Gimp.PlugIn):
    def do_query_procedures(self):
        return [ EXPORT, INITIALIZE]

    def do_set_i18n (self, name):
        return False

    def do_create_procedure(self, name):

        if name == EXPORT:
            procedure = Gimp.ImageProcedure.new(self, name,
                                                Gimp.PDBProcType.PLUGIN,
                                                self.export, None)
            procedure.set_documentation(f"{EXPORT}: Export the current paint and spec layers",
                                "Helper functions to help jasorello's iracing painting workflow",
                                name)
            procedure.set_menu_label(name)

        elif name == INITIALIZE:
            procedure = Gimp.ImageProcedure.new(self, name,
                                                Gimp.PDBProcType.PLUGIN,
                                                self.initialize, None)
            procedure.set_documentation(f"{INITIALIZE}: Initialize a default iracing paint to prepare for export",
                                "Helper functions to help jasorello's iracing painting workflow",
                                name)
            procedure.set_menu_label(name)

        
        procedure.set_image_types("*")

        procedure.add_menu_path('<Image>/Tools/iRacing/')

        procedure.set_attribution("Jason Breen", "Jason Breen", "2025")

        return procedure
    
    def export(self, procedure, run_mode, image, drawables, config, run_data):
        export.regenerate_from_pattern(image)

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


    def initialize(self, procedure, run_mode, image, drawables, config, run_data):

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(IracingHelper.__gtype__, sys.argv)