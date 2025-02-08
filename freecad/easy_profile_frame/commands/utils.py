from freecad.easy_profile_frame.typing import SelectionObject, Feature, Body, AppPart, SketchObject, Edge
import Part
import FreeCAD as App
from typing import Any
import math

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

def GetExistent(name: str, obj_type: str, doc: App.Document|Body|AppPart) -> Any:
    '''Get an object from a document if it exists, otherwise create a new one.'''
    obj = doc.getObject(name)
    if obj is not None:
        return obj
    if isinstance(doc, App.Document):
        return doc.addObject(obj_type, name)
    else:
        return doc.newObject(obj_type, name)

def CopyObj(source: App.DocumentObject|Feature, target: Body|AppPart) -> Any:
    '''
    Copy an object across documents.
    '''
    doc = target.Document
    obj:App.DocumentObject|Feature = doc.copyObject(source)
    obj = target.addObject(obj)[0]
    obj.Label = source.Label
    return obj

def calculate_edges_angle(edge1:Edge, edge2:Edge):
    """
    Calculate the angle between two Part.Edge objects.

    Parameters:
    edge1 -- The first edge (Part.Edge)
    edge2 -- The second edge (Part.Edge)

    Returns:
    The angle between the two edges in degrees.
    """
    # Get the direction vector of the first edge (using the tangent at the start point)
    vec1 = edge1.tangentAt(edge1.FirstParameter)

    # Get the direction vector of the second edge (using the tangent at the start point)
    vec2 = edge2.tangentAt(edge2.FirstParameter)

    # Calculate the dot product and the magnitude product of the two direction vectors
    dot_product = vec1.dot(vec2)
    magnitude_product = vec1.Length * vec2.Length

    # Ensure the denominator is not 0 to avoid division by zero error
    if magnitude_product == 0:
        raise ValueError("Edges do not have a valid direction to compute an angle.")

    # Calculate the angle in radians
    angle_radians = math.acos(dot_product / magnitude_product)

    # Convert the angle to degrees
    angle_degrees = math.degrees(angle_radians)

    return angle_degrees