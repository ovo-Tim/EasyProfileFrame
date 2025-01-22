import FreeCADGui as Gui
import FreeCAD as App
from FreeCAD import Part
import os
from freecad.easy_profile_frame import ICONPATH, RESSOURCESPATH
from freecad.easy_profile_frame.resources.ui import CreateProfilesBySketchPanel as CreateProfilesBySketchPanelUI
from freecad.easy_profile_frame.typing import SelectionObject, SketchObject, Part2DObject, Edge, Feature, Body, AppPart
from PySide6.QtWidgets import QWidget, QButtonGroup
from PySide6.QtCore import Signal
import Part
import time
import math

translate=App.Qt.translate
QT_TRANSLATE_NOOP=App.Qt.QT_TRANSLATE_NOOP
LIB_PATH = os.path.join(RESSOURCESPATH, "PartLib")

def IsAllWires(objects: list[SelectionObject]) -> bool:
    for obj in objects:
        if obj.Object.TypeId == 'Sketcher::SketchObject' or obj.Object.TypeId == 'Part::Part2DObjectPython':
            continue
        sub_objs: tuple[Part.Shape] = obj.SubObjects
        for subobj in sub_objs:
            if not isinstance(subobj, Part.Edge):
                return False
    return True

def GetAllWireNames(objects: list[SelectionObject]) -> list[str]:
    '''
    This might return an object like 'Sketch' or 'Line' or a subobject like 'Sketch:Edge1'.
    You might need to get subobject by `FreeCAD.ActiveDocument.getObject("Sketch").getSubObject("Edge1")`.
    '''
    wires: list[str] = []
    for obj in objects:
        sub_obj_names: tuple[str, ...] = obj.SubElementNames
        if (obj.Object.TypeId == 'Sketcher::SketchObject' or obj.Object.TypeId == 'Part::Part2DObjectPython') and sub_obj_names == ():
            # If user directly select a sketch object or a line created by Draft.
            wires.append(obj.Object.Name)
            continue
        for subobjname in sub_obj_names:
            if 'Edge' in subobjname: # Let's hope this won't be a problem.
                wires.append(f'{obj.Object.Name}:{subobjname}')
    return wires

def GetSubEdges(names: list[str]) -> list[str]:
    '''
    Return {name: Part.Edge}.
    '''
    objs = []
    for n in names:
        if ':' in n:
            parent, subobj = n.split(':')
            obj = App.ActiveDocument.getObject(parent).getSubObject(subobj)
            if isinstance(obj, Part.Edge):
                objs.append(n)
        else:
            for i, edge in enumerate(App.ActiveDocument.getObject(n).Shape.Edges):
                objs.append(f'{n}:Edge{i+1}')
    return objs

def GetOrCreate(name: str, obj_type: str, doc: App.Document|Body|AppPart):
    obj = doc.getObject(name)
    print(f'Getting object {name} Result: {obj}')
    if obj is not None:
        return obj
    if isinstance(doc, App.Document):
        return doc.addObject(obj_type, name)
    else:
        return doc.newObject(obj_type, name)

def CopyObj(source: App.DocumentObject|Feature, target: Body, check_existing: bool = True):
    '''
    Copy an object across documents.
    '''
    if check_existing:
        existing_obj = target.getObject(source.Name)
        if existing_obj is not None:
            return existing_obj
    doc = target.Document
    obj:App.DocumentObject|Feature = doc.copyObject(source)
    obj = target.addObject(obj)[0]
    obj.Label = source.Label
    return obj

