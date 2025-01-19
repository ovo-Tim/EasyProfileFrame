import FreeCADGui as Gui
import FreeCAD as App
from FreeCAD import Part
import os
from freecad.easy_profile_frame import ICONPATH, RESSOURCESPATH
from freecad.easy_profile_frame.resources.ui import CreateProfilesBySketchPanel as CreateProfilesBySketchPanelUI
from freecad.easy_profile_frame.typing import SelectionObject, SketchObject, Part2DObject, Edge
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

translate=App.Qt.translate
QT_TRANSLATE_NOOP=App.Qt.QT_TRANSLATE_NOOP
LIB_PATH = os.path.join(RESSOURCESPATH, "PartLib")

def IsAllWires(objects: list[SelectionObject]) -> bool:
    for obj in objects:
        if obj.Object.TypeId == 'Sketcher::SketchObject' or obj.Object.TypeId == 'Part::Part2DObjectPython':
            continue
        sub_objs: list[Part.Shape] = obj.SubObjects
        for subobj in sub_objs:
            if not isinstance(subobj, Part.Edge):
                return False
    return True

def GetAllWireNames(objects: list[SelectionObject]) -> list[str]:
    '''
    This might return an object like 'Sketch' or 'Line' or a subobject like 'Sketch:Edge1'.
    You might need to get subobject by `FreeCAD.ActiveDocument.getObject("Sketch").getSubObject("Edge1")`.
    '''
    wires: list[Part.Edge, SketchObject, Part2DObject] = []
    for obj in objects:
        sub_obj_names: list[str] = obj.SubElementNames
        if (obj.Object.TypeId == 'Sketcher::SketchObject' or obj.Object.TypeId == 'Part::Part2DObjectPython') and sub_obj_names == ():
            # If user directly select a sketch object or a line created by Draft.
            wires.append(obj.Object.Name)
            continue
        for subobjname in sub_obj_names:
            if 'Edge' in subobjname: # Let's hope this won't be a problem.
                wires.append(f'{obj.Object.Name}:{subobjname}')
    return wires

class CreateProfilesBySketchWidget(QWidget, CreateProfilesBySketchPanelUI.Ui_Form):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.radioBtn_custom.toggled.connect(self.on_radioBtn_custom_toggled)
        self.radioBtn_lib.toggled.connect(self.on_radioBtn_lib_toggled)
        self.lib_files.currentTextChanged.connect(self.update_sketch_list)
        self.frame_wire_selector_add.clicked.connect(self.add_wires)
        self.frame_wire_selector_rm.clicked.connect(self.remove_wires)
        self.frame_wire_selector_show.clicked.connect(self.show_all_wires)
        self.custom_sketch_select_btn.clicked.connect(self.select_sketch)

        self.loaded_sketches = []
        self.custom_sketch = None
        self._current_lib: App.Document = None

        self.read_lib_list()

    def on_radioBtn_custom_toggled(self, checked):
        if checked:
            self.custom_group.setEnabled(True)
            self.lib_group.setEnabled(False)

    def on_radioBtn_lib_toggled(self, checked):
        if checked:
            self.lib_group.setEnabled(True)
            self.custom_group.setEnabled(False)

    def read_lib_list(self):
        App.Console.PrintLog(f"Reading library from { LIB_PATH } \n")
        files = [f for f in os.listdir(LIB_PATH) if f.endswith('.FCStd')]
        self.lib_files.clear()
        self.lib_files.addItems(files)

    def read_lib(self, path):
        App.Console.PrintLog(f"Reading library from { path } \n")
        if self._current_lib is not None:
            App.closeDocument(self._current_lib.Name)
        current_doc = App.ActiveDocument
        self._current_lib = App.openDocument(path, True)
        App.setActiveDocument(current_doc.Name)
        return self._current_lib

    def update_sketch_list(self, file_name):
        file_path = os.path.join(LIB_PATH, file_name)

        try:
            doc = self.read_lib(file_path)
            self.loaded_sketches = [obj.Label for obj in doc.Objects if obj.isDerivedFrom("Sketcher::SketchObject")]
            self.lib_sketches.clear()
            self.lib_sketches.addItems(self.loaded_sketches)
        except Exception as e:
            App.Console.PrintError(f"Error reading library: {e} \n")

    def cleanup(self):
        if self._current_lib is not None:
            App.closeDocument(self._current_lib.Name)

    def closeEvent(self, event):
        self.cleanup()
        return super().closeEvent(event)

    def add_wires(self):
        selected_objects: list[SelectionObject] = Gui.Selection.getSelectionEx()
        self.wire_list.addItems(GetAllWireNames(selected_objects))
        self.remove_repetitions()

    def remove_wires(self):
        for item in self.wire_list.selectedItems():
            self.wire_list.takeItem(self.wire_list.row(item))

    def show_all_wires(self):
        selected: list[str] = [self.wire_list.item(i).text() for i in range(self.wire_list.count())]
        for obj in selected:
            Gui.Selection.addSelection(App.ActiveDocument.Name, *obj.split(':'))

    def remove_repetitions(self):
        selected: list[str] = [self.wire_list.item(i).text() for i in range(self.wire_list.count())]
        selected = list(set(selected))
        selected = [obj for obj in selected if (':' not in obj) or (obj.split(':')[0] not in selected)]
        self.wire_list.clear()
        self.wire_list.addItems(selected)

    def select_sketch(self):
        selected_object: SelectionObject = Gui.Selection.getSelection()[0]
        if selected_object.TypeId == 'Sketcher::SketchObject':
            self.custom_sketch = selected_object
            self.custom_sketch_label.setText(selected_object.Label)

class CreateProfilesBySketchPanel:
    '''
    All annoying stuff has been done in the CreateProfilesBySketchWidget, this class only cares about drawing.
    '''
    redraw = Signal()
    def __init__(self):
        self.form = CreateProfilesBySketchWidget()
        self.redraw.connect(self._draw)
        self.form.add_wires()

    def cleanup(self):
        self.form.close()

    def _draw(self):
        pass

    def draw(self, sketch: SketchObject, lines: list[Edge], joint_type: str):
        pass

class CreateProfilesCommandBase:

    def IsActive(self):
        selected_objects: list[SelectionObject] = Gui.Selection.getSelectionEx()
        # Check if all selected objects are edges
        if not IsAllWires(selected_objects):
            return False

        return selected_objects != []

class CreateProfilesBySketchCommand(CreateProfilesCommandBase):
    """Create Profiles from wires"""

    def GetResources(self):
        return {
                "Pixmap"  : os.path.join(ICONPATH, "MakerWorkbench_Aluproft_Cmd.svg"),
                "Accel"   : "Shift+P",
                "MenuText": "Create Profile",
                "ToolTip" : "Create new profiles from wires"}

    def Activated(self):
        self.panel = CreateProfilesBySketchPanel()
        # Gui.Selection.addObserver(panel)
        # Gui.Selection.addSelectionGate('SELECT Part::Feature SUBELEMENT Edge')

        Gui.Control.showDialog(self.panel)

    def Deactivated(self):
        self.panel.cleanup()
        del self.panel

Gui.addCommand("EPF_CreateProfilesBySketcher", CreateProfilesBySketchCommand())