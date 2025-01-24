from freecad.easy_profile_frame.typing import SelectionObject, Feature, Body, AppPart, SketchObject
import Part
import FreeCAD as App
from typing import Any

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

def GetOrCreate(name: str, obj_type: str, doc: App.Document|Body|AppPart) -> Any:
    '''Get an object from a document if it exists, otherwise create a new one.'''
    obj = doc.getObject(name)
    print(f'Getting object {name} Result: {obj}')
    if obj is not None:
        return obj
    if isinstance(doc, App.Document):
        return doc.addObject(obj_type, name)
    else:
        return doc.newObject(obj_type, name)

def CopyObj(source: App.DocumentObject|Feature, target: Body|AppPart, check_exist: bool = True) -> Any:
    '''
    Copy an object across documents.
    '''
    if check_exist:
        # I really don't like this, but is seems that there is no way to check if an object exists by label.
        for child in target.OutList:
            if child.Label == source.Label:
                return child
    doc = target.Document
    obj:App.DocumentObject|Feature = doc.copyObject(source)
    obj = target.addObject(obj)[0]
    obj.Label = source.Label
    return obj

def GetStored(body: Body, obj: SketchObject|Feature, typeId: str):
    if not hasattr(body, f'profile_{typeId}'):
        body.addProperty("App::PropertyString", f"profile_{typeId}", "EPF",
                            f"The original of {typeId} used to create the profile.")
        body.addProperty("App::PropertyString", f"profile_{typeId}_localName", "EPF",
                            f"The local name of {typeId} used to create the profile.")
    if getattr(body, f"profile_{typeId}") == obj.Name:
        return body.getObject(getattr(body, f"profile_{typeId}_localName"))
    else:
        sketch_type = obj.Name
        obj = CopyObj(obj, body)
        sketch_localName = obj.Name
        setattr(body, f"profile_{typeId}", sketch_type)
        setattr(body, f"profile_{typeId}_localName", sketch_localName)
        return obj