class CreateProfilesBySketchWidget(QWidget, CreateProfilesBySketchPanelUI.Ui_Form):
    redraw = Signal()
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
        self.realtime_update.toggled.connect(self.enable_realtime_update)
        self.UPDATE_LIST = [self.auto_align,
                       self.no_processing,
                       self.miter_cut,
                       self.reserved,
                       self.fillet
                       ]
        self.update_btn_group = QButtonGroup(self)
        for btn in self.UPDATE_LIST:
            self.update_btn_group.addButton(btn)
        self.enable_realtime_update(self.realtime_update.isChecked())

        self.custom_sketch: SketchObject|None = None
        self.current_lib: App.Document|None = None

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
        if self.current_lib is not None:
            App.closeDocument(self.current_lib.Name)
        current_doc = App.ActiveDocument
        self.current_lib = App.openDocument(path, True)
        App.setActiveDocument(current_doc.Name)
        return self.current_lib

    def update_sketch_list(self, file_name):
        file_path = os.path.join(LIB_PATH, file_name)

        try:
            doc = self.read_lib(file_path)
            self.lib_sketches.clear()
            self.lib_sketches.addItems([obj.Label for obj in doc.Objects if obj.isDerivedFrom("Sketcher::SketchObject")])
        except Exception as e:
            App.Console.PrintError(f"Error reading library: {e} \n")

    def cleanup(self):
        if self.current_lib is not None:
            App.closeDocument(self.current_lib.Name)

    def closeEvent(self, event):
        self.cleanup()
        return super().closeEvent(event)

    def add_wires(self):
        selected_objects: list[SelectionObject] = Gui.Selection.getSelectionEx()
        self.wire_list.addItems(GetAllWireNames(selected_objects))
        self.remove_repetitions()
        if self.realtime_update.isChecked():
            self.redraw.emit()

    def remove_wires(self):
        for item in self.wire_list.selectedItems():
            self.wire_list.takeItem(self.wire_list.row(item))
        if self.realtime_update.isChecked():
            self.redraw.emit()

    def show_all_wires(self):
        AllItems: list[str] = [self.wire_list.item(i).text() for i in range(self.wire_list.count())]
        for obj in AllItems:
            Gui.Selection.addSelection(App.ActiveDocument.Name, *obj.split(':'))

    def remove_repetitions(self):
        AllItems: list[str] = [self.wire_list.item(i).text() for i in range(self.wire_list.count())]
        AllItems = list(set(AllItems))
        AllItems = [obj for obj in AllItems if (':' not in obj) or (obj.split(':')[0] not in AllItems)]
        self.wire_list.clear()
        self.wire_list.addItems(AllItems)

    def select_sketch(self):
        selected_object: SketchObject = Gui.Selection.getSelection()[0]
        if selected_object.TypeId == 'Sketcher::SketchObject':
            self.custom_sketch = selected_object
            self.custom_sketch_label.setText(selected_object.Name)
            if self.realtime_update.isChecked():
                self.redraw.emit()
        else:
            App.Console.PrintError(f"{selected_object.Name} is not a sketch. \n")

    def enable_realtime_update(self, checked):
        if checked:
            self.lib_sketches.currentTextChanged.connect(self.redraw)
            self.update_btn_group.buttonToggled.connect(self.redraw)
        else:
            self.lib_sketches.currentTextChanged.disconnect(self.redraw)
            self.update_btn_group.buttonToggled.disconnect(self.redraw)

