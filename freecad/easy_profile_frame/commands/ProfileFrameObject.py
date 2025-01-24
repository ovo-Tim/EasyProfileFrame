import FreeCAD as App
from freecad.easy_profile_frame import ICONPATH
import os
from freecad.easy_profile_frame.typing import SketchObject, AppPart, Body
from .utils import GetStored, GetOrCreate

class CustomObjectViewProvider:
    def __init__(self, vobj):
        """Initialize the ViewProvider"""
        vobj.addExtension("Gui::ViewProviderGroupExtensionPython")
        vobj.Proxy = self

    def getIcon(self):
        """Return the icon for this object"""
        return os.path.join(ICONPATH, "MakerWorkbench_Aluproft_Cmd.svg")

class MyExtension():
    def __init__(self,obj):
        obj.addExtension("App::GroupExtensionPython")

class ProfileFrameObject:
    def __init__(self, body):
        """Initialize the custom Object type"""
        body.Proxy = self
        self.Type = "ProfileFrameObject"

        # Add necessary properties
        body.addProperty("App::PropertyString", "Sketch", "EasyProfileFrame", "Sweep sketch").Sketch = ""
        body.addProperty("App::PropertyString", "EdgeName", "EasyProfileFrame", "Edge reference (Sketch:Edge)").EdgeName = ""
        body.addProperty("App::PropertyLength", "OffsetX", "EasyProfileFrame", "Offset in X direction").OffsetX = 0.0
        body.addProperty("App::PropertyLength", "OffsetY", "EasyProfileFrame", "Offset in Y direction").OffsetY = 0.0
        body.addProperty("App::PropertyAngle", "Angle", "EasyProfileFrame", "Rotation angle around Z axis").Angle = 0

        # Initialize state variables
        self._last_offset_x = body.OffsetX.Value
        self._last_offset_y = body.OffsetY.Value
        self._last_angle = body.Angle

        # Set up the ViewObject
        if hasattr(body, "ViewObject"):
            body.ViewObject.Proxy = CustomObjectViewProvider(body.ViewObject)

    def apply_offset_and_rotation(self, sketch, offset_x, offset_y, angle):
        """Apply offset and rotation to the sketch"""
        # Check if OffsetX, OffsetY, or Angle has changed
        if (offset_x == self._last_offset_x and offset_y == self._last_offset_y and angle == self._last_angle):
            print("No change")
            return

        # Convert offsets to a vector
        offset_vector = App.Vector(offset_x, offset_y, 0)

        # Set the offset
        sketch.AttachmentOffset.Base = offset_vector

        # Set the rotation
        rotation = App.Rotation(App.Vector(0, 0, 1), angle)
        sketch.AttachmentOffset.Rotation = rotation

        # Recompute the sketch
        sketch.recompute()

        # Update state variables
        self._last_offset_x = offset_x
        self._last_offset_y = offset_y
        self._last_angle = angle

    def onDocumentRestored(self, obj):
        """Initialize when restoring from a file"""
        obj.Proxy = self
        if hasattr(obj, "ViewObject"):
            obj.ViewObject.Proxy = CustomObjectViewProvider(obj.ViewObject)

    def execute(self, obj):
        """Core method for building the geometry"""
        # Validate necessary properties
        if not obj.Sketch or not obj.EdgeName:
            return

        # Parse the edge reference
        try:
            edge_sketch_name, subedge = obj.EdgeName.split(':')
        except ValueError:
            raise ValueError("Invalid edge name format. Use 'SketchName:EdgeN'")

        # Get or create a copy of the sketch
        sketch: SketchObject = GetStored(obj, App.ActiveDocument.getObject(obj.Sketch), 'sketch')
        edge_sketch: SketchObject = GetStored(obj, App.ActiveDocument.getObject(edge_sketch_name), 'edge_sketch')

        # Apply offset and rotation to the sketch
        self.apply_offset_and_rotation(sketch, obj.OffsetX, obj.OffsetY, obj.Angle)

        # Position the sketch at the start of the edge
        sketch.AttachmentSupport = [(edge_sketch, subedge)]
        sketch.MapMode = 'NormalToEdge'
        sketch.recompute()

        # Perform the sweep
        result_shape = self.sweep(sketch, edge_sketch, subedge, obj, obj.EdgeName)

        # Ensure the geometry is visible
        obj.purgeTouched()

    def sweep(self, sketch: SketchObject, edge_sketch: SketchObject, subedge: str, body: Body, name: str):
        # PartDesign API
        # _t = time.time()
        sweep_obj:Feature = GetOrCreate(f'frame_{name.replace(':', '_')}', 'PartDesign::AdditivePipe', body)
        sweep_obj.Profile = sketch
        sweep_obj.Spine = (edge_sketch, [subedge])
        sweep_obj.recompute()
        # print(f"Sweeping took {time.time() - _t} s")

        edge_sketch.Visibility = False
        sketch.Visibility = False

        return sweep_obj

def CreateProfileFrameBody(SketchName: str, EdgeName: str, doc: App.Document|AppPart = None, name = "ProfileFrameBody"):
    ''' Note: The sketch and edge must be in the current document. '''
    if doc is None:
        doc = App.activeDocument()

    name = name.replace(':', '_')
    # obj = GetOrCreate(name, "PartDesign::FeaturePython", doc)
    obj = doc.getObject(name)
    if obj is None:
        if isinstance(doc, App.Document):
            obj = doc.addObject('PartDesign::FeaturePython', name)
        else:
            obj = doc.newObject('PartDesign::FeaturePython', name)
        # Initialize the object
        ProfileFrameObject(obj)
        MyExtension(obj)
    obj.Sketch = SketchName
    obj.EdgeName = EdgeName
    return obj