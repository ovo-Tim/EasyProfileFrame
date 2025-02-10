import FreeCAD as App
import FreeCADGui as Gui
from freecad.easy_profile_frame.typing import SelectionObject
import os
from freecad.easy_profile_frame import ICONPATH

class GenerateBomCommand:
    def init_sheet(self, sheet):
        sheet.Label = "BOM of frame"

        sheet.set("A1", "Profile Label")
        sheet.set("B1", "Profile model")
        sheet.set("C1", "Profile length")
        sheet.set("D1", "Left chamfer angle")
        sheet.set("E1", "Right chamfer angle")

    def GetObjects(self, selected_objects:list[SelectionObject]):
        objs = []
        for obj in selected_objects:
            if hasattr(obj.Object, "Proxy") and hasattr(obj.Object.Proxy, "Type") and obj.Object.Proxy.Type == "ProfileFrameObject":
                objs.append(obj)
            if obj.Object.TypeId == "App::Part":
                for subobj in obj.Object.Group:
                    if hasattr(subobj, "Proxy") and hasattr(subobj.Proxy, "Type") and subobj.Proxy.Type == "ProfileFrameObject":
                        objs.append(subobj)
        if not objs:
            for obj in App.ActiveDocument.Objects:
                if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type == "ProfileFrameObject":
                    objs.append(obj)
        return objs

    def Activated(self):
        sheet = App.ActiveDocument.addObject("Spreadsheet::Sheet", "BOM of frame")
        self.init_sheet(sheet)

        selected_objects: list = Gui.Selection.getSelectionEx()
        objs = self.GetObjects(selected_objects)
        for i, obj in enumerate(objs):
            sheet.set("A{}".format(i + 2), obj.Label)
            sheet.set("B{}".format(i + 2), obj.Proxy.sketchLableL)
            sheet.set("C{}".format(i + 2), obj.Length.toStr())
            sheet.set("D{}".format(i + 2), obj.ChamferAngleR.toStr())
            sheet.set("E{}".format(i + 2), obj.ChamferAngleL.toStr())

        sheet.recompute()

    def GetResources(self):
        return {
                "Pixmap"  : os.path.join(ICONPATH, "Workbench_Spreadsheet.svg"),
                "Accel"   : "Shift+P",
                "MenuText": "Generate BOM",
                "ToolTip" : "Generate BOM of frame"}

Gui.addCommand("EPF_GenerateBom", GenerateBomCommand())