class CreateProfilesBySketchPanel:
    '''
    All annoying stuff has been done in the CreateProfilesBySketchWidget, this class only cares about drawing.
    '''
    def __init__(self):
        self.form = CreateProfilesBySketchWidget()
        self.form.redraw.connect(self._draw)
        self.form.add_wires()
        self.drawed: dict[str, Body] = {}
        self.my_part = None

        # self.body:Body = App.ActiveDocument.addObject('PartDesign::Body', 'Body')
        self.part: AppPart = App.ActiveDocument.addObject('App::Part', 'Part')
        self.copied_sketche: SketchObject|None = None

        self._draw()

    def cleanup(self):
        self.form.close()

    def sweep(self, sketch: SketchObject, name: str):
        '''
        This function will automatically move and rotate the sketch to the start point of the line and sweep it.
        '''
        edge_sketch_name, subedge = name.split(':')

        # Create new body
        body:Body = GetOrCreate(f'frame_{name.replace(':', '_')}_body', 'PartDesign::Body', self.part)

        # Copy sketch and the line
        _t = time.time()

        # if self.copied_sketche is not None:
        #     if self.copied_sketche.Label != sketch.Label:
        #         self.body.removeObject(self.copied_sketche)

        #         self.copied_sketche = CopyObj(sketch, self.body)
        # else:
        #     self.copied_sketche = CopyObj(sketch, self.body)
        # sketch = CopyObj(self.copied_sketche, self.body)
        sketch = CopyObj(sketch, body)
        edge_sketch = App.ActiveDocument.getObject(edge_sketch_name)
        edge_sketch = CopyObj(edge_sketch, body)
        print(f"Copying sketch took {time.time() - _t} s")

        # Move and rotate the sketch to the start point of the line
        _t = time.time()
        line = edge_sketch.getSubObject(subedge)
        sketch.AttachmentSupport = [(edge_sketch, subedge)]
        edge_vector = line.tangentAt(0)
        z_axis = App.Vector(0, 0, 1)
        rotation_axis = z_axis.cross(edge_vector)
        rotation_angle = math.degrees(z_axis.getAngle(edge_vector)) + 90
        sketch.AttachmentOffset = App.Placement(App.Vector(0, 0, 0), App.Rotation(rotation_axis, rotation_angle))
        sketch.MapMode = 'NormalToEdge'
        print(f"Moving and rotating sketch took {time.time() - _t} s")

        # Part API, don't work well.
        # sweep = Part.Wire(line).makePipeShell([sketch.Shape.Wires[0]], True, False, 2)
        # name = name.replace(':', '_')
        # sweep_obj:Part.Feature = GetOrCreate(name, 'Part::Sweep', self.body)
        # sweep_obj.Shape = sweep

        # PartDesign API
        _t = time.time()
        sweep_obj:Feature = GetOrCreate(f'frame_{name.replace(':', '_')}', 'PartDesign::AdditivePipe', body)
        sweep_obj.Profile = sketch
        sweep_obj.Spine = (edge_sketch, [subedge])
        sweep_obj.recompute()
        print(f"Sweeping took {time.time() - _t} s")

        edge_sketch.Visibility = False
        sketch.Visibility = False

        self.drawed[name] = body

    def _draw(self):
        # Get the sketch
        sketch: SketchObject|None = None
        if self.form.radioBtn_lib.isChecked():
            sketch = self.form.current_lib.getObjectsByLabel(self.form.lib_sketches.currentText())[0]
            print(self.form.current_lib, self.form.lib_sketches.currentText())
        elif self.form.radioBtn_custom.isChecked():
            sketch = self.form.current_lib.getObjectsByLabel(self.form.custom_sketch)[0]

        # Get the lines
        lineNames: list[str] = [self.form.wire_list.item(i).text() for i in range(self.form.wire_list.count())]
        lines: list[str] = GetSubEdges(lineNames)

        print(f"Drawing { lines } on { sketch }")
        if sketch is None:
            return
        if self.form.no_processing.isChecked():
            self.draw(sketch, lines, 'NoProcessing')

    def draw(self, sketch: SketchObject, lines: list[str], joint_type: str, remove_old: bool = True):
        if remove_old:
            remove_list = set(self.drawed.keys()) - set(lines)
            print(f"Drawed: {self.drawed.keys()} Drawing: {lines} Remove: {remove_list}")
            for name in remove_list:
                self.drawed[name].removeObjectsFromDocument()
                App.ActiveDocument.removeObject(self.drawed[name].Name)
                self.drawed.pop(name)
        if joint_type == 'NoProcessing':
            for line in lines:
                self.sweep(sketch, line)

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

        Gui.Control.showDialog(self.panel)

    # def Deactivated(self):
    #     self.panel.cleanup()
    #     del self.panel

Gui.addCommand("EPF_CreateProfilesBySketcher", CreateProfilesBySketchCommand())