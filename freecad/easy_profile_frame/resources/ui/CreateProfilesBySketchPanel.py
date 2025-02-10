# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CreateProfilesBySketchPanel.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(601, 918)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_wire_selector = QGroupBox(Form)
        self.frame_wire_selector.setObjectName("frame_wire_selector")
        self.verticalLayout_2 = QVBoxLayout(self.frame_wire_selector)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_5 = QLabel(self.frame_wire_selector)
        self.label_5.setObjectName("label_5")

        self.verticalLayout_2.addWidget(self.label_5)

        self.wire_list = QListWidget(self.frame_wire_selector)
        self.wire_list.setObjectName("wire_list")

        self.verticalLayout_2.addWidget(self.wire_list)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_wire_selector_add = QPushButton(self.frame_wire_selector)
        self.frame_wire_selector_add.setObjectName("frame_wire_selector_add")

        self.horizontalLayout.addWidget(self.frame_wire_selector_add)

        self.frame_wire_selector_rm = QPushButton(self.frame_wire_selector)
        self.frame_wire_selector_rm.setObjectName("frame_wire_selector_rm")

        self.horizontalLayout.addWidget(self.frame_wire_selector_rm)

        self.frame_wire_selector_show = QPushButton(self.frame_wire_selector)
        self.frame_wire_selector_show.setObjectName("frame_wire_selector_show")

        self.horizontalLayout.addWidget(self.frame_wire_selector_show)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.verticalLayout.addWidget(self.frame_wire_selector)

        self.profile = QGroupBox(Form)
        self.profile.setObjectName("profile")
        self.verticalLayout_3 = QVBoxLayout(self.profile)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.radioBtn_lib = QRadioButton(self.profile)
        self.radioBtn_lib.setObjectName("radioBtn_lib")
        self.radioBtn_lib.setChecked(True)

        self.verticalLayout_3.addWidget(self.radioBtn_lib)

        self.radioBtn_custom = QRadioButton(self.profile)
        self.radioBtn_custom.setObjectName("radioBtn_custom")

        self.verticalLayout_3.addWidget(self.radioBtn_custom)

        self.lib_group = QGroupBox(self.profile)
        self.lib_group.setObjectName("lib_group")
        self.formLayout = QFormLayout(self.lib_group)
        self.formLayout.setObjectName("formLayout")
        self.label = QLabel(self.lib_group)
        self.label.setObjectName("label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.lib_files = QComboBox(self.lib_group)
        self.lib_files.setObjectName("lib_files")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.lib_files)

        self.lib_sketches = QComboBox(self.lib_group)
        self.lib_sketches.setObjectName("lib_sketches")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.lib_sketches)

        self.label_2 = QLabel(self.lib_group)
        self.label_2.setObjectName("label_2")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_2)

        self.verticalLayout_3.addWidget(self.lib_group)

        self.custom_group = QGroupBox(self.profile)
        self.custom_group.setObjectName("custom_group")
        self.formLayout_2 = QFormLayout(self.custom_group)
        self.formLayout_2.setObjectName("formLayout_2")
        self.custom_sketch_select_btn = QPushButton(self.custom_group)
        self.custom_sketch_select_btn.setObjectName("custom_sketch_select_btn")

        self.formLayout_2.setWidget(
            0, QFormLayout.LabelRole, self.custom_sketch_select_btn
        )

        self.custom_sketch_label = QLabel(self.custom_group)
        self.custom_sketch_label.setObjectName("custom_sketch_label")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.custom_sketch_label)

        self.verticalLayout_3.addWidget(self.custom_group)

        self.verticalLayout.addWidget(self.profile)

        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.rotate_btn = QPushButton(self.groupBox)
        self.rotate_btn.setObjectName("rotate_btn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.rotate_btn.sizePolicy().hasHeightForWidth())
        self.rotate_btn.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.rotate_btn)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.angle_dis = QLabel(self.groupBox)
        self.angle_dis.setObjectName("angle_dis")

        self.horizontalLayout_2.addWidget(self.angle_dis)

        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)

        self.groupBox_3 = QGroupBox(self.groupBox)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_6 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.X_offset = QHBoxLayout()
        self.X_offset.setObjectName("X_offset")
        self.label_3 = QLabel(self.groupBox_3)
        self.label_3.setObjectName("label_3")

        self.X_offset.addWidget(self.label_3)

        self.verticalLayout_6.addLayout(self.X_offset)

        self.Y_offset = QHBoxLayout()
        self.Y_offset.setObjectName("Y_offset")
        self.label_6 = QLabel(self.groupBox_3)
        self.label_6.setObjectName("label_6")

        self.Y_offset.addWidget(self.label_6)

        self.verticalLayout_6.addLayout(self.Y_offset)

        self.gridLayout.addWidget(self.groupBox_3, 1, 0, 1, 1)

        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(Form)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label__ = QLabel(self.groupBox_2)
        self.label__.setObjectName("label__")

        self.verticalLayout_4.addWidget(self.label__)

        self.no_processing = QRadioButton(self.groupBox_2)
        self.no_processing.setObjectName("no_processing")

        self.verticalLayout_4.addWidget(self.no_processing)

        self.miter_cut = QRadioButton(self.groupBox_2)
        self.miter_cut.setObjectName("miter_cut")
        self.miter_cut.setChecked(True)

        self.verticalLayout_4.addWidget(self.miter_cut)

        self.auto_alignA = QRadioButton(self.groupBox_2)
        self.auto_alignA.setObjectName("auto_alignA")
        self.auto_alignA.setChecked(False)

        self.verticalLayout_4.addWidget(self.auto_alignA)

        self.auto_alignB = QRadioButton(self.groupBox_2)
        self.auto_alignB.setObjectName("auto_alignB")

        self.verticalLayout_4.addWidget(self.auto_alignB)

        self.verticalLayout.addWidget(self.groupBox_2)

        self.realtime_update = QCheckBox(Form)
        self.realtime_update.setObjectName("realtime_update")
        self.realtime_update.setChecked(True)

        self.verticalLayout.addWidget(self.realtime_update)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.frame_wire_selector.setTitle(
            QCoreApplication.translate("Form", "Frame wire selector", None)
        )
        self.label_5.setText(
            QCoreApplication.translate(
                "Form",
                "We recommend you select sketched or lines that created by Draft.",
                None,
            )
        )
        # if QT_CONFIG(tooltip)
        self.frame_wire_selector_add.setToolTip(
            QCoreApplication.translate("Form", "Add selected wires", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.frame_wire_selector_add.setText(
            QCoreApplication.translate("Form", "Add", None)
        )
        self.frame_wire_selector_rm.setText(
            QCoreApplication.translate("Form", "Remove", None)
        )
        self.frame_wire_selector_show.setText(
            QCoreApplication.translate("Form", "Show all", None)
        )
        self.profile.setTitle(
            QCoreApplication.translate("Form", "Profile(Created from sketch)", None)
        )
        self.radioBtn_lib.setText(
            QCoreApplication.translate("Form", "Select from library", None)
        )
        self.radioBtn_custom.setText(
            QCoreApplication.translate("Form", "Custom sketch", None)
        )
        self.lib_group.setTitle(
            QCoreApplication.translate("Form", "Select from library", None)
        )
        self.label.setText(QCoreApplication.translate("Form", "File:", None))
        self.label_2.setText(QCoreApplication.translate("Form", "Sketch:", None))
        self.custom_group.setTitle(
            QCoreApplication.translate("Form", "Custom sketch", None)
        )
        # if QT_CONFIG(tooltip)
        self.custom_sketch_select_btn.setToolTip(
            QCoreApplication.translate("Form", "Select the sketch and press me.", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.custom_sketch_select_btn.setText(
            QCoreApplication.translate("Form", "Select", None)
        )
        self.custom_sketch_label.setText(
            QCoreApplication.translate("Form", "Please select...", None)
        )
        self.groupBox.setTitle(QCoreApplication.translate("Form", "Move", None))
        self.rotate_btn.setText(QCoreApplication.translate("Form", "Rotate", None))
        self.angle_dis.setText(QCoreApplication.translate("Form", "Angle: 0", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Form", "Offset", None))
        self.label_3.setText(QCoreApplication.translate("Form", "X:", None))
        self.label_6.setText(QCoreApplication.translate("Form", "Y:", None))
        # if QT_CONFIG(tooltip)
        self.groupBox_2.setToolTip(
            QCoreApplication.translate(
                "Form",
                "This method only works on profiles without offsets(Rotations are allowed).",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.groupBox_2.setTitle(
            QCoreApplication.translate("Form", "Corner joint method", None)
        )
        self.label__.setText(
            QCoreApplication.translate("Form", "It's easy to modify later.", None)
        )
        self.no_processing.setText(
            QCoreApplication.translate(
                "Form",
                "No processing\n" "(Stretch  according to the original line length)",
                None,
            )
        )
        self.miter_cut.setText(
            QCoreApplication.translate(
                "Form", "Miter Cut(Support non-rectangular)", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.auto_alignA.setToolTip(
            QCoreApplication.translate(
                "Form",
                "This method only works on profiles without offsets(Rotations are allowed).",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.auto_alignA.setText(
            QCoreApplication.translate("Form", "Auto-Alignment A", None)
        )
        # if QT_CONFIG(tooltip)
        self.auto_alignB.setToolTip(
            QCoreApplication.translate(
                "Form",
                "This method only works on profiles without offsets(Rotations are allowed).",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.auto_alignB.setText(
            QCoreApplication.translate("Form", "Auto-Alignment B", None)
        )
        self.realtime_update.setText(
            QCoreApplication.translate("Form", "Real-time update view", None)
        )

    # retranslateUi
