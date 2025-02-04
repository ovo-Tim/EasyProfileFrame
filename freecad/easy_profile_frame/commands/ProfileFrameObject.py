import FreeCAD as App
from freecad.easy_profile_frame import ICONPATH
from FreeCAD import Units as FCUnits
import os
from freecad.easy_profile_frame.typing import SketchObject, AppPart, Body, Feature, Edge
from .utils import GetStored, GetExistent
import Part
import math

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
    FAST_SWEEP = True # Use Pad instead of Sweep when process straight line
    def __init__(self, body:Feature):
        """Initialize the custom Object type"""
        body.Proxy = self
        self.Type = "ProfileFrameObject"

        # Add properties
        body.addProperty("App::PropertyString", "Sketch", "EasyProfileFrame", "Sweep sketch").Sketch = ""
        body.addProperty("App::PropertyString", "EdgeName", "EasyProfileFrame", "Edge reference (Sketch:Edge)").EdgeName = ""
        body.addProperty("App::PropertyLength", "OffsetX", "EasyProfileFrame", "Offset in X direction").OffsetX = 0.0
        body.addProperty("App::PropertyLength", "OffsetY", "EasyProfileFrame", "Offset in Y direction").OffsetY = 0.0
        body.addProperty("App::PropertyAngle", "Angle", "EasyProfileFrame", "Rotation angle around Z axis").Angle = 0
        body.addProperty("App::PropertyLength", "Length", "EasyProfileFrame", "This property isn't included chamfer",
                         read_only=True).Length = 0
        body.addProperty("App::PropertyAngle", "ChamferAngleL", "EasyProfileFrame", "Chamfer angle of the left side. Can only be multiples of 90").ChamferAngleL = 0
        body.addProperty("App::PropertyLength", "ChamferLengthL", "EasyProfileFrame", "Chamfer length of the left side",
                         read_only=True).ChamferLengthL = 0.0
        body.addProperty("App::PropertyInteger", "ChamferDirectionL", "EasyProfileFrame", "Chamfer direction of the left side, 1~4").ChamferDirectionL = 1
        body.addProperty("App::PropertyAngle", "ChamferAngleR", "EasyProfileFrame", "Chamfer angle of the right side. Can only be multiples of 90").ChamferAngleR = 0
        body.addProperty("App::PropertyLength", "ChamferLengthR", "EasyProfileFrame", "Chamfer length of the right side",
                         read_only=True).ChamferLengthR = 0.0
        body.addProperty("App::PropertyInteger", "ChamferDirectionR", "EasyProfileFrame", "Chamfer direction of the right side, 1~4").ChamferDirectionR = 1

        # Initialize state variables
        self._last_offset_x = body.OffsetX
        self._last_offset_y = body.OffsetY
        self._last_angle = body.Angle

        # Set up the ViewObject
        if hasattr(body, "ViewObject"):
            body.ViewObject.Proxy = CustomObjectViewProvider(body.ViewObject)

    def apply_offset_and_rotation(self, sketch, offset_x, offset_y, angle):
        """Apply offset and rotation to the sketch"""
        # Check if OffsetX, OffsetY, or Angle has changed
        if (offset_x == self._last_offset_x and offset_y == self._last_offset_y and angle == self._last_angle):
            # print("No change")
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
        sketchL = GetStored(obj, App.ActiveDocument.getObject(obj.Sketch), 'sketchL')
        edge_sketch: SketchObject = GetStored(obj, App.ActiveDocument.getObject(edge_sketch_name), 'edge_sketch')

        # Apply offset and rotation to the sketch
        self.apply_offset_and_rotation(sketchL, obj.OffsetX, obj.OffsetY, obj.Angle)

        # Position the sketch at the start of the edge
        sketchL.AttachmentSupport = [(edge_sketch, subedge)]
        sketchL.MapMode = 'NormalToEdge'
        sketchL.recompute()

        # Perform the sweep
        if self.FAST_SWEEP:
            edge:Edge = edge_sketch.getSubObject(subedge)
            if isinstance(edge.Curve, (Part.Line, Part.LineSegment)): # It's a straight line
                print("Straight line, fast sweep")
                baseObj = self.pad(sketchL, edge.Length, obj, obj.EdgeName, reversed=True)
            else:
                baseObj = self.sweep(sketchL, edge_sketch, subedge, obj, obj.EdgeName)
        else:
            baseObj = self.sweep(sketchL, edge_sketch, subedge, obj, obj.EdgeName)

        obj.Length = FCUnits.Quantity(edge_sketch.getSubObject(subedge).Length)

        # Chamfer
        if obj.ChamferAngleL > 0:
            self.create_chamfer(sketchL, obj.ChamferAngleL, obj.ChamferDirectionL, obj, (edge_sketch, subedge), (edge_sketch, 'Vertex1'), baseObj)

        # Ensure the geometry is visible
        obj.purgeTouched()

    def pad(self, sketch: SketchObject, length: float, body:Body, name:str, reversed=False, baseFeature=None):
        pad_obj = GetExistent(f'frame_{name.replace(':', '_')}', 'PartDesign::Pad', body)
        pad_obj.Profile = sketch
        pad_obj.Length = length
        pad_obj.Reversed = reversed
        pad_obj.BaseFeature = baseFeature
        pad_obj.recompute()

        sketch.Visibility = False
        if baseFeature is not None:
            baseFeature.Visibility = False
        return pad_obj

    def sweep(self, sketch: SketchObject, edge_sketch: SketchObject, subedge: str, body: Body, name: str):
        # PartDesign API
        # _t = time.time()
        sweep_obj:Feature = GetExistent(f'frame_{name.replace(':', '_')}', 'PartDesign::AdditivePipe', body)
        sweep_obj.Profile = sketch
        sweep_obj.Spine = (edge_sketch, [subedge])
        sweep_obj.recompute()
        # print(f"Sweeping took {time.time() - _t} s")

        edge_sketch.Visibility = False
        sketch.Visibility = False

        return sweep_obj

    def __getstate__(self):
        state = {'_last_offset_x': self._last_offset_x.toStr(),
                 '_last_offset_y': self._last_offset_y.toStr(),
                 '_last_angle': self._last_angle.toStr()
                 }
        return state

    def __setstate__(self, state):
        self._last_offset_x = FCUnits.Quantity(state['_last_offset_x'])
        self._last_offset_y = FCUnits.Quantity(state['_last_offset_y'])
        self._last_angle = FCUnits.Quantity(state['_last_angle'])

    def create_chamfer(self, sketch: SketchObject, angle: float, direction: int, body: Body, edge: tuple[Part.Feature, str], point: tuple[Part.Feature, str], baseFeature):
        '''
        sketch: The sketch used to extend the profile.
        direction: 1~4
        point: The point used to attach the cutting sketch.
        '''
        # print(f"Creating chamfer, angle: {angle}, direction: {direction}")
        boundBox = sketch.Shape.BoundBox
        xy_extremes = (boundBox.XMin, boundBox.XMax, boundBox.YMin, boundBox.YMax)

        # Extend tan(angle)*width/2
        # TODO: It's better to set math expression instead of approximate value, but I guess nobody cares.(I'm too lazy to do it.)
        if direction in (1, 2):
            width = xy_extremes[1] - xy_extremes[0]
        else:
            width = xy_extremes[3] - xy_extremes[2]
        width = abs(width)
        extended_length = abs(math.tan(math.radians(angle)) * width / 2)
        # print(f"Extended length: {extended_length}")
        obj = self.pad(sketch, extended_length, body, "Chamfer", baseFeature=baseFeature)

        # Draw a cutting sketch
        chamfer_sketch: SketchObject = GetExistent('chamferCuttingSketch', 'Sketcher::SketchObject', body)
        chamfer_sketch.AttachmentSupport = [edge, point]
        chamfer_sketch.MapMode = 'NormalToEdge'
        chamfer_sketch.AttachmentOffset = App.Placement(App.Vector(0,0,0),  App.Rotation(0, 90, direction*90))
        chamfer_sketch.Visibility = False
        chamfer_sketch.recompute()

        tx = extended_length
        ty = width / 2
        triangle = [(-tx, ty), (-tx, -ty), (tx, ty)]
        chamfer_sketch.addGeometry(Part.LineSegment(App.Vector(triangle[0][0], triangle[0][1], 0),
                                    App.Vector(triangle[1][0], triangle[1][1], 0)), False)
        chamfer_sketch.addGeometry(Part.LineSegment(App.Vector(triangle[1][0], triangle[1][1], 0),
                                    App.Vector(triangle[2][0], triangle[2][1], 0)), False)
        chamfer_sketch.addGeometry(Part.LineSegment(App.Vector(triangle[2][0], triangle[2][1], 0),
                                    App.Vector(triangle[0][0], triangle[0][1], 0)), False)
        chamfer_sketch.recompute()

        # Create Pocket
        pocket_obj = GetExistent(f'Chamfer', 'PartDesign::Pocket', body)
        pocket_obj.Profile = chamfer_sketch
        pocket_obj.AlongSketchNormal = 1
        pocket_obj.Type = 1
        pocket_obj.Midplane = 1
        pocket_obj.BaseFeature = obj
        pocket_obj.recompute()

        obj.Visibility = False

def CreateProfileFrameBody(SketchName: str, EdgeName: str, doc: App.Document|AppPart = None, name = "ProfileFrameBody"):
    ''' Note: The sketch and edge must be in the current document. '''
    if doc is None:
        doc = App.activeDocument()

    name = name.replace(':', '_')
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