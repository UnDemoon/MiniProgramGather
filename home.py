# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'home.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(694, 522)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.Label_2 = QtWidgets.QLabel(self.centralwidget)
        self.Label_2.setObjectName("Label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.Label_2)
        self.DateEdit_2 = QtWidgets.QDateEdit(self.centralwidget)
        self.DateEdit_2.setObjectName("DateEdit_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.DateEdit_2)
        self.Label = QtWidgets.QLabel(self.centralwidget)
        self.Label.setObjectName("Label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.Label)
        self.DateEdit = QtWidgets.QDateEdit(self.centralwidget)
        self.DateEdit.setObjectName("DateEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.DateEdit)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label)
        self.verticalLayout.addLayout(self.formLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.horizontalLayout.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "微信小游戏采集"))
        self.Label_2.setText(_translate("MainWindow", "开始"))
        self.Label.setText(_translate("MainWindow", "结束"))
        self.label.setText(_translate("MainWindow", "session"))
        self.pushButton.setText(_translate("MainWindow", "开始"))
