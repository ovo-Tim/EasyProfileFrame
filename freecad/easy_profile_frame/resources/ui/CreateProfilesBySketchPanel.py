# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CreateProfilesBySketchPanel.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QGroupBox, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QRadioButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(551, 722)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame_wire_selector = QGroupBox(Form)
        self.frame_wire_selector.setObjectName(u"frame_wire_selector")
        self.verticalLayout_2 = QVBoxLayout(self.frame_wire_selector)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_5 = QLabel(self.frame_wire_selector)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout_2.addWidget(self.label_5)

        self.wire_list = QListWidget(self.frame_wire_selector)
        self.wire_list.setObjectName(u"wire_list")

        self.verticalLayout_2.addWidget(self.wire_list)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_wire_selector_add = QPushButton(self.frame_wire_selector)
        self.frame_wire_selector_add.setObjectName(u"frame_wire_selector_add")

        self.horizontalLayout.addWidget(self.frame_wire_selector_add)

        self.frame_wire_selector_rm = QPushButton(self.frame_wire_selector)
        self.frame_wire_selector_rm.setObjectName(u"frame_wire_selector_rm")

        self.horizontalLayout.addWidget(self.frame_wire_selector_rm)

        self.frame_wire_selector_show = QPushButton(self.frame_wire_selector)
        self.frame_wire_selector_show.setObjectName(u"frame_wire_selector_show")

        self.horizontalLayout.addWidget(self.frame_wire_selector_show)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.verticalLayout.addWidget(self.frame_wire_selector)

        self.profile = QGroupBox(Form)
        self.profile.setObjectName(u"profile")
        self.verticalLayout_3 = QVBoxLayout(self.profile)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.radioBtn_lib = QRadioButton(self.profile)
        self.radioBtn_lib.setObjectName(u"radioBtn_lib")
        self.radioBtn_lib.setChecked(True)

        self.verticalLayout_3.addWidget(self.radioBtn_lib)

        self.radioBtn_custom = QRadioButton(self.profile)
        self.radioBtn_custom.setObjectName(u"radioBtn_custom")

        self.verticalLayout_3.addWidget(self.radioBtn_custom)

        self.lib_group = QGroupBox(self.profile)
        self.lib_group.setObjectName(u"lib_group")
        self.formLayout = QFormLayout(self.lib_group)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.lib_group)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.lib_files = QComboBox(self.lib_group)
        self.lib_files.setObjectName(u"lib_files")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.lib_files)

        self.lib_sketches = QComboBox(self.lib_group)
        self.lib_sketches.setObjectName(u"lib_sketches")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.lib_sketches)

        self.label_2 = QLabel(self.lib_group)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_2)


        self.verticalLayout_3.addWidget(self.lib_group)

        self.custom_group = QGroupBox(self.profile)
        self.custom_group.setObjectName(u"custom_group")
        self.formLayout_2 = QFormLayout(self.custom_group)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.custom_sketch_select_btn = QPushButton(self.custom_group)
        self.custom_sketch_select_btn.setObjectName(u"custom_sketch_select_btn")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.custom_sketch_select_btn)

        self.custom_sketch_label = QLabel(self.custom_group)
        self.custom_sketch_label.setObjectName(u"custom_sketch_label")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.custom_sketch_label)


        self.verticalLayout_3.addWidget(self.custom_group)


        self.verticalLayout.addWidget(self.profile)

        self.groupBox_2 = QGroupBox(Form)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_4.addWidget(self.label_4)

        self.auto_align = QRadioButton(self.groupBox_2)
        self.auto_align.setObjectName(u"auto_align")
        self.auto_align.setChecked(True)

        self.verticalLayout_4.addWidget(self.auto_align)

        self.miter_cut = QRadioButton(self.groupBox_2)
        self.miter_cut.setObjectName(u"miter_cut")

        self.verticalLayout_4.addWidget(self.miter_cut)

        self.reserved = QRadioButton(self.groupBox_2)
        self.reserved.setObjectName(u"reserved")

        self.verticalLayout_4.addWidget(self.reserved)

        self.no_processing = QRadioButton(self.groupBox_2)
        self.no_processing.setObjectName(u"no_processing")

        self.verticalLayout_4.addWidget(self.no_processing)

        self.fillet = QRadioButton(self.groupBox_2)
        self.fillet.setObjectName(u"fillet")

        self.verticalLayout_4.addWidget(self.fillet)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.realtime_update = QCheckBox(Form)
        self.realtime_update.setObjectName(u"realtime_update")
        self.realtime_update.setChecked(True)

        self.verticalLayout.addWidget(self.realtime_update)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.frame_wire_selector.setTitle(QCoreApplication.translate("Form", u"Frame wire selector", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"We recommend you select sketched or lines that created by Draft.", None))
#if QT_CONFIG(tooltip)
        self.frame_wire_selector_add.setToolTip(QCoreApplication.translate("Form", u"Add selected wires", None))
#endif // QT_CONFIG(tooltip)
        self.frame_wire_selector_add.setText(QCoreApplication.translate("Form", u"Add", None))
        self.frame_wire_selector_rm.setText(QCoreApplication.translate("Form", u"Remove", None))
        self.frame_wire_selector_show.setText(QCoreApplication.translate("Form", u"Show all", None))
        self.profile.setTitle(QCoreApplication.translate("Form", u"Profile(Created from sketch)", None))
        self.radioBtn_lib.setText(QCoreApplication.translate("Form", u"Select from library", None))
        self.radioBtn_custom.setText(QCoreApplication.translate("Form", u"Custom sketch", None))
        self.lib_group.setTitle(QCoreApplication.translate("Form", u"Select from library", None))
        self.label.setText(QCoreApplication.translate("Form", u"File:", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Sketch:", None))
        self.custom_group.setTitle(QCoreApplication.translate("Form", u"Custom sketch", None))
#if QT_CONFIG(tooltip)
        self.custom_sketch_select_btn.setToolTip(QCoreApplication.translate("Form", u"Select the sketch and press me.", None))
#endif // QT_CONFIG(tooltip)
        self.custom_sketch_select_btn.setText(QCoreApplication.translate("Form", u"Select", None))
        self.custom_sketch_label.setText(QCoreApplication.translate("Form", u"Please select...", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", u"Corner joint method", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"It's easy to modify later.", None))
        self.auto_align.setText(QCoreApplication.translate("Form", u"Auto-Alignment", None))
        self.miter_cut.setText(QCoreApplication.translate("Form", u"Miter Cut", None))
        self.reserved.setText(QCoreApplication.translate("Form", u"Reserved(Manual stretch later)", None))
        self.no_processing.setText(QCoreApplication.translate("Form", u"No processing(Stretch  according to the original line length)", None))
        self.fillet.setText(QCoreApplication.translate("Form", u"Fillet", None))
        self.realtime_update.setText(QCoreApplication.translate("Form", u"Real-time update view", None))
    # retranslateUi

