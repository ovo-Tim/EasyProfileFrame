set(Namespace_SRCS
        freecad/easy_profile_frame/init_gui.py
        freecad/easy_profile_frame/__init__.py
        freecad/easy_profile_frame/my_numpy_function.py
        freecad/easy_profile_frame/version.py
        freecad/easy_profile_frame/resources/cool.svg
        freecad/easy_profile_frame/resources/translations/easy_profile_frame_es-ES.qm
        freecad/easy_profile_frame/resources/translations/easy_profile_frame_es-ES.ts
)

SOURCE_GROUP("" FILES ${Namespace_SRCS})

ADD_CUSTOM_TARGET(SEARCHBAR ALL
        SOURCES ${Namespace_SRCS}
)

fc_copy_sources(SEARCHBAR "${CMAKE_BINARY_DIR}/Mod/EasyProfileFrame" ${Namespace_SRCS})

INSTALL(
    FILES
        ${Namespace_SRCS}
    DESTINATION
        Mod/SearchBar
)
