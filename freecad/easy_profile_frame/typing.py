from typing import TYPE_CHECKING, Any
global PySide
if TYPE_CHECKING:
    import FreeCADGui as Gui
    import Sketcher, Part
    SelectionObject = Gui.SelectionObject
    SketchObject = Sketcher.SketchObject
    Part2DObject = Part.Part2DObject
    Edge = Part.Edge
else:
    SelectionObject = Any
    SketchObject = Any
    Part2DObject = Any
    Edge = Any