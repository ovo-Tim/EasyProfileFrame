from setuptools import setup
import os

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "freecad", "easy_profile_frame", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.easy_profile_frame',
      version=str(__version__),
      packages=['freecad',
                'freecad.easy_profile_frame'],
      maintainer="Tim Tu",
      maintainer_email="ovo-tim@qq.com",
      url="https://github.com/ovo-Tim/easy-profile-frame",
      description="A FreeCAD workbench designed to simplify the creation of frames using profiles, such as aluminum profiles. It also includes support for exporting Bill of Materials (BOM).",
      install_requires=[],
      include_package_data=True)
