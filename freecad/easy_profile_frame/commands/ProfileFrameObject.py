import FreeCAD as App
from freecad.easy_profile_frame import ICONPATH
from FreeCAD import Units as FCUnits
import os
from freecad.easy_profile_frame.typing import SketchObject, AppPart, Body, Feature, Edge
from .utils import GetExistent, CopyObj
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

class ProfileFrameObject:
    def __init__(self, obj:Feature):
        """Initialize the custom Object type"""
        obj.Proxy = self
        self.Type = "ProfileFrameObject"

        # Add properties
        obj.addProperty("App::PropertyString", "Sketch", "EasyProfileFrame", "Sweep sketch").Sketch = ""
        obj.addProperty("App::PropertyString", "EdgeName", "EasyProfileFrame", "Edge reference (Sketch:Edge)").EdgeName = ""
        obj.addProperty("App::PropertyLength", "OffsetX", "EasyProfileFrame", "Offset in X direction").OffsetX = 0.0
        obj.addProperty("App::PropertyLength", "OffsetY", "EasyProfileFrame", "Offset in Y direction").OffsetY = 0.0
        obj.addProperty("App::PropertyAngle", "Angle", "EasyProfileFrame", "Rotation angle around Z axis").Angle = 0
        obj.addProperty("App::PropertyLength", "Length", "EasyProfileFrame", "This property isn't included chamfer",
                         read_only=True).Length = 0
        obj.addProperty("App::PropertyAngle", "ChamferAngleL", "EasyProfileFrame", "Chamfer angle of the left side. Can only be multiples of 90").ChamferAngleL = 0
        obj.addProperty("App::PropertyLength", "ChamferLengthL", "EasyProfileFrame", "Chamfer length of the left side",
                         read_only=True).ChamferLengthL = 0.0
        obj.addProperty("App::PropertyInteger", "ChamferDirectionL", "EasyProfileFrame", "Chamfer direction of the left side, 1~4").ChamferDirectionL = 1
        obj.addProperty("App::PropertyLength", "ExtendedLengthL", "EasyProfileFrame", "Extended length of the left side. \
                        (When Chanfer Angle is set, this property will be determined autmaticallyy)").ExtendedLengthL = 0.0

        obj.addProperty("App::PropertyAngle", "ChamferAngleR", "EasyProfileFrame", "Chamfer angle of the right side. Can only be multiples of 90").ChamferAngleR = 0
        obj.addProperty("App::PropertyLength", "ChamferLengthR", "EasyProfileFrame", "Chamfer length of the right side",
                         read_only=True).ChamferLengthR = 0.0
        obj.addProperty("App::PropertyInteger", "ChamferDirectionR", "EasyProfileFrame", "Chamfer direction of the right side, 1~4").ChamferDirectionR = 1
        obj.addProperty("App::PropertyLength", "ExtendedLengthR", "EasyProfileFrame", "Extended length of the right side. \
                        (When Chanfer Angle is set, this property will be determined automatically)").ExtendedLengthR = 0.0

        # Initialize state variables(Needs to be stored when the document is saved)
        self._last_offset_x = obj.OffsetX
        self._last_offset_y = obj.OffsetY
        self._last_offset_z = FCUnits.Quantity(0)
        self._last_angle = obj.Angle
        self.chamfer_sketch_cache:list = [None, None]
        self.sketchLableL = None
        self.sketchR:tuple[str, str]|None = None # (Label, Name)

        obj.addExtension('Part::AttachExtensionPython')
        obj.addExtension("App::GroupExtensionPython")

        # Set up the ViewObject
        if hasattr(obj, "ViewObject"):
            obj.ViewObject.Proxy = CustomObjectViewProvider(obj.ViewObject)

    def apply_offset_and_rotation(self, obj, offset_x, offset_y, angle, offset_z=FCUnits.Quantity(0)):
        """Apply offset and rotation to the sketch"""
        # Check if OffsetX, OffsetY, or Angle has changed
        if (offset_x == self._last_offset_x and offset_y == self._last_offset_y and angle == self._last_angle and offset_z == self._last_offset_z):
            # print("No change")
            return

        # Convert offsets to a vector
        offset_vector = App.Vector(offset_x, offset_y, offset_z)

        # Set the offset
        obj.AttachmentOffset.Base = offset_vector

        # Set the rotation
        rotation = App.Rotation(App.Vector(0, 0, 1), angle)
        obj.AttachmentOffset.Rotation = rotation

        # Recompute the sketch
        obj.recompute()

        # Update state variables
        self._last_offset_x = offset_x
        self._last_offset_y = offset_y
        self._last_offset_z = offset_z
        self._last_angle = angle

    def onDocumentRestored(self, obj):
        """Initialize when restoring from a file"""
        obj.Proxy = self
        if hasattr(obj, "ViewObject"):
            obj.ViewObject.Proxy = CustomObjectViewProvider(obj.ViewObject)

    def execute(self, obj):
        """Core method for building the geometry"""
        _offset_z = FCUnits.Quantity(0)
        # Validate necessary properties
        if not obj.Sketch or not obj.EdgeName:
            return

        # Parse the edge reference
        try:
            edge_sketch_name, subedge = obj.EdgeName.split(':')
        except ValueError:
            raise ValueError("Invalid edge name format. Use 'SketchName:EdgeN'")

        sketchL = obj.getObject(obj.Sketch)
        edge_sketch: SketchObject = App.ActiveDocument.getObject(edge_sketch_name)

        # Perform the sweep
        edge:Edge = edge_sketch.getSubObject(subedge)
        pad_length = edge.Length
        if obj.ChamferAngleR == 0:
            pad_length += obj.ExtendedLengthR.Value
        if obj.ChamferAngleL == 0:
            pad_length += obj.ExtendedLengthL.Value # Then set offset below
            _offset_z = obj.ExtendedLengthL
        baseObj = self.pad(sketchL, pad_length, obj, obj.EdgeName, reversed=True)

        # Chamfer
        if obj.ChamferAngleL > 0:
            baseObj, extended_length = self.create_chamfer(sketchL, obj.ChamferAngleL, obj.ChamferDirectionL, obj, baseObj, f"Chamfer_{obj.Name}_L")
            obj.ExtendedLengthL = FCUnits.Quantity(extended_length)
            obj.setEditorMode('ExtendedLengthL', 1)
        else:
            self.clean_chamfer(obj, f"Chamfer_{obj.Name}_L")
        if obj.ChamferAngleR > 0:
            sketchR = self.getSketchR(obj, pad_length)
            baseObj, extended_length = self.create_chamfer(sketchR, obj.ChamferAngleR, obj.ChamferDirectionR, obj, baseObj, f"Chamfer_{obj.Name}_R",
                                                           offset=-pad_length, right=True)
            obj.ExtendedLengthR = FCUnits.Quantity(extended_length)
            obj.setEditorMode('ExtendedLengthR', 1)
        else:
            self.clean_chamfer(obj, f"Chamfer_{obj.Name}_R", right=True)
            # Extend the right side
            # if obj.ExtendedLengthR > 0:
            #     sketchR = self.getSketchR(obj, pad_length)
            #     baseObj = self.pad(sketchR, obj.ExtendedLengthR, obj, f"ExtendR_{obj.Name}", baseFeature=baseObj, reversed=True)

        obj.Length = FCUnits.Quantity(pad_length + obj.ExtendedLengthL.Value + obj.ExtendedLengthR.Value)

        obj.Shape = baseObj.Shape

        # Apply offset and rotation to the obj
        self.apply_offset_and_rotation(obj, obj.OffsetX, obj.OffsetY, obj.Angle, offset_z=_offset_z)

        obj.AttachmentSupport = [(edge_sketch, subedge)]
        obj.MapMode = 'NormalToEdge'

        # Ensure the geometry is visible
        obj.purgeTouched()

    def pad(self, sketch: SketchObject, length: float, body:Body, name:str, reversed=False, baseFeature=None):
        pad_obj = GetExistent(f'frame_{name.replace(':', '_')}', 'PartDesign::Pad', body)
        if pad_obj.Profile !=sketch or pad_obj.Length!=length or pad_obj.Reversed!=reversed or pad_obj.BaseFeature!=baseFeature:
            pad_obj.Profile = sketch
            pad_obj.Length = length
            pad_obj.Reversed = reversed
            pad_obj.BaseFeature = baseFeature
            pad_obj.recompute()
        sketch.Visibility = False
        pad_obj.Visibility = False
        pad_obj.purgeTouched()
        return pad_obj

    def __getstate__(self):
        state = {'_last_offset_x': self._last_offset_x.toStr(),
                 '_last_offset_y': self._last_offset_y.toStr(),
                 '_last_offset_z': self._last_offset_z.toStr(),
                 '_last_angle': self._last_angle.toStr(),
                 'chamfer_sketch_cache': self.chamfer_sketch_cache,
                 'sketchLableL': self.sketchLableL,
                 'sketchR': self.sketchR,
                 }
        return state

    def __setstate__(self, state):
        self._last_offset_x = FCUnits.Quantity(state['_last_offset_x'])
        self._last_offset_y = FCUnits.Quantity(state['_last_offset_y'])
        self._last_offset_z = FCUnits.Quantity(state['_last_offset_z'])
        self._last_angle = FCUnits.Quantity(state['_last_angle'])
        self.chamfer_sketch_cache = state['chamfer_sketch_cache']
        self.sketchLableL = state['sketchLableL']
        self.sketchR = state['sketchR']

    def clean_chamfer(self, body:Body, name, right=False):
        pocket_obj = body.getObject(f"Chamfer_{name}")
        if pocket_obj is not None:
            App.ActiveDocument.removeObject(pocket_obj.Name)
        chamfer_sketch = body.getObject(f"chamferCuttingSketch_{name}")
        if chamfer_sketch is not None:
            App.ActiveDocument.removeObject(chamfer_sketch.Name)
        extended_obj = body.getObject(f"frame_Chamfer_extend_{name}")
        if extended_obj is not None:
            App.ActiveDocument.removeObject(extended_obj.Name)
            if right:
                body.ExtendedLengthR = FCUnits.Quantity(0)
                body.setEditorMode('ExtendedLengthR', 0)
            else:
                body.ExtendedLengthL = FCUnits.Quantity(0)
                body.setEditorMode('ExtendedLengthL', 0)

    def create_chamfer(self, sketch: SketchObject, angle: float, direction: int, body: Body, baseFeature, name, offset=0.0, right=False):
        '''
        sketch: The sketch used to extend the profile.
        direction: 1~4
        '''
        boundBox = sketch.Shape.BoundBox
        xy_extremes = (boundBox.XMin, boundBox.XMax, boundBox.YMin, boundBox.YMax)

        # Extend tan(angle)*width/2
        # TODO: It's better to set math expression instead of approximate value, but I guess nobody cares.(I'm too lazy to do it.)
        if direction in (1, 3):
            width = xy_extremes[1] - xy_extremes[0]
        else:
            width = xy_extremes[3] - xy_extremes[2]
        width = round(abs(width), 5)
        extended_length = round(abs(math.tan(math.radians(angle)) * width / 2), 5)
        extended_obj = self.pad(sketch, extended_length, body, f"Chamfer_extend_{name}", baseFeature=baseFeature, reversed=right)

        # Draw a cutting sketch
        chamfer_sketch: SketchObject = GetExistent(f'chamferCuttingSketch_{name}', 'Sketcher::SketchObject', body)
        if self.chamfer_sketch_cache[right] != (extended_length, width, baseFeature.Name, direction):
            print(f"{self.chamfer_sketch_cache[right]} != {(extended_length, width, baseFeature.Name, direction)}, redrawing")
            if self.chamfer_sketch_cache[right] is not None:
                chamfer_sketch.Geometry = []
                chamfer_sketch.Constraints = []
            self.draw_chamfer_sketch(chamfer_sketch, extended_length, width, baseFeature, direction, offset, right=right)
            self.chamfer_sketch_cache[right] = (extended_length, width, baseFeature.Name, direction)

        # Create Pocket
        pocket_obj = GetExistent(f'Chamfer_{name}', 'PartDesign::Pocket', body)
        if pocket_obj.BaseFeature!=extended_obj or pocket_obj.Profile!=chamfer_sketch:
            pocket_obj.BaseFeature = extended_obj
            pocket_obj.Profile = chamfer_sketch
            pocket_obj.AlongSketchNormal = 1
            pocket_obj.Type = 1
            pocket_obj.Midplane = 1
            pocket_obj.recompute()
        extended_obj.Visibility = False
        pocket_obj.Visibility = False
        pocket_obj.purgeTouched()
        extended_obj.purgeTouched()
        return pocket_obj, extended_length

    def draw_chamfer_sketch(self, chamfer_sketch: SketchObject, length: float, width: float, baseFeature, direction, offset, right):
        chamfer_sketch.AttachmentSupport = [(baseFeature, '')]
        chamfer_sketch.MapMode = 'ObjectXY'
        chamfer_sketch.AttachmentOffset = App.Placement(App.Vector(0 , 0, offset),  App.Rotation(0, 90, direction*90))
        chamfer_sketch.Visibility = False
        chamfer_sketch.recompute()

        tx = length
        ty = width / 2
        triangle = [(-tx, ty), (-tx, -ty), (tx, ty)] if not right else [(tx, ty), (tx, -ty), (-tx, ty)]
        chamfer_sketch.addGeometry(Part.LineSegment(App.Vector(triangle[0][0], triangle[0][1], 0),
                                    App.Vector(triangle[1][0], triangle[1][1], 0)), False)
        chamfer_sketch.addGeometry(Part.LineSegment(App.Vector(triangle[1][0], triangle[1][1], 0),
                                    App.Vector(triangle[2][0], triangle[2][1], 0)), False)
        chamfer_sketch.addGeometry(Part.LineSegment(App.Vector(triangle[2][0], triangle[2][1], 0),
                                    App.Vector(triangle[0][0], triangle[0][1], 0)), False)
        chamfer_sketch.recompute()

    def getSketchR(self, obj, pad_length):
        if self.sketchR is not None:
            if self.sketchR[0].startswith(f'{self.sketchLableL}_R'):
                return obj.getObject(self.sketchR[1])
            App.ActiveDocument.removeObject(self.sketchR[1])

        sketchR:SketchObject = CopyObj(obj.getObject(obj.Sketch), obj)
        sketchR.AttachmentSupport = obj.getObject(obj.Sketch)
        sketchR.MapMode = 'ObjectXY'
        sketchR.AttachmentOffset.Base = App.Vector(0 ,0 , - pad_length)
        sketchR.Label = f'{sketchR.Label}_R'
        self.sketchR = (sketchR.Label, sketchR.Name)
        sketchR.recompute()
        return sketchR

    def setSketch(self, obj, sketch: SketchObject):
        if sketch.Label == self.sketchLableL:
            return
        if self.sketchLableL is not None:
            App.ActiveDocument.removeObject(obj.Sketch)
            self.sketchLableL = None # Unnecessary
        obj.Sketch = CopyObj(sketch, obj).Name
        self.sketchLableL = sketch.Label

def CreateProfileFrameBody(Sketch: SketchObject, EdgeName: str, doc: App.Document|AppPart = None, name = "ProfileFrameBody"):
    ''' Note: The sketch and edge must be in the current document. '''
    if doc is None:
        doc = App.activeDocument()

    name = name.replace(':', '_')
    obj = doc.getObject(name)
    if obj is None:
        if isinstance(doc, App.Document):
            obj = doc.addObject('PartDesign::FeatureAdditivePython', name)
        else:
            obj = doc.newObject('PartDesign::FeatureAdditivePython', name)
        # Initialize the object
        ProfileFrameObject(obj)
    obj.Proxy.setSketch(obj, Sketch)
    obj.EdgeName = EdgeName
    return obj