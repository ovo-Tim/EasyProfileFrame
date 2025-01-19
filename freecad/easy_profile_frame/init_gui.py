import os
import FreeCADGui as Gui
import FreeCAD as App
from freecad.easy_profile_frame import ICONPATH, TRANSLATIONSPATH

translate=App.Qt.translate
QT_TRANSLATE_NOOP=App.Qt.QT_TRANSLATE_NOOP

# Add translations path
Gui.addLanguagePath(TRANSLATIONSPATH)
Gui.updateLocale()

class EasyProfileFrame(Gui.Workbench):
    """
    class which gets initiated at startup of the gui
    """
    MenuText = translate("Workbench", "Easy profile frame")
    ToolTip = translate("Workbench", "a simple Easy profile frame")
    # Icon = os.path.join(ICONPATH, "cool.svg")
    toolbox = ["EPF_CreateProfilesBySketcher"]

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        here is the place to import all the commands
        """
        # Register commands
        import freecad.easy_profile_frame.commands.create_profiles

        App.Console.PrintMessage(translate(
            "Log",
            "Switching to easy_profile_frame") + "\n")

        # NOTE: Context for this commands must be "Workbench"
        self.appendToolbar(QT_TRANSLATE_NOOP("Workbench", "Tools"), self.toolbox)
        self.appendMenu(QT_TRANSLATE_NOOP("Workbench", "Tools"), self.toolbox)

    def Activated(self):
        '''
        code which should be computed when a user switch to this workbench
        '''
        App.Console.PrintMessage(translate(
            "Log",
            "Workbench easy_profile_frame activated.") + "\n")

    def Deactivated(self):
        '''
        code which should be computed when this workbench is deactivated
        '''
        App.Console.PrintMessage(translate(
            "Log",
            "Workbench easy_profile_frame de-activated.") + "\n")


Gui.addWorkbench(EasyProfileFrame())
