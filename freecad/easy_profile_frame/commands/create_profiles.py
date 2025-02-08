import FreeCADGui as Gui
import FreeCAD as App
import os
from freecad.easy_profile_frame import ICONPATH, RESSOURCESPATH
from freecad.easy_profile_frame.resources.ui import CreateProfilesBySketchPanel as CreateProfilesBySketchPanelUI
from freecad.easy_profile_frame.typing import SelectionObject, SketchObject, Body, AppPart, Edge, Vertex
from PySide6.QtWidgets import QWidget, QButtonGroup
from PySide6.QtCore import Signal
from FreeCAD import Units as FCUnits
from .ProfileFrameObject import CreateProfileFrameBody
from .utils import GetAllWireNames, GetSubEdges, IsAllWires, calculate_edges_angle

translate=App.Qt.translate
QT_TRANSLATE_NOOP=App.Qt.QT_TRANSLATE_NOOP
LIB_PATH = os.path.join(RESSOURCESPATH, "PartLib")

def getObjectFromName(name:str, doc:App.Document|Body):
    obj, subname = name.split(':')
    return doc.getObject(obj).getSubObject(subname)

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
        self.rotate_btn.clicked.connect(self.rotate)
        self.UPDATE_LIST = [self.auto_alignA,
                       self.auto_alignB,
                       self.no_processing,
                       self.miter_cut,
                       ]
        self.update_btn_group = QButtonGroup(self)
        for btn in self.UPDATE_LIST:
            self.update_btn_group.addButton(btn)
        self.enable_realtime_update(self.realtime_update.isChecked())

        self.custom_sketch: SketchObject|None = None
        self.current_lib: App.Document|None = None
        self.setup_offsetBox()

        self.angle = 0
        self.offset = (FCUnits.Quantity("0 mm"), FCUnits.Quantity("0 mm"))

        self.read_lib_list()

    def rotate(self):
        self.angle += 90
        self.angle %= 360
        self.angle_dis.setText(f"Angle: {self.angle}°")
        self.redraw.emit()

    def setup_offsetBox(self):
        self.offsetBoxX = Gui.UiLoader().createWidget("Gui::QuantitySpinBox")
        self.offsetBoxY = Gui.UiLoader().createWidget("Gui::QuantitySpinBox")
        self.offsetBoxX.setProperty("unit","mm")
        self.offsetBoxY.setProperty("unit","mm")
        self.X_offset.addWidget(self.offsetBoxX)
        self.Y_offset.addWidget(self.offsetBoxY)
        self.offsetBoxX.valueChanged.connect(self._offset_changed)
        self.offsetBoxY.valueChanged.connect(self._offset_changed)

    def _offset_changed(self, _):
        self.offset = (self.offsetBoxX.property("value"), self.offsetBoxY.property("value"))
        self.redraw.emit()

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
        self.form.add_wires()
        self.drawed: dict[str, Body] = {}

        # self.body:Body = App.ActiveDocument.addObject('PartDesign::Body', 'Body')
        self.part: AppPart = App.ActiveDocument.addObject('App::Part', 'Part')

        self._draw()
        self.form.redraw.connect(self._draw)

    def cleanup(self):
        self.form.close()

    def _draw(self):
        # Get the sketch
        sketch: SketchObject|None = None
        if self.form.radioBtn_lib.isChecked():
            sketch = self.form.current_lib.getObjectsByLabel(self.form.lib_sketches.currentText())[0]
        elif self.form.radioBtn_custom.isChecked():
            sketch = self.form.current_lib.getObjectsByLabel(self.form.custom_sketch)[0]

        # Get the lines
        lineNames: list[str] = [self.form.wire_list.item(i).text() for i in range(self.form.wire_list.count())]
        lines: list[str] = GetSubEdges(lineNames)

        if sketch is None:
            return
        if self.form.no_processing.isChecked():
            self.draw(sketch, lines, 'NoProcessing')
        elif self.form.miter_cut.isChecked():
            self.draw(sketch, lines, 'MiterCut')

    def set_offset(self, obj):
        # Set offset and rotation
        obj.OffsetX = self.form.offsetBoxX.property("value")
        obj.OffsetY = self.form.offsetBoxY.property("value")
        obj.Angle = self.form.angle

    def no_processing(self, sketch: SketchObject, lines: list[str]):
        for name in lines:
            # Create new body
            obj = CreateProfileFrameBody(sketch, name, self.part, f'Frame_{name}')
            self.drawed[name] = obj
            self.set_offset(obj)
            obj.recompute()

    def interact_vertex(self, vertex1, vertex2) -> tuple[Vertex, int, int]|None:
        points1 = [i.Point for i in vertex1]
        points2 = [i.Point for i in vertex2]
        for j, p in enumerate(points1):
            for k, p2 in enumerate(points2):
                if p == p2: return (p, j, k)

    def miter_cut(self, sketch: SketchObject, lines: list[str]):
        self.no_processing(sketch, lines)
        for i, line1N in enumerate(lines):
            for line2N in lines[i+1:]:
                line1_obj: Edge = getObjectFromName(line1N, App.ActiveDocument)
                line2_obj: Edge = getObjectFromName(line2N, App.ActiveDocument)
                # intersections = line1_obj.Curve.intersectCC(line2_obj.Curve)
                # intersections= [i.toShape().Point for i in intersections]
                interact_vertex = self.interact_vertex(line1_obj.Vertexes, line2_obj.Vertexes)
                if interact_vertex is None:
                    continue

                chamfer_angle = calculate_edges_angle(line1_obj, line2_obj)/2
                App.Console.PrintMessage(f"Create chamfer at {interact_vertex[0]}. Angle: {chamfer_angle}° \n")
                setattr(self.drawed[line1N], f"ChamferAngle{'R' if interact_vertex[1] else 'L'}", chamfer_angle)
                setattr(self.drawed[line2N], f"ChamferAngle{'R' if interact_vertex[2] else 'L'}", chamfer_angle)

                self.drawed[line1N].recompute()
                self.drawed[line2N].recompute()

    def draw(self, sketch: SketchObject, lines: list[str], joint_type: str, remove_old: bool = True):
        if remove_old:
            remove_list = set(self.drawed.keys()) - set(lines)
            for name in remove_list:
                self.drawed[name].removeObjectsFromDocument()
                App.ActiveDocument.removeObject(self.drawed[name].Name)
                self.drawed.pop(name)

        if joint_type == 'NoProcessing':
            self.no_processing(sketch, lines)
        elif joint_type == 'MiterCut':
            self.miter_cut(sketch, lines)

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