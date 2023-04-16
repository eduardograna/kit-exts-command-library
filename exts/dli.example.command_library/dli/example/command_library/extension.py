import omni.ext
import omni.ui as ui
import omni.kit.commands # New
import omni.usd # New
from typing import List # New


# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[dli.example.command_library] some_public_function was called with x: ", x)
    return x ** x


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class DliExampleCommand_libraryExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[dli.example.command_library] dli example command_library startup")

        self._count = 0

        self._window = ui.Window("My Window", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                label = ui.Label("")

                def on_click():
                    selection = get_selection()
                    print(selection)
                    import omni.kit.commands
                    omni.kit.commands.execute('ScaleIncrement', prim_paths=selection)

                with ui.HStack():
                    ui.Button("Scale Selected", clicked_fn=on_click)

    def on_shutdown(self):
        print("[dli.example.command_library] dli example command_library shutdown")


class ScaleIncrement(omni.kit.commands.Command):
    ATTR = 'xformOp:scale'

    def __init__(self, prim_paths: List[str]):
        self.stage = omni.usd.get_context().get_stage()
        self.prim_paths = prim_paths
        self.data = {}
        for path in self.prim_paths:
            data = {}
            data['prim'] = self.stage.GetPrimAtPath(path)
            data['scale_attribute'] = data['prim'].GetAttribute(self.ATTR)
            data['old_scale'] = data['scale_attribute'].Get()
            data['new_scale'] = tuple(x + 1 for x in data['old_scale'])
            self.data[path] = data

    def do(self):
        self.set_scale('new_scale')

    def undo(self):
        self.set_scale('old_scale')

    def set_scale(self, scale_name):
        for p, data in self.data.items():
            data['scale_attribute'].Set(data[scale_name])


def get_selection() -> List[str]:
    """Get the list of currently selected prims"""
    return omni.usd.get_context().get_selection().get_selected_prim_paths()
