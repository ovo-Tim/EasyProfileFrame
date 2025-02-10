from typing import TYPE_CHECKING, Any

global PySide
if TYPE_CHECKING:
    import FreeCADGui as Gui
    import FreeCAD as App
    import Sketcher, Part, PartDesign

    SelectionObject = Gui.SelectionObject
    SketchObject = Sketcher.SketchObject
    Part2DObject = Part.Part2DObject
    Edge = Part.Edge
    Feature = PartDesign.Feature
    Quantity = App.Base.Quantity
    Vertex = Part.Vertex

    class Body(PartDesign.Body):
        def addObject(self, obj: App.DocumentObject) -> list[App.DocumentObject]: ...
        def removeObject(self, obj: App.DocumentObject) -> list[App.DocumentObject]: ...
        def getObject(self, name: str) -> Feature: ...

    AppPart = App.Part
else:
    SelectionObject = Any
    SketchObject = Any
    Part2DObject = Any
    Edge = Any
    Feature = Any
    Body = Any
    AppPart = Any
    Quantity = Any
    Vertex = Any
