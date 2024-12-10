# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 11:51:49 2024

@author: Thomas_JA
"""
import io
from PyQt5 import QtCore, QtGui, QtWidgets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

 
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################


def check_left_right(style_row, index):
    """
    style_row - array of characters: p, n, x, f
    index     - integer of where a pinch or fade is said to be

    Uses the index to search the style_row for the direction of pinching and fading.
    """
    # If it is the last item in the array then the direction is left
    if index == (len(style_row)-1) and style_row[index - 1] == 'n' :
        return 'left'
    # If it is the first item in the array then the direction is right
    elif index == 0 and style_row[index + 1] == 'n':
        return 'right'
    # If both directions are void, then pinch in both directions
    elif style_row[index - 1] == 'n' and style_row[index + 1] == 'n':
        return 'both'
    # If the item before is void, pinch to the left
    elif style_row[index - 1] == 'n':
        return 'left'
    # If the item after is void pinch to the right
    elif style_row[index + 1] == 'n':
        return 'right'


#######################################################################################################################################################


def find_bottom(style_array, row, index, direction):
    """
    style_array - array of characters: n, p, f, x.
    row         - integer, the row of the style array currently being worked
    index       - integer, the index at which the pinch of fade currently being calculated is at
    direction   - string: left, righ, both. The direction in which the formation pinches or fades

    Finds the non np.nan values for the slope calculation later.
    """
    #Creates an empty list to add row number to later
    slope_rows = []

    if direction == 'left':
        #If direction is left, it will grab the appropriate two values from the next row
        slope_points = style_array[row+1][[index-1, index]]
        n=0 # Increment for rows of the style array, used in the while loop
        #Then checks if they both are not np.nan
        if np.all(slope_points == ['x', 'x']):
            slope_rows.append(row+1) # Adds to the list if not np.nan
        else:
            while np.any(slope_points != ['x', 'x']): #Searches downwards until it finds 2 values that aren't np.nan
                n += 1
                slope_points=style_array[row+1+n][[index, index+1]]
            slope_rows.append(row+1+n)
            

    elif direction == 'right':
        #If direction is right, it will grab the appropriate two values from the next row
        slope_points = style_array[row+1][[index, index+1]]
        n=0 # Increment for rows of the style array, used in the while loop
        if np.all(slope_points == ['x', 'x']):
            slope_rows.append(row+1)# Adds to the list if not np.nan
        else:
            while np.any(slope_points != ['x', 'x']): #Searches downwards until it finds 2 values that aren't np.nan
                n += 1
                slope_points=style_array[row+1+n][[index, index+1]]
            slope_rows.append(row+1+n)
            

    elif direction == 'both': 
        #If direction is both we must grab four values to check the value to the left and right of the pinch point
        slope_right=style_array[row+1][[index, index+1]]
        slope_left=style_array[row+1][[index-1, index]]
        n=0 # Increment for rows of the style array, used in the while loop
        if np.all(slope_left == ['x','x']): #This checks the left side for np.nan values
            slope_rows.append(row+1)# Adds to the list if not np.nan
        else:
            while np.any(slope_left != ['x', 'x']):
                n += 1
                slope_left=style_array[row+1+n][[index, index+1]]
            slope_rows.append(row+1+n)
            
        n=0 # Increment for rows of the style array, used in the while loop
        if np.all(slope_right == ['x', 'x']): #This checks the right side for np.nan values
            slope_rows.append(row+1)# Adds to the list if not np.nan
        else:
            while np.any(slope_right != ['x', 'x']):
                n += 1
                slope_right=style_array[row+1+n][[index, index+1]]
            slope_rows.append(row+1+n)

    return slope_rows


#######################################################################################################################################################


def slope_calculator(formations_array, style_array, distance, row, index, direction, midpoint_ratio1, midpoint_ratio2=2):
    """
    formations_array - array of floats, top depth of formations
    style_array      - array of characters: n, p, f, x
    distance         - array of integers or floats, indicating the distance from the start of the cross section that each well is at
    row              - integer, the row of the style array currently being worked
    index            - integer, the index at which the pinch of fade currently being calculated is at
    direction        - string: left, righ, both. The direction in which the formation pinches or fades 
    """
    
    if direction == 'right':
        slope_rows = find_bottom(style_array, row, index, direction)
        depth1 = formations_array[slope_rows, index][0]
        depth2 = formations_array[slope_rows, index+1][0]

        distance1 = distance[index]
        distance2 = distance[index+1]
        

        slope = (depth1 - depth2) / (distance1 - distance2)
        midpoint = midpoint_ratio1
        yintercept = depth1 - (slope * distance1)
        point = (slope * midpoint) + yintercept


        new_point = np.array([[point], [point], [midpoint]])

        return new_point

    elif direction == 'left':
        slope_rows = find_bottom(style_array, row, index, direction)
        depth1 = formations_array[slope_rows, index][0]
        depth2 = formations_array[slope_rows, index-1][0]

        distance1 = distance[index]
        distance2 = distance[index-1]
        

        slope = (depth1 - depth2) / (distance1 - distance2)
        midpoint = midpoint_ratio1
        yintercept = depth1 - (slope * distance1)
        point = (slope * midpoint) + yintercept

        new_point = np.array([[point], [point], [midpoint]])

        return new_point

    
    elif direction == 'both':
        left_right_points = []
        slope_rows = find_bottom(style_array, row, index, direction)
        #Calculate the left point
        
        depth1 = formations_array[slope_rows[0], index]
        depth2 = formations_array[slope_rows[0], index-1]

        distance1 = distance[index]
        distance2 = distance[index-1]
        
        slope = (depth1 - depth2) / (distance1 - distance2)
        midpoint = midpoint_ratio1
        yintercept = depth1 - (slope * distance1)
        point = (slope * midpoint) + yintercept

        new_point = np.array([[point], [point], [midpoint]])
        left_right_points.append(new_point)

        #Calculate the right point
        depth1 = formations_array[slope_rows[1], index]
        depth2 = formations_array[slope_rows[1], index+1]

        distance1 = distance[index]
        distance2 = distance[index+1]
        
        slope = (depth1 - depth2) / (distance1 - distance2)
        midpoint = midpoint_ratio2
        yintercept = depth1 - (slope * distance1)
        point = (slope * midpoint) + yintercept

        new_point = np.array([[point], [point], [midpoint]])
        left_right_points.append(new_point)

        return left_right_points
   
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1511, 930)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 5, 1491, 880))
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        
        self.selectFile_button = QtWidgets.QPushButton(self.tab)
        self.selectFile_button.setGeometry(QtCore.QRect(0, 10, 91, 31))
        self.selectFile_button.setObjectName("selectFile_button")
        
        self.mainUpdate_button = QtWidgets.QPushButton(self.tab)
        self.mainUpdate_button.setGeometry(QtCore.QRect(100, 10, 111, 31))
        self.mainUpdate_button.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.mainUpdate_button.setObjectName("mainUpdate_button")
        
        self.main_xsecplot = QtWidgets.QLabel(self.tab)
        self.main_xsecplot.setGeometry(QtCore.QRect(10, 80, 1471, 751))
        self.main_xsecplot.setFrameShape(QtWidgets.QFrame.Box)
        self.main_xsecplot.setText("")
        self.main_xsecplot.setAlignment(QtCore.Qt.AlignCenter)
        self.main_xsecplot.setObjectName("main_xsecplot")
        
        self.adjustPinchFade_combox = QtWidgets.QComboBox(self.tab)
        self.adjustPinchFade_combox.setGeometry(QtCore.QRect(310, 40, 69, 22))
        self.adjustPinchFade_combox.setObjectName("adujstPinchFade_combox")
        
        self.adjustPinchFadeFormation_combox = QtWidgets.QComboBox(self.tab)
        self.adjustPinchFadeFormation_combox.setGeometry(QtCore.QRect(390, 40, 69, 22))
        self.adjustPinchFadeFormation_combox.setObjectName("adjustPinchFadeFormation_combox")
        
        self.adjustPinchFadeIndex_combox = QtWidgets.QComboBox(self.tab)
        self.adjustPinchFadeIndex_combox.setGeometry(QtCore.QRect(470, 40, 110, 22))
        self.adjustPinchFadeIndex_combox.setObjectName("adjustPinchFadeIndex_combox")
        
        self.adjustPinchFade_slider = QtWidgets.QSlider(self.tab)
        self.adjustPinchFade_slider.setGeometry(QtCore.QRect(600, 40, 160, 22))
        self.adjustPinchFade_slider.setOrientation(QtCore.Qt.Horizontal)
        self.adjustPinchFade_slider.setObjectName("adjustPinchFade_slider")
        
        self.adjustPinchFadeMin_label = QtWidgets.QLabel(self.tab)
        self.adjustPinchFadeMin_label.setGeometry(QtCore.QRect(580, 20, 47, 20))
        self.adjustPinchFadeMin_label.setText("")
        self.adjustPinchFadeMin_label.setObjectName("adjustPinchFadeMin_label")
        self.adjustPinchFadeMin_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.adjustPinchFadeMax_label = QtWidgets.QLabel(self.tab)
        self.adjustPinchFadeMax_label.setGeometry(QtCore.QRect(730, 20, 47, 20))
        self.adjustPinchFadeMax_label.setText("")
        self.adjustPinchFadeMax_label.setObjectName("adjustPinchFadeMax_label")
        self.adjustPinchFadeMax_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.adjustPinchFadetitle_label = QtWidgets.QLabel(self.tab)
        self.adjustPinchFadetitle_label.setGeometry(QtCore.QRect(333, 10, 230, 20))
        self.adjustPinchFadetitle_label.setText('Adjust Pinch / Fade Locations')
        self.adjustPinchFadetitle_label.setObjectName('adjustPinchFadetitle_label')
        self.adjustPinchFadetitle_label.setAlignment(QtCore.Qt.AlignCenter)
        font = self.adjustPinchFadetitle_label.font()
        font.setPointSize(12)
        self.adjustPinchFadetitle_label.setFont(font)
        
        self.numberOfTeeth_textbox = QtWidgets.QTextEdit(self.tab)
        self.numberOfTeeth_textbox.setGeometry(QtCore.QRect(800, 40, 30, 20))
        self.numberOfTeeth_textbox.setObjectName("numberOfTeeth_textedit")
        self.numberOfTeeth_textbox.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.numberOfTeeth_label = QtWidgets.QLabel(self.tab)
        self.numberOfTeeth_label.setGeometry(QtCore.QRect(785, 20, 60, 20))
        self.numberOfTeeth_label.setText('# of teeth')
        self.numberOfTeeth_label.setObjectName('numberOfTeeth_label')
        self.numberOfTeeth_label.setAlignment(QtCore.Qt.AlignCenter)
        font = self.numberOfTeeth_label.font()
        font.setPointSize(10)
        self.numberOfTeeth_label.setFont(font)
        
        
        
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("picture--pencil.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.tab, icon, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        
        self.formationsUpdate_button = QtWidgets.QPushButton(self.tab_2)
        self.formationsUpdate_button.setGeometry(QtCore.QRect(10, 10, 111, 31))
        self.formationsUpdate_button.setObjectName("formationsUpdate_button")
        
        self.formations_table = QtWidgets.QTableWidget(self.tab_2)
        self.formations_table.setGeometry(QtCore.QRect(0, 50, 1481, 401))
        self.formations_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.formations_table.setObjectName("formations_table")
        self.formations_table.setColumnCount(0)
        self.formations_table.setRowCount(0)
        
        self.TopDepthOfFormations_label = QtWidgets.QLabel(self.tab_2)
        self.TopDepthOfFormations_label.setGeometry(QtCore.QRect(150, 0, 261, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.TopDepthOfFormations_label.setFont(font)
        self.TopDepthOfFormations_label.setObjectName("TopDepthOfFormations_label")
        self.TopDepthOfFormations_label.setText("Top Depth of Formations")
        
        self.formationPolygons_table = QtWidgets.QTableWidget(self.tab_2)
        self.formationPolygons_table.setGeometry(QtCore.QRect(0, 501, 1481, 311))
        self.formationPolygons_table.setObjectName("formationPolygons_table")
        self.formationPolygons_table.setColumnCount(0)
        self.formationPolygons_table.setRowCount(0)
        
        self.formationPolygons_label = QtWidgets.QLabel(self.tab_2)
        self.formationPolygons_label.setGeometry(QtCore.QRect(0, 460, 211, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.formationPolygons_label.setFont(font)
        self.formationPolygons_label.setObjectName("formationPolygons_label")
        
        self.formationPolygons_combox = QtWidgets.QComboBox(self.tab_2)
        self.formationPolygons_combox.setGeometry(QtCore.QRect(220, 461, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.formationPolygons_combox.setFont(font)
        self.formationPolygons_combox.setObjectName("formationPolygons_combox")
        
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("table-heatmap.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.tab_2, icon1, "")
        
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.styleUpdate_button = QtWidgets.QPushButton(self.tab_3)
        self.styleUpdate_button.setGeometry(QtCore.QRect(10, 10, 111, 31))
        self.styleUpdate_button.setObjectName("styleUpdate_button")
        
        self.style_table = QtWidgets.QTableWidget(self.tab_3)
        self.style_table.setGeometry(QtCore.QRect(0, 220, 1261, 271))
        self.style_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.style_table.setObjectName("style_table")
        self.style_table.setColumnCount(0)
        self.style_table.setRowCount(0)
        
        self.colors_table = QtWidgets.QTableWidget(self.tab_3)
        self.colors_table.setGeometry(QtCore.QRect(1270, 320, 211, 491))
        self.colors_table.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.colors_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.colors_table.setObjectName("colors_table")
        self.colors_table.setColumnCount(0)
        self.colors_table.setRowCount(0)
        
        self.sampleType_table = QtWidgets.QTableWidget(self.tab_3)
        self.sampleType_table.setGeometry(QtCore.QRect(0, 580, 1261, 231))
        self.sampleType_table.setObjectName("sampleType_table")
        self.sampleType_table.setColumnCount(0)
        self.sampleType_table.setRowCount(0)
        
        self.formationStyle_lable = QtWidgets.QLabel(self.tab_3)
        self.formationStyle_lable.setGeometry(QtCore.QRect(0, 190, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.formationStyle_lable.setFont(font)
        self.formationStyle_lable.setObjectName("formationStyle_lable")
        self.formationStyle_lable.setText("Formation Style")
        
        self.sampleType_label = QtWidgets.QLabel(self.tab_3)
        self.sampleType_label.setGeometry(QtCore.QRect(0, 550, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.sampleType_label.setFont(font)
        self.sampleType_label.setObjectName("sampleType_label")
        self.sampleType_label.setText('Sample Type')
        
        self.sampleType_combox = QtWidgets.QComboBox(self.tab_3)
        self.sampleType_combox.setGeometry(QtCore.QRect(240, 550, 69, 22))
        self.sampleType_combox.setObjectName("sampleType_combox")
        
        self.sampleChangesWithDepth_label = QtWidgets.QLabel(self.tab_3)
        self.sampleChangesWithDepth_label.setGeometry(QtCore.QRect(190, 530, 191, 16))
        self.sampleChangesWithDepth_label.setObjectName("sampleChangesWithDepth_label")
        
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("palette-paint-brush.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.tab_3, icon2, "")
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1511, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuSave = QtWidgets.QMenu(self.menuFile)
        self.menuExport_Data = QtWidgets.QMenu(self.menubar)
        self.menuExport_Data.setObjectName("menuExport_Data")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("disk-black.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menuSave.setIcon(icon3)
        self.menuSave.setObjectName("menuSave")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.actionSave_as_PDF = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("blue-document-pdf.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave_as_PDF.setIcon(icon3)
        self.actionSave_as_PDF.setObjectName("actionSave_as_PDF")
        
        self.actionSave_as_PNG = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("blue-document-image.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave_as_PNG.setIcon(icon4)
        self.actionSave_as_PNG.setObjectName("actionSave_as_PNG")
        
        self.actionSave_as_JPEG = QtWidgets.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("application-image.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave_as_JPEG.setIcon(icon5)
        self.actionSave_as_JPEG.setObjectName("actionSave_as_JPEG")
        
        self.actionSave_as_TIFF = QtWidgets.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("blue-document-attribute-t.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave_as_TIFF.setIcon(icon6)
        self.actionSave_as_TIFF.setObjectName("actionSave_as_TIFF")
        
        self.actionSave_as_EPS = QtWidgets.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("blue-document-sticky-note.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave_as_EPS.setIcon(icon7)
        self.actionSave_as_EPS.setObjectName("actionSave_as_EPS")
        
        self.actionExport_as_Excel = QtWidgets.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("table-excel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExport_as_Excel.setIcon(icon9)
        self.actionExport_as_Excel.setObjectName("actionExport_as_Excel")
        
        self.actionExport_as_CSV = QtWidgets.QAction(MainWindow)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap("document-excel-csv.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExport_as_CSV.setIcon(icon10)
        self.actionExport_as_CSV.setObjectName("actionExport_as_CSV")
        
        
        
        self.menuSave.addAction(self.actionSave_as_PDF)
        self.menuSave.addAction(self.actionSave_as_PNG)
        self.menuSave.addAction(self.actionSave_as_JPEG)
        self.menuSave.addAction(self.actionSave_as_TIFF)
        self.menuSave.addAction(self.actionSave_as_EPS)
        self.menuFile.addAction(self.menuSave.menuAction())
        self.menuExport_Data.addAction(self.actionExport_as_Excel)
        self.menuExport_Data.addAction(self.actionExport_as_CSV)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuExport_Data.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        self.formations_updated = False
        self.style_updated      = False
        self.polygon_updated    = False
        self.sampleType_updated = False
        self.colors_updated     = False
        self.pinchFadeslider_changed = False
        self.toothNumber_changed = False
        
        self.table_font = QtGui.QFont('MS Shell Dlg 2', 12)
        
        self.sampleType_combox.addItem('No', False)
        self.sampleType_combox.addItem('Yes', True)
        
        self.adjustPinchFade_combox.addItem('Pinch')
        self.adjustPinchFade_combox.addItem('Fade')
        
        
        self.mainUpdate_button.clicked.connect(self.update_figure)
        self.formationsUpdate_button.clicked.connect(self.update_figure)
        self.styleUpdate_button.clicked.connect(self.update_figure)
        self.selectFile_button.clicked.connect(self.select_file)
        self.formationPolygons_combox.activated.connect(self.create_formation_polygons_table)
        self.formationPolygons_table.itemChanged.connect(self.polygon_updated_status)
        self.formations_table.itemChanged.connect(self.formation_updated_status)
        self.style_table.itemChanged.connect(self.style_updated_status)
        self.sampleType_table.itemChanged.connect(self.sample_type_updated_status)
        self.colors_table.itemChanged.connect(self.colors_status)
        
        self.sampleType_combox.activated.connect(self.sample_changes)
        
        self.adjustPinchFadeFormation_combox.activated.connect(self.pinch_fade_index_combox)
        self.adjustPinchFade_combox.activated.connect(self.pinch_fade_index_combox)
        self.adjustPinchFade_slider.valueChanged.connect(self.pinch_fade_slider)
        
        self.adjustPinchFadeIndex_combox.activated.connect(self.pinch_fade_slider_setup)
        
        self.numberOfTeeth_textbox.textChanged.connect(self.tooth_number_status)
        self.adjustPinchFade_combox.currentIndexChanged.connect(self.update_visibility)
        self.adjustPinchFadeIndex_combox.currentIndexChanged.connect(self.update_visibility)
        self.numberOfTeeth_textbox.hide()
        self.numberOfTeeth_label.hide()
        
        
        self.actionSave_as_PDF.triggered.connect(self.save_pdf)
        self.actionSave_as_PNG.triggered.connect(self.save_png)
        self.actionSave_as_TIFF.triggered.connect(self.save_tiff)
        self.actionSave_as_JPEG.triggered.connect(self.save_jpeg)
        self.actionSave_as_EPS.triggered.connect(self.save_eps)
        
        self.actionExport_as_Excel.triggered.connect(self.export_as_excel)
        
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Josh\'s Cross Section Tool"))
        self.selectFile_button.setText(_translate("MainWindow", "Select File"))
        self.mainUpdate_button.setText(_translate("MainWindow", "Update Figure"))
        self.mainUpdate_button.setShortcut(_translate("MainWindow", "Return"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Main"))
        self.formationsUpdate_button.setText(_translate("MainWindow", "Update Figure"))
        self.formationsUpdate_button.setShortcut(_translate("MainWindow", "Return"))
        self.TopDepthOfFormations_label.setText(_translate("MainWindow", "Top Depth of Formations"))
        self.formationPolygons_label.setText(_translate("MainWindow", "Formation Polygons"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Formations"))
        self.styleUpdate_button.setText(_translate("MainWindow", "Update Figure"))
        self.styleUpdate_button.setShortcut(_translate("MainWindow", "Return"))
        self.formationStyle_lable.setText(_translate("MainWindow", "Formation Style"))
        self.sampleType_label.setText(_translate("MainWindow", "Sample Type"))
        self.sampleChangesWithDepth_label.setText(_translate("MainWindow", "Does sample type change with depth?"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Style"))
        self.menuFile.setTitle(_translate("MainWindow", "Cross Section"))
        self.menuSave.setTitle(_translate("MainWindow", "Save"))
        self.menuExport_Data.setTitle(_translate("MainWindow", "Export Data"))
        self.actionSave_as_PDF.setText(_translate("MainWindow", "Save as PDF"))
        self.actionSave_as_PNG.setText(_translate("MainWindow", "Save as PNG"))
        self.actionSave_as_JPEG.setText(_translate("MainWindow", "Save as JPEG"))
        self.actionSave_as_TIFF.setText(_translate("MainWindow", "Save as TIFF"))
        self.actionSave_as_EPS.setText(_translate("MainWindow", "Save as EPS"))
        self.actionExport_as_Excel.setText(_translate("MainWindow", "Export as Excel"))
        self.actionExport_as_CSV.setText(_translate("MainWindow", "Export as CSV"))
#######################################################################################################################################################################
    def teeth_of_fade(self):
        """
        Takes the number inputted into the textbox and converts that into the values required to create that many teeth
        in the fade
        """
        
        #Collects the row and index of the fade that is being edited
        row = self.adjustPinchFadeFormation_combox.currentData()
        index = self.adjustPinchFadeIndex_combox.currentIndex()
        #Collects the desired tooth number
        current_teeth_num = int(self.numberOfTeeth_textbox.toPlainText())
        
        #Changes the values used for that fade. Each fade has two values [linspace number, number of tiles]
        self.number_of_teeth_dict[row][0+(2*index)] = (current_teeth_num * 2) - 1
        self.number_of_teeth_dict[row][1+(2*index)] = current_teeth_num - 1
        
        
        
    def update_visibility(self):
        """
        Shows or hides the number of teeth textbox depending on the dropdown selections.
        This is to avoid confusion and programmatic issues with number being entered when they shouldnt be.        
        """        
        # Get the current values
        fade_text = self.adjustPinchFade_combox.currentText()
        fade_index_data = self.adjustPinchFadeIndex_combox.currentData()

        # Check if currently fade is being edited and that there is a fade to edit in this formation. Then updates visibility
        if fade_text == "Fade" and fade_index_data != "No Fade":
            self.numberOfTeeth_textbox.show()
            self.numberOfTeeth_label.show()
        else:
            self.numberOfTeeth_textbox.hide()
            self.numberOfTeeth_label.hide()
        

    def pinch_fade_slider(self, value):
        """ 
        Takes the value from the adjustPinchFade_slider and  changes the value of the pinch or fade at the selected formation and index.
        This function automatically collects the value from the slider in the 'value' variable
        """
        #Collects the style being edited, its row and index. 
        pinch_or_fade = self.adjustPinchFade_combox.currentText()
        row = self.adjustPinchFadeFormation_combox.currentData()
        index = self.adjustPinchFadeIndex_combox.currentIndex()
        
        #Adds an index correction so that it accesses the correct value in the list [left_borehole_distance, middle_distance, right_borehole_distance]
        #Lists of the previous format are all concatenated so that a single formation has one list containing all the needed values 
        index_correction = 3*index
        
        #Checks for the style being edited and changes the middle_distance value associated with that point
        if pinch_or_fade == 'Pinch':
            self.pinch_correction_dict[row][1+index_correction] = value
        else:
            self.fade_correction_dict[row][1+index_correction] = value
        #Changes the status of the slider change for the flow of data later
        self.pinchFadeslider_changed = True    


    def pinch_fade_slider_setup(self):
        """
        Populates the labels above the slider and also creates the min, max and pointer values for the slider when a pinch or fade is selected.
        The left side of the slider if the left borehole's distance from the start of the cross section, the right side is the right borehole's distance
        The pointer value is by default the middle between the two, but will stay wherever you move it
        """
        #Gathers the row, type of style being edited and the data of the selection. The data can either be an index or a string
        current_value = self.adjustPinchFadeIndex_combox.currentData()
        pinch_or_fade = str(self.adjustPinchFade_combox.currentText())
        row = self.adjustPinchFadeFormation_combox.currentData()
        
        #Clears the labels and the ticks on the slider
        self.adjustPinchFadeMin_label.setText('')
        self.adjustPinchFadeMax_label.setText('')
        self.adjustPinchFade_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        
       
        if current_value in ['No Pinch', 'No Fade']:
            return  # Skip the rest if there's no pinch or fade
        
        else: #Creates an index correction so that it accesses the correct value in the list [left_borehole_distance, middle_distance, right_borehole_distance]
              #Lists of the previous format are all concatenated so that a single formation has one list containing all the needed values
            current_value = int(current_value)
            value_correction = 3 * current_value
            
        if pinch_or_fade == 'Pinch':
            self.adjustPinchFade_slider.blockSignals(True)  # Block signals to avoid accidentally changing the middle value
            self.adjustPinchFade_slider.setMinimum(int(self.pinch_correction_dict[row][0 + value_correction]))
            self.adjustPinchFade_slider.setMaximum(int(self.pinch_correction_dict[row][2 +value_correction ]))
            self.adjustPinchFade_slider.setValue(int(self.pinch_correction_dict[row][1 + value_correction]))
            self.adjustPinchFade_slider.blockSignals(False)  # Unblock signals
            
            self.adjustPinchFade_slider.setTickPosition(QtWidgets.QSlider.TicksBelow) #Adds ticks below the slider
        
            #Adds the distance to the labels above the slider
            self.adjustPinchFadeMin_label.setText(str(self.pinch_correction_dict[row][0 + value_correction]) + ' ft')
            self.adjustPinchFadeMax_label.setText(str(self.pinch_correction_dict[row][2 + value_correction]) + ' ft')
            
            #Automatically adjust the size of the labels to fit the text
            self.adjustPinchFadeMin_label.adjustSize()
            self.adjustPinchFadeMax_label.adjustSize()
            
        else:
            self.adjustPinchFade_slider.blockSignals(True)  # Block signals to avoid accidentally changing the middle value
            self.adjustPinchFade_slider.setMinimum(int(self.fade_correction_dict[row][0 + value_correction]))
            self.adjustPinchFade_slider.setMaximum(int(self.fade_correction_dict[row][2 + value_correction]))
            self.adjustPinchFade_slider.setValue(int(self.fade_correction_dict[row][1 + value_correction]))
            self.adjustPinchFade_slider.blockSignals(False)  # Unblock signals
            
            self.adjustPinchFade_slider.setTickPosition(QtWidgets.QSlider.TicksBelow) #Adds ticks below the slider
            
            #Adds the distance to the labels above the slider
            self.adjustPinchFadeMin_label.setText(str(self.fade_correction_dict[row][0 + value_correction]) + ' ft')
            self.adjustPinchFadeMax_label.setText(str(self.fade_correction_dict[row][2 + value_correction]) + ' ft')
            
            #Automatically adjust the size of the labels to fit the text
            self.adjustPinchFadeMin_label.adjustSize()
            self.adjustPinchFadeMax_label.adjustSize()
            
        
        

    def pinch_fade_index_combox(self):
        """
        Populates the pinch fade index dropdown with the appropriate values. It will fill with W# and direction if a pinch or fade exists for that formation and
        will fill with No Fade or No Pinch if not
        """
        
        #Clear the box so that the only options are the new options
        #If this is not done, options will continue to add even if a new file is selected
        self.adjustPinchFadeIndex_combox.clear()
        
        #Collect the style being edited and the formation being edited
        pinch_or_fade = str(self.adjustPinchFade_combox.currentText())
        row = self.adjustPinchFadeFormation_combox.currentData()
        
        #If the style is pinch then check the length of the the list for that formation
        if pinch_or_fade == 'Pinch':
            current_list = self.pinch_correction_dict[row] #Gather the data list
            well_list = self.pinch_well_dict[row] #Gather the well numbers associated
            number_of_pinches = int(len(current_list) / 3) #Calculate how many pinches are in this formation. Rounds to the nearest integer 
                                                           
            if number_of_pinches == 0: #If there is no pinch the previous calculation will round down to 0
                self.adjustPinchFadeIndex_combox.addItem('No Pinch', 'No Pinch') # This creates an entry with the text and data 'No Pinch'
            else:
                for pinch in range(number_of_pinches): #Loops for each pinch that is in that formation
                    self.adjustPinchFadeIndex_combox.addItem(str(well_list[pinch]), str(pinch)) # Creates an entry with the text of W-# direction, and data being an index
        else: # If the style is not pinch then it must be fade                                  # This allows a better understanding of what is being edited and still creates an easy way to acess the correct list location with the index
            current_list = self.fade_correction_dict[row] #Gather the data list
            well_list = self.fade_well_dict[row] #Gather the well numbers associated
            number_of_fades = int(len(current_list) / 3) #Calculate how many fades are in this formation. Rounds to the nearest integer
            if number_of_fades == 0:
                self.adjustPinchFadeIndex_combox.addItem('No Fade', 'No Fade') # This creates an entry with the text and data 'No Fade'
            else:
                for fade in range(number_of_fades):
                    self.adjustPinchFadeIndex_combox.addItem(str(well_list[fade]), str(fade)) # Creates an entry with the text of W-# direction, and data being an index
                                                                                                # This allows a better understanding of what is being edited and still creates an easy way to acess the correct list location with the index
        self.pinch_fade_slider_setup() #Calls the function to initially set up the slider


    def create_pinch_fade_correction_dict(self):
        """ 
        Creates dictionaries with pinch/fade lists, also creates well dictionaries for both and a tooth number dictionary.
        This dictionaries are locations for the user to edit these features in the front end and create some sort of change in the plot
        """
        
        # Defining all the empty dictionaries
        self.pinch_correction_dict = {}
        self.fade_correction_dict = {}
        
        self.pinch_well_dict = {}
        self.fade_well_dict = {}
        
        self.number_of_teeth_dict = {}
        
        #Loop for each row(formation) of the style array
        for row in range(self.style_array.shape[0]):
            #Create empty lists for each row that can be used to assign to each row(formation) in the dictionary
            pinch_list = []
            fade_list = []
            fade_well_list = []
            pinch_well_list = []
            number_of_teeth_list = []
            
            #Loop for each column(well) in the style array
            for col in range(self.style_array.shape[1]):
                
                
                if self.style_array[row, col] == 'f': #Check for fading
                    direction = check_left_right(self.style_array[row], col) #Collect the direction to decide which locations values to add in what order
                    
                    if direction == 'left':
                        fade_list.append(self.locations[col-1]) #Add the left well first 
                        middle = (self.locations[col-1] + self.locations[col]) / 2 #Calculate the midpoint
                        fade_list.append(middle) #Add the midpoint second
                        fade_list.append(self.locations[col]) #Add the right well third
                        fade_well_list.append('W-'+ str(self.w_num[col]) + ' Left') #Create a string with the form W-# direction for ease of use to the user
                        number_of_teeth_list.append(7) # Add a default value for the teeth
                        number_of_teeth_list.append(3) # Add a default value for the teeth
                        
                    elif direction == 'right':
                        fade_list.append(self.locations[col]) #Add the left well first
                        middle = (self.locations[col] + self.locations[col+1]) / 2 #Calculate the midpoint
                        fade_list.append(middle) #Add the midpoint second
                        fade_list.append(self.locations[col+1]) #Add the right well third
                        fade_well_list.append('W-'+ str(self.w_num[col]) + ' Right') #Create a string with the form W-# direction for ease of use to the user
                        number_of_teeth_list.append(7) # Add a default value for the teeth
                        number_of_teeth_list.append(3) # Add a default value for the teeth
                        
                    elif direction == 'both': #In the case of both, the left point will be added first so that it is easy to read options as top-down = left-right
                        fade_list.append(self.locations[col-1]) #Add the left well first
                        middle = (self.locations[col-1] + self.locations[col]) / 2 #Calculate the midpoint
                        fade_list.append(middle) #Add the midpoint second
                        fade_list.append(self.locations[col]) #Add the right well third
                        fade_well_list.append('W-'+ str(self.w_num[col]) + ' Left') #Create a string with the form W-# direction for ease of use to the user
                        number_of_teeth_list.append(7) # Add a default value for the teeth
                        number_of_teeth_list.append(3) # Add a default value for the teeth
                        
                        fade_list.append(self.locations[col]) #Add the left well first
                        middle = (self.locations[col] + self.locations[col+1]) / 2 #Calculate the midpoint
                        fade_list.append(middle) #Add the midpoint second
                        fade_list.append(self.locations[col+1]) #Add the right point third
                        fade_well_list.append('W-'+ str(self.w_num[col]) + ' Right') #Create a string with the form W-# direction for ease of use to the user
                        number_of_teeth_list.append(7) # Add a default value for the teeth
                        number_of_teeth_list.append(3) # Add a default value for the teeth
                        
                elif self.style_array[row, col] == 'p': #Check for pinching
                    direction = check_left_right(self.style_array[row], col) #Collect the direction to decide which locations values to add in what order
                    
                    if direction == 'left':
                        pinch_list.append(self.locations[col-1]) #Add the left point first
                        middle = (self.locations[col-1] + self.locations[col]) / 2 #Calculate the midpoint
                        pinch_list.append(middle) #Add the midpoint second
                        pinch_list.append(self.locations[col]) #Add the right point third
                        pinch_well_list.append('W-'+ str(self.w_num[col]) + ' Left') #Create a string with the form W-# direction for ease of use to the user
    
                    elif direction == 'right':
                        pinch_list.append(self.locations[col]) #Add the left point first
                        middle = (self.locations[col] + self.locations[col+1]) / 2
                        pinch_list.append(middle) #Add the midpoint second
                        pinch_list.append(self.locations[col+1]) #Add the right point third
                        pinch_well_list.append('W-'+ str(self.w_num[col]) + ' Right') #Create a string with the form W-# direction for ease of use to the user
    
                    elif direction == 'both': #In the case of both, the left point will be added first so that it is easy to read options as top-down = left-right
                        pinch_list.append(self.locations[col-1]) #Add the left point first
                        middle = (self.locations[col-1] + self.locations[col]) / 2
                        pinch_list.append(middle) #Add the midpoint second
                        pinch_list.append(self.locations[col]) #Add the right point third
                        pinch_well_list.append('W-'+ str(self.w_num[col]) + ' Left') #Create a string with the form W-# direction for ease of use to the user
    
                        pinch_list.append(self.locations[col]) #Add the left point first
                        middle = (self.locations[col] + self.locations[col+1]) / 2
                        pinch_list.append(middle) #Add the midpoint second
                        pinch_list.append(self.locations[col+1]) #Add the right point third
                        pinch_well_list.append('W-'+ str(self.w_num[col]) + ' Right') #Create a string with the form W-# direction for ease of use to the user

            
            # Check if there is no pinching or fading in the formation and add that to the dictionary
            if len(pinch_list) == 0:
                pinch_list.append('No Pinch')
                pinch_well_list.append("No Pinch")
            if len(fade_list) == 0:
                fade_list.append('No Fade')
                fade_well_list.append('No Fade')
                number_of_teeth_list.append('No Fade')
            
            
            #Create a key (row number) and definition (list) for each formation
            self.pinch_correction_dict[row] = pinch_list
            self.fade_correction_dict[row] = fade_list
            
            self.pinch_well_dict[row] = pinch_well_list
            self.fade_well_dict[row] = fade_well_list
            
            self.number_of_teeth_dict[row] = number_of_teeth_list
            
##########################################################################################################################################
    
    def formation_polygons_combo_box(self):
        """ 
        Populates the formation polygons and pinch fade formations dropdowns with formation names from the selected file
        """
        #Clear the dropdowns so that values can be added
        self.formationPolygons_combox.clear()
        self.adjustPinchFadeFormation_combox.clear()
        
        index=0 #Initiate a value that will be used as the data value for the dropdowns
        for form in self.formations_list[:-1]: #Exclude the last value in the formation list because that is the bottom or TD
            self.formationPolygons_combox.addItem(form, index) #Add the formation to the dropdown with the index as the data
            self.adjustPinchFadeFormation_combox.addItem(form, index) #Add the formation to the dropdown with the index as the data
            index += 1 #Increment the index
            
            
    def create_formation_polygons_table(self):
        """ 
        Populates the formation polygons table with the top, bottom and distance values of a polygon
        """
        #Pulls the currently selected formation and its polygon
        index = self.formationPolygons_combox.currentData()
        polygon = self.formation_polygons[index]
        
        #Creates the shape the table needs to be to fit the polygon
        self.formationPolygons_table.setRowCount(polygon.shape[0])
        self.formationPolygons_table.setColumnCount(polygon.shape[1])
        
        #Labels the rows
        self.formationPolygons_table.setVerticalHeaderLabels(['Formation Top', 'Formation Bottom', 'Distance'])
        
        #Loops through the polygon array
        for i in range(polygon.shape[0]):
            for j in range(polygon.shape[1]):
                item = str(polygon[i, j])
                self.formationPolygons_table.setItem(i, j, QtWidgets.QTableWidgetItem(item)) #Adds each value to the table
                
        self.formationPolygons_table.setFont(self.table_font) #Set the font size larger
                
                
    def update_formation_polygon(self):
        """ 
        Updates the formation polygon array with any changes made by the user
        """
        #Pulls the currently selected formation and its polygon
        index = self.formationPolygons_combox.currentData()
        polygon = self.formation_polygons[index]
        
        #Loops through the polygon array
        for i in range(polygon.shape[0]):
            for j in range(polygon.shape[1]):
                item = self.formationPolygons_table.item(i, j) #Pulls the item in the polygon table
                polygon[i, j] = float(item.text()) #Converts it to a usable value and assigns it to the correct location
        
    
    
                
##########################################################################################################################################################

    def create_formations_table(self):
        """ 
        Populates the Top Depth of Formations table with data from the selected excel sheet
        """
        #Creates the shape the table needs to be for the data
        self.formations_table.setRowCount(self.formations_array.shape[0]+1)
        self.formations_table.setColumnCount(self.formations_array.shape[1])
        
        #Creates the W-# labels for each column of the table
        self.w_num_headers = [ "W-" + str(w) for w in self.w_num]
        row_headers = self.formations_list #Collects formation names to use as row labels
        row_headers.append("Distance") #Labels the last column as Distance
        
        #Sets the labels for the rows and columns
        self.formations_table.setVerticalHeaderLabels(self.formations_list)
        self.formations_table.setHorizontalHeaderLabels(self.w_num_headers)
        
        #Loops through the formations array
        for i in range(self.formations_array.shape[0]):
            for j in range(self.formations_array.shape[1]):
                item = str( self.formations_array[i,j]) 
                self.formations_table.setItem(i, j, QtWidgets.QTableWidgetItem(item)) #Add the values from the array to the table
        
                dist = str(self.locations[j])
                self.formations_table.setItem(self.formations_array.shape[0], j,  QtWidgets.QTableWidgetItem(dist)) #Add location values to the last row
                
        self.formations_table.setFont(self.table_font) #Set the font size larger
                
                
                
    def update_formations_array(self):
        """ 
        Updates the formation tops array when the Top Depth of Formations table is changed. That way any value that is changed within the program can be
        reflected in an exported excel sheet and in the plot
        """
        #Loop through the formation array
        for row in range(self.formations_array.shape[0]):
            for col in range(self.formations_array.shape[1]):
                item = self.formations_table.item(row, col) #Pulls the item in the formation table
                self.formations_array[row, col] = float(item.text()) #Converts it to a usable value and assigns it to the correct location
            
                
                
    def create_style_table(self):
        """
        Populates the data for formation style, sample type and colors tables.
        """
        #Create the table shape required for the data
        self.style_table.setRowCount(self.style_array.shape[0])
        self.style_table.setColumnCount(self.style_array.shape[1])
        
        #Labels the rows and columns with previously created labels or formations and W-#
        self.style_table.setVerticalHeaderLabels(self.formations_list)
        self.style_table.setHorizontalHeaderLabels(self.w_num_headers)
        
        #Loops through the style_array
        for i in range(self.style_array.shape[0]):
            for j in range(self.style_array.shape[1]):
                self.style_table.setItem(i, j, QtWidgets.QTableWidgetItem(self.style_array[i, j])) #Add style items to the 
                
        
        self.style_table.setFont(self.table_font) #Set the font size larger
        
        #Creates the table shape required to have 1 color for each formation
        self.colors_table.setRowCount(self.style_array.shape[0]-1)
        self.colors_table.setColumnCount(1)
        
        #Labels the formations and the column
        self.colors_table.setHorizontalHeaderLabels(["Formations Colors"])
        self.colors_table.setVerticalHeaderLabels(self.formations_list[:-1])
        self.colors_table.setColumnWidth(0, 170) #Sets the column width to fit the widget
        
        #Creates the sample type table with 1 row and the necessary columns
        self.sampleType_table.setRowCount(1)
        self.sampleType_table.setColumnCount(self.style_array.shape[1])
        
        #Labels each W-# and the row
        self.sampleType_table.setHorizontalHeaderLabels(self.w_num_headers)
        self.sampleType_table.setVerticalHeaderLabels(['Sample Type'])
        
        #Loops through the style array columns
        for col in range(self.style_array.shape[1]):
            samp_type = str(self.core_or_cuttings[col]) #Pulls a values from each index in the sample type array
            self.sampleType_table.setItem(0, col, QtWidgets.QTableWidgetItem(samp_type)) #Adds these to the table
            
        
                
    def update_style_array(self):
        """ 
        Updates the style array with changes made by the user
        """
        #Loops through the style array
        for row in range(self.style_array.shape[0]):
            for col in range(self.style_array.shape[1]):
                item = self.style_table.item(row, col) #Pulls an item from the table
                self.style_array[row, col] = str(item.text()) #Converts the item to a usable value and inserts it into the appropriate location
                
                
    def update_colors_list(self):
        """ 
        Updates the color list if any colors are added by the user
        """
        #Uses try to avoid errors if colors are not added
        try:
            self.colors_list = [] #Create an empty color list
            #Loop through the formations
            for row in range(self.style_array.shape[0]-1):
                color = self.colors_table.item(row, 0) # Pulls the colors from the table 
                self.colors_list.append(str(color.text())) # Adds the colors to the list
        except:
            self.color_list = [] #Clear the list if errors are encountered
            pass #If any error is encountered then just move on and ignore all this
#############################################################################################################
        
    def update_sample_type(self):
        pass
        
    def sample_changes(self):
        """ 
        This expands the sample type table to allow changes in sample type at all formation contacts
        """
        if self.sampleType_combox.currentData():
            self.sampleType_table.setRowCount(self.style_array.shape[0])
            self.sampleType_table.setColumnCount(self.style_array.shape[1])
            
            self.sampleType_table.setVerticalHeaderLabels(self.formations_list)
            self.sampleType_table.setHorizontalHeaderLabels(self.w_num_headers)
            
            for row in range(self.style_array.shape[0]):
                for col in range(self.style_array.shape[1]):
                    samp_type = str(self.core_or_cuttings[col])
                    self.sampleType_table.setItem(row, col, QtWidgets.QTableWidgetItem(samp_type))
        else:
            #Creates the sample type table with 1 row and the necessary columns
            self.sampleType_table.setRowCount(1)
            self.sampleType_table.setColumnCount(self.style_array.shape[1])
            
            #Labels each W-# and the row
            self.sampleType_table.setHorizontalHeaderLabels(self.w_num_headers)
            self.sampleType_table.setVerticalHeaderLabels(['Sample Type'])
            
            #Loops through the style array columns
            for col in range(self.style_array.shape[1]):
                samp_type = str(self.core_or_cuttings[col]) #Pulls a values from each index in the sample type array
                self.sampleType_table.setItem(0, col, QtWidgets.QTableWidgetItem(samp_type)) #Adds these to the table
            
#############################################################################################################                    
    
        


    def formation_updated_status(self):
        self.formations_updated = True
        
    def style_updated_status(self):
        self.style_updated = True

    def polygon_updated_status(self):
        self.polygon_updated = True

    def sample_type_updated_status(self):
        self.sampleType_updated = True
        
    def colors_status(self):
        self.colors_updated = True
        
    def tooth_number_status(self):
        self.toothNumber_changed = True
            
##################################################################################################################################################          
    def update_figure(self):
        plt.close()

        # Early exits for simple changes that don't require lots of calculations
        if self.toothNumber_changed:
            self.handle_tooth_number_change()
            return

        if self.pinchFadeslider_changed:
            self.handle_pinch_fade_slider_change()
            return

        # Handle grouped updates systematically
        if self.formations_updated:
            self.handle_formations_update()

        if self.style_updated:
            self.handle_style_update()

        if self.polygon_updated:
            self.handle_polygon_update()

        if self.sampleType_updated:
            self.handle_sample_type_update()

        if self.colors_updated:
            self.handle_colors_update()

        # Final updates
        self.create_plot()
        self.pinch_fade_index_combox()
        self.create_formation_polygons_table()

    # Modular Methods for Specific Updates
    def handle_tooth_number_change(self):
        self.teeth_of_fade()
        self.calculate_polygons()
        self.create_plot()
        self.create_formation_polygons_table()
        self.numberOfTeeth_textbox.clear()
        self.toothNumber_changed = False

    def handle_pinch_fade_slider_change(self):
        self.calculate_polygons()
        self.create_plot()
        self.create_formation_polygons_table()
        self.pinchFadeslider_changed = False

    def handle_formations_update(self):
        self.update_formations_array()
        self.create_initial_polygon_list()
        self.calculate_polygons()
        self.formations_updated = False

    def handle_style_update(self):
        self.update_style_array()
        self.create_pinch_fade_correction_dict()
        self.formation_polygons_combo_box()
        self.calculate_polygons()
        self.style_updated = False

    def handle_polygon_update(self):
        self.update_formation_polygon()
        self.polygon_updated = False

    def handle_sample_type_update(self):
        self.update_sample_type()
        self.sampleType_updated = False

    def handle_colors_update(self):
        self.update_colors_list()
        self.colors_updated = False

#####################################################################################################################################################        
    def select_file (self):
        fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', '')
        self.filepath = fname[0]
        
    
        self.create_initial_info()
        self.create_pinch_fade_correction_dict()
        self.formation_polygons_combo_box()
        self.create_initial_polygon_list()
        self.calculate_polygons()
        self.create_plot()
        self.create_formations_table()
        self.create_style_table()
        
        self.pinch_fade_index_combox()
        self.create_formation_polygons_table()
        
        
    def create_plot (self):
        top_of_bottom = np.max(self.formations_array[-1])
        fig, ax = plt.subplots(figsize=(24, 12))

        ax.fill_between(self.distance, top_of_bottom, self.elev)
        ax.plot(self.distance, self.elev, color='k', linewidth=0.8)
        
        runs = 0
        for formation in self.formation_polygons:
            try:
                ax.fill_between(formation[-1], formation[0], formation[1], color=self.colors_list[runs])
                runs+=1
            except:
                ax.fill_between(formation[-1], formation[0], formation[1])
 
        for n in range(len(self.w_num)):
            ax.vlines(self.locations[n], color='k', ymin=(self.formations_array[-1, n] -10), ymax=self.well_elev[n])
            ax.annotate(self.w_num[n], (self.locations[n]-50, self.well_elev[n]+10))
                
        ax.set_xlabel("Distance (ft)")
        ax.set_ylabel('Elevation (ft)')
    
        image_buffer = io.BytesIO()
        fig.savefig(image_buffer, format='png')
        image_buffer.seek(0)
        # Convert buffer data to QPixmap and display it
        plot_image = image_buffer.getvalue()
        self.pixmap = QtGui.QPixmap()
        success = self.pixmap.loadFromData(plot_image)

        if success:
            self.main_xsecplot.setPixmap(self.pixmap)
                
            
        
        
    
    def create_initial_info (self):
        df_elev = pd.read_excel(self.filepath, sheet_name='Elev')
        df_cross = pd.read_excel(self.filepath, sheet_name='Xsecs')

        #Here we split the well info sheet into formations and styles
        df_formations = df_cross.set_index('W_NUM').loc[:, 'FORM_START' : 'STYLE_START'].drop(columns=['FORM_START', 'STYLE_START'])
        df_style      = df_cross.set_index('W_NUM').loc[:, 'STYLE_START':'CORE_OR_CUTTINGS'].drop(columns=['STYLE_START', 'CORE_OR_CUTTINGS'])
        
        #This creates an array that can be plotted later. Surface elevation
        self.elev = df_elev['LiDAR_Elev'].tolist()
        self.distance = df_elev["ACTUAL_DISTANCE"].tolist()
        self.elev_array = np.array([self.elev, self.distance])

        self.w_num = df_cross['W_NUM'].tolist()
        self.core_or_cuttings = df_cross['CORE_OR_CUTTINGS'].tolist()

        #This extracts the distances for each well and the elevation of each well
        self.locations = df_cross['DIST_FT'].tolist()
        self.well_elev = np.array(df_cross['DEM_ELEV'].tolist())
        
        ################################################################################################################################################

        #This creates a list of all the formation names from the formation dataframe column headers
        self.formations_list = df_formations.columns.tolist()

        #This creates an array of the formation tops
        all_formations = []
        for formation in self.formations_list:
            temp_list = df_formations[formation].tolist()
            all_formations.append(temp_list)
        self.formations_array = np.array(all_formations)

        #Creates a mask that is used for the true formation depth calculation later
        not_elev = self.formations_array != 0
        #Creates an array of repeated well elevations that is used to calculate true formation depth
        elev_stack = np.repeat([self.well_elev], self.formations_array.shape[0], axis=0)

        #Calculates true formation depth by the difference of elevation and formation top only for values that arent equal to 0
        self.formations_array[not_elev] = elev_stack[not_elev] - self.formations_array[not_elev]
        #Calculates true formation depth by the sum of elevation and formation top for the values that are 0
        self.formations_array[~not_elev] = elev_stack[~not_elev] + self.formations_array[~not_elev]

        #########################################################################################################################################################

        #Creates a list of style column headers
        style_columns = df_style.columns.tolist()

        #Creates an array of the style indicators that can be used for the polygon calculation decisions
        all_styles = []
        for style in style_columns:
            temp_list = df_style[style].tolist()
            all_styles.append(temp_list)
        self.style_array = np.array(all_styles).astype('U')

        #####################################################################################################################################################
            
    def create_initial_polygon_list(self):
        
        #Creates a copy of the formation array so that the original is preserved
        big_array = np.copy(self.formations_array)

        #Creates initial polygons for each formation, making sure that if the top of the formation is np.nan the bottom is too. 
        #Also makes sure that if the formation below has np.nan as a value, it searches the next one down to make sure it has a number in the formation bottom
        self.initial_polygon_list = []
        for row in range(big_array.shape[0] - 1):
            first_row = np.copy(big_array[row])
            nan_template = np.isnan(first_row)

            second_row = np.copy(big_array[row + 1])
            second_row[nan_template] = np.nan
            nan_second = np.isnan(second_row)

            run = 2
            while not np.array_equal(nan_template, nan_second):
                values_needed = nan_template != nan_second
                second_row[values_needed] = big_array[row + run][values_needed]
                run += 1
                nan_second = np.isnan(second_row)
            #Append each initial polygon to a list where they can be accessed during the final polygon calculation
            self.initial_polygon_list.append(np.array([first_row, second_row]))
            
            
        ########################################################################################################################################################

    
    def calculate_polygons(self):
        #######################################################################################################################################################
        #######################################################################################################################################################
        #######################################################################################################################################################
        # The final polygon creation process
        # Each polygon will be created in the same form 3-rows, 2Dimensions
        # Row-1 is the formation top
        # Row-2 is the formation bottom
        # Row-3 is the corresponding x value for the depths in rows 1&2
        # Polygons will not necessarily be of the same length, this is why they are added to a list and calulated seperately.
        # That is also why the polygons all will contain their own x values within them.
        ########################################################################################################################################################
        self.formation_polygons = []
        fade_teeth_offset = self.locations[-1] * 0.01

        for row in range(len(self.initial_polygon_list)):
        #Calculates the polygons for formations that fade
            total_stack = self.initial_polygon_list[row].copy()
            total_stack = np.vstack((total_stack, self.locations))
            sorted_fade_index = 'NO'
            midpoint_correction_index = 0 #Used to keep track of which number to use in the midpoint correction list for this row. Found in pinch_fade_correction_dict
            tooth_index_correction = 0
           
            
            if np.any(self.style_array[row] == 'f'):

                fade_index = np.where(self.style_array[row] == 'f')[0]
                sorted_fade_index = np.sort(fade_index)
                insert_index_correction = 0

                for fade in fade_index:
                    direction = check_left_right(self.style_array[row], fade)
                    
            #Calculates the fade polygon if the formation fades left
                    if direction == 'left':
                        insert_location = fade + insert_index_correction
                        #Check for interlocking vs pool case
                        if row != 0:
                            #In interlocking cases, the above formation will be blocky and the below formation will have the teeth
                            if np.all(self.style_array[row-1, fade-1:fade+1] == ['f', 'n']): #Interlocking above
                               
                                #Calculate the universal values for this interlocking figure
                                midpoint = self.fade_correction_dict[row][1 + midpoint_correction_index]
                                midpoint_correction_index += 3
                                teeth_point = midpoint + fade_teeth_offset
                                #Calculate the bottom slope values
                                bottom_slope = (self.initial_polygon_list[row+1][0, fade-1] - self.initial_polygon_list[row][1, fade] ) / (self.locations[fade-1] - self.locations[fade])
                                yintercept = self.initial_polygon_list[row][1, fade] - (bottom_slope * self.locations[fade])
                                bottom_midpoint_elev = (bottom_slope * midpoint) + yintercept
                                bottom_teeth_elev = (bottom_slope * teeth_point) + yintercept
                                #Calculate the top elev with thickness and bottom midpoint elevation
                                top_slope = (self.initial_polygon_list[row][0, fade] - self.initial_polygon_list[row-1][0, fade-1]) / (self.locations[fade] - self.locations[fade-1])
                                yintercept = self.initial_polygon_list[row][0, fade] - (top_slope * self.locations[fade])
                                top_midpoint_elev = (top_slope * midpoint) + yintercept
                                
                                
                                

                                
                                #Calculate the points between top and bottom
                                peaks_and_troughs = np.linspace(bottom_midpoint_elev, top_midpoint_elev, num = self.number_of_teeth_dict[row][0+tooth_index_correction])
                                peak_locations  = np.hstack((np.tile([midpoint, teeth_point], self.number_of_teeth_dict[row][1+tooth_index_correction] ), midpoint))
                                bottom_array = np.hstack((np.tile([bottom_midpoint_elev, bottom_teeth_elev], self.number_of_teeth_dict[row][1+tooth_index_correction]), bottom_midpoint_elev))
                                

                                interlock_figure_array = np.vstack((peaks_and_troughs, bottom_array, peak_locations))
                                
                                total_stack = np.insert(total_stack, [insert_location], interlock_figure_array, axis=1)
                                insert_index_correction += self.number_of_teeth_dict[row][0+tooth_index_correction]
                                tooth_index_correction += 2
                                

                            elif np.all(self.style_array[row+1, fade-1:fade+1] == ['f', 'n']):#Creates a blocky polygon to draw over if the formation below interlocks
                                new_stack = np.array([[self.initial_polygon_list[row+1][0,fade+1]], [self.initial_polygon_list[row+1][1,fade+1]], [self.locations[fade+1]]])
                                total_stack = np.insert(total_stack, [insert_location+1], new_stack, axis=1)
                               


                            
                            else:
                                #Calculate the universal values for this interlocking figure
                                thickness = self.initial_polygon_list[row][0, fade] - self.initial_polygon_list[row][1, fade]
                                midpoint = self.fade_correction_dict[row][1 + midpoint_correction_index]
                                midpoint_correction_index += 3
                                teeth_point = midpoint + fade_teeth_offset
                                #Calculate the bottom slope values
                                bottom_slope = (self.initial_polygon_list[row+1][0, fade-1] - self.initial_polygon_list[row][1, fade] ) / (self.locations[fade-1] - self.locations[fade])
                                yintercept = self.initial_polygon_list[row][1, fade] - (bottom_slope * self.locations[fade])
                                bottom_midpoint_elev = (bottom_slope * midpoint) + yintercept
                                bottom_teeth_elev = (bottom_slope * teeth_point) + yintercept
                                #Calculate the top elev with thickness and bottom midpoint elevation
                                top_midpoint_elev = bottom_midpoint_elev + thickness

            
                                #Calculate the points between top and bottom
                                peaks_and_troughs = np.linspace(bottom_midpoint_elev, top_midpoint_elev, num = self.number_of_teeth_dict[row][0+tooth_index_correction])
                                peak_locations  = np.hstack((np.tile([midpoint, teeth_point], self.number_of_teeth_dict[row][1+tooth_index_correction]), midpoint))
                                bottom_array = np.hstack((np.tile([bottom_midpoint_elev, bottom_teeth_elev], self.number_of_teeth_dict[row][1+tooth_index_correction]), bottom_midpoint_elev))
                                    
                                
                                interlock_figure_array = np.vstack((peaks_and_troughs, bottom_array, peak_locations))
                                
                                total_stack = np.insert(total_stack, [insert_location], interlock_figure_array, axis=1)
                                insert_index_correction += self.number_of_teeth_dict[row][0+tooth_index_correction]
                                tooth_index_correction += 2


                #Calculates the fade polygon if the formation fades right
                    elif direction == 'right':
                        insert_location = fade + insert_index_correction
                        #Check for interlocking vs pool case
                        if row != 0:
                            #In interlocking cases, the above formation will be blocky and the below formation will have the teeth
                            if np.all(self.style_array[row-1, fade:fade+2] == ['n', 'f']): #Interlocking above
                                midpoint = self.fade_correction_dict[row][1 + midpoint_correction_index]
                                midpoint_correction_index += 3
                                teeth_point = midpoint - fade_teeth_offset

                                top_slope = (self.initial_polygon_list[row][0, fade] - self.initial_polygon_list[row-1][0, fade+1]) / (self.locations[fade] - self.locations[fade+1])
                                yintercept = self.finitial_polygon_list[row][0, fade] - (top_slope * self.locations[fade])
                                top_midpoint_elev = (top_slope * midpoint) + yintercept
                               

                                bottom_slope = (self.initial_polygon_list[row][1, fade] - self.initial_polygon_list[row-1][1, fade+1]) / (self.locations[fade] - self.locations[fade+1])
                                yintercept = self.initial_polygon_list[row][1, fade] - (bottom_slope * self.locations[fade])
                                bottom_midpoint_elev = (bottom_slope * midpoint) + yintercept
                                bottom_teeth_elev = (bottom_slope * teeth_point) + yintercept
                                
                                top_slope = (self.initial_polygon_list[row][0, fade] - self.initial_polygon_list[row-1][0, fade+1]) / (self.locations[fade] - self.locations[fade+1])
                                yintercept = self.initial_polygon_list[row][0, fade] - (top_slope * self.locations[fade])
                                top_midpoint_elev = (top_slope * midpoint) + yintercept

                                peaks_and_troughs = np.linspace(top_midpoint_elev, bottom_midpoint_elev, num=self.number_of_teeth_dict[row][0+tooth_index_correction])
                                peak_locations = np.hstack((np.tile([midpoint, teeth_point], self.number_of_teeth_dict[row][1+tooth_index_correction]), midpoint))
                                bottom_array = np.hstack((np.tile([bottom_midpoint_elev, bottom_teeth_elev], self.number_of_teeth_dict[row][1+tooth_index_correction]), bottom_midpoint_elev))
                                
                                
                                interlock_figure_array = np.vstack((peaks_and_troughs, bottom_array, peak_locations))
            
                                total_stack = np.insert(total_stack, [insert_location], interlock_figure_array, axis=1)
                                insert_index_correction += self.number_of_teeth_dict[row][0+tooth_index_correction]
                                tooth_index_correction += 2
                                
                                
                            elif np.all(self.style_array[row+1, fade:fade+2] == ['n', 'f']): #Creates a blocky polygon to draw over if the formation below interlocks
                                new_stack = np.array([[self.initial_polygon_list[row+1][0,fade+1]], [self.initial_polygon_list[row+1][1,fade+1]], [self.locations[fade+1]]])
                                total_stack = np.insert(total_stack, [insert_location+1], new_stack, axis=1)
                                insert_index_correction += 1
                                
                                
                    

                            
                            else:
                                thickness = self.initial_polygon_list[row][0, fade] - self.initial_polygon_list[row][1, fade]
                                midpoint = self.fade_correction_dict[row][1 + midpoint_correction_index]
                                midpoint_correction_index += 3
                                teeth_point = midpoint - fade_teeth_offset

                                bottom_slope = (self.initial_polygon_list[row][1, fade] - self.initial_polygon_list[row+1][0, fade+1]) / (self.locations[fade] - self.locations[fade+1])
                                yintercept = self.initial_polygon_list[row][1, fade] - (bottom_slope * self.locations[fade])
                                bottom_midpoint_elev = (bottom_slope * midpoint) + yintercept
                                bottom_teeth_elev = (bottom_slope * teeth_point) + yintercept

                                top_midpoint_elev = bottom_midpoint_elev + thickness

                                peaks_and_troughs = np.linspace(top_midpoint_elev, bottom_midpoint_elev, num=self.number_of_teeth_dict[row][0+tooth_index_correction])
                                peak_locations = np.hstack((np.tile([midpoint, teeth_point], self.number_of_teeth_dict[row][1+tooth_index_correction]), midpoint))
                                bottom_array = np.hstack((np.tile([bottom_midpoint_elev, bottom_teeth_elev], self.number_of_teeth_dict[row][1+tooth_index_correction]), bottom_midpoint_elev))
                                
                                
                                interlock_figure_array = np.vstack((peaks_and_troughs, bottom_array, peak_locations))

                                total_stack = np.insert(total_stack, [insert_location+1], interlock_figure_array, axis=1)
                                insert_index_correction += self.number_of_teeth_dict[row][0+tooth_index_correction]
                                tooth_index_correction += 2

                                

                    
                    
                    elif direction == 'both':
                        insert_location = fade + insert_index_correction
                        

                        #In interlocking cases, the above formation will be blocky and the below formation will have the teeth
                        if np.all(self.style_array[row-1, fade-1:fade+1] == ['f', 'n']): #Interlocks above
                            #Calculate the universal values for this interlocking figure
                            thickness = self.initial_polygon_list[row][0, fade] - self.initial_polygon_list[row][1, fade]
                            midpoint = self.fade_correction_dict[row][1 + midpoint_correction_index]
                            midpoint_correction_index += 3
                            teeth_point = midpoint + fade_teeth_offset
                            #Calculate the bottom slope values
                            bottom_slope = (self.initial_polygon_list[row+1][0, fade-1] - self.initial_polygon_list[row][1, fade] ) / (self.locations[fade-1] - self.locations[fade])
                            yintercept = self.initial_polygon_list[row][1, fade] - (bottom_slope * self.locations[fade])
                            bottom_midpoint_elev = (bottom_slope * midpoint) + yintercept
                            bottom_teeth_elev = (bottom_slope * teeth_point) + yintercept
                            #Calculate the top elev with thickness and bottom midpoint elevation
                            top_midpoint_elev = bottom_midpoint_elev + thickness


                            #Calculate the points between top and bottom
                            peaks_and_troughs = np.linspace(bottom_midpoint_elev, top_midpoint_elev, num = self.number_of_teeth_dict[row][0+tooth_index_correction])
                            peak_locations  = np.hstack((np.tile([midpoint, teeth_point], self.number_of_teeth_dict[row][1+tooth_index_correction]), midpoint))
                            bottom_array = np.hstack((np.tile([bottom_midpoint_elev, bottom_teeth_elev], self.number_of_teeth_dict[row][1+tooth_index_correction]), bottom_midpoint_elev))
                            
                            
                            interlock_figure_array = np.vstack((peaks_and_troughs, bottom_array, peak_locations))
                            
                            total_stack = np.insert(total_stack, [insert_location], interlock_figure_array, axis=1)
                            insert_index_correction += self.number_of_teeth_dict[row][0+tooth_index_correction]
                            
                                
                            #Creates a blocky polygon to draw over if the formation below interlocks
                        elif np.all(self.style_array[row+1, fade-1:fade+1] == ['f', 'n']): #Interlocks below
                            new_stack = np.array([[self.initial_polygon_list[row+1][0,fade+1]], [self.initial_polygon_list[row+1][1,fade+1]], [self.locations[fade+1]]])
                            total_stack = np.insert(total_stack, [insert_location+1], new_stack, axis=1)
                            insert_index_correction += 1
                            tooth_index_correction += 2
                            
                            


                            
                        else: #No interlocking
                            #Calculate the universal values for this interlocking figure
                            thickness = self.initial_polygon_list[row][0, fade] - self.initial_polygon_list[row][1, fade]
                            midpoint = self.fade_correction_dict[row][1 + midpoint_correction_index]
                            midpoint_correction_index += 3
                            teeth_point = midpoint + fade_teeth_offset
                            #Calculate the bottom slope values
                            bottom_slope = (self.initial_polygon_list[row][1, fade] - self.initial_polygon_list[row+1][0, fade-1]) / (self.locations[fade] - self.locations[fade-1])
                            yintercept = self.initial_polygon_list[row][1, fade] - (bottom_slope * self.locations[fade])
                            bottom_midpoint_elev = (bottom_slope * midpoint) + yintercept
                            bottom_teeth_elev = (bottom_slope * teeth_point) + yintercept
                            #Calculate the top elev with thickness and bottom midpoint elevation
                            top_midpoint_elev = bottom_midpoint_elev + thickness
                            

                            #Calculate the points between top and bottom
                            peaks_and_troughs = np.linspace(bottom_midpoint_elev, top_midpoint_elev, num = self.number_of_teeth_dict[row][0+tooth_index_correction])
                            peak_locations  = np.hstack((np.tile([midpoint, teeth_point],self.number_of_teeth_dict[row][1+tooth_index_correction]), midpoint))
                            bottom_array = np.hstack((np.tile([bottom_midpoint_elev, bottom_teeth_elev],self.number_of_teeth_dict[row][1+tooth_index_correction]), bottom_midpoint_elev))
                            
                            
                            interlock_figure_array = np.vstack((peaks_and_troughs, bottom_array, peak_locations))
                            
                            total_stack = np.insert(total_stack, [insert_location], interlock_figure_array, axis=1)
                            insert_index_correction += self.number_of_teeth_dict[row][0+tooth_index_correction]
                            tooth_index_correction += 2
                            
                            


                        insert_location = fade + insert_index_correction
                        #In interlocking cases, the above formation will be blocky and the below formation will have the teeth
                        if np.all(self.style_array[row-1, fade:fade+2] == ['n', 'f']): #Interlocks above
                            midpoint = self.fade_correction_dict[row][1 + midpoint_correction_index]
                            midpoint_correction_index += 3
                            teeth_point = midpoint - fade_teeth_offset

                            top_slope = (self.initial_polygon_list[row][0, fade] - self.initial_polygon_list[row-1][0, fade+1]) / (self.locations[fade] - self.locations[fade+1])
                            yintercept = self.initial_polygon_list[row][0, fade] - (top_slope * self.locations[fade])
                            top_midpoint_elev = (top_slope * midpoint) + yintercept
                               

                            bottom_slope = (self.initial_polygon_list[row][1, fade] - self.initial_polygon_list[row-1][1, fade+1]) / (self.locations[fade] - self.locations[fade+1])
                            yintercept = self.initial_polygon_list[row][0, fade] - (bottom_slope * self.locations[fade])
                            bottom_midpoint_elev = (bottom_slope * midpoint) + yintercept
                            bottom_teeth_elev = (bottom_slope * teeth_point) + yintercept

                            peaks_and_troughs = np.linspace(top_midpoint_elev, bottom_midpoint_elev, num=self.number_of_teeth_dict[row][0+tooth_index_correction])
                            peak_locations = np.hstack((np.tile([midpoint, teeth_point], self.number_of_teeth_dict[row][1+tooth_index_correction]), midpoint))
                            bottom_array = np.hstack((np.tile([bottom_midpoint_elev, bottom_teeth_elev], self.number_of_teeth_dict[row][1+tooth_index_correction]), bottom_midpoint_elev))
                            
                            
                            interlock_figure_array = np.vstack((peaks_and_troughs, bottom_array, peak_locations))
                            
                            total_stack = np.insert(total_stack, [insert_location], interlock_figure_array, axis=1)
                            insert_index_correction += self.number_of_teeth_dict[row][0+tooth_index_correction]
                            tooth_index_correction += 2
                                
                            #Creates a blocky polygon to draw over if the formation below interlocks
                        elif np.all(self.style_array[row+1, fade:fade+2] == ['n', 'f']): #Interlocks below
                            new_stack = np.array([[self.initial_polygon_list[row+1][0,fade+1]], [self.initial_polygon_list[row+1][1,fade+1]], [self.locations[fade+1]]])
                            total_stack = np.insert(total_stack, [insert_location+1], new_stack, axis=1)
                            insert_index_correction += 1
                           


                            
                        else: #No interlocking
                            thickness = self.initial_polygon_list[row][0, fade] - self.initial_polygon_list[row][1, fade]
                            midpoint = self.fade_correction_dict[row][1 + midpoint_correction_index]
                            midpoint_correction_index += 3
                            teeth_point = midpoint - fade_teeth_offset

                            bottom_slope = (self.initial_polygon_list[row][1, fade] - self.initial_polygon_list[row+1][0, fade+1]) / (self.locations[fade] - self.locations[fade+1])
                            yintercept = self.initial_polygon_list[row][1, fade] - (bottom_slope * self.locations[fade])
                            bottom_midpoint_elev = (bottom_slope * midpoint) + yintercept
                            bottom_teeth_elev = (bottom_slope * teeth_point) + yintercept

                            top_midpoint_elev = bottom_midpoint_elev + thickness

                            peaks_and_troughs = np.linspace(top_midpoint_elev, bottom_midpoint_elev, num=self.number_of_teeth_dict[row][0+tooth_index_correction])
                            peak_locations = np.hstack((np.tile([midpoint, teeth_point], self.number_of_teeth_dict[row][1+tooth_index_correction]), midpoint))
                            bottom_array = np.hstack((np.tile([bottom_midpoint_elev, bottom_teeth_elev], self.number_of_teeth_dict[row][1+tooth_index_correction]), bottom_midpoint_elev))
                            
                            
                            interlock_figure_array = np.vstack((peaks_and_troughs, bottom_array, peak_locations))
                            
                            total_stack = np.insert(total_stack, [insert_location+1], interlock_figure_array, axis=1)
                            insert_index_correction += self.number_of_teeth_dict[row][0+tooth_index_correction]
                            tooth_index_correction += 2
                            
 
                            
        ########################################################################################################################################################

        #Calculates the polygons for formations that pinch
            if np.any(self.style_array[row] == 'p'):
                pinch_index = np.where(self.style_array[row] == 'p')[0]
                pinch_insert_correction = 0 #Keeps track of how many points have been added to the array to make sure next points are placed correctly
                midpoint_correction_index = 0
                
                
                
                
                for pinch in pinch_index:

                    if type(sorted_fade_index) != str:
                        #Check which fade indexes have a direction of both and double index correction accordingly
                        index_compared_to_fade  = np.searchsorted(sorted_fade_index, pinch)
                        for fade in sorted_fade_index[:index_compared_to_fade]:
                            fade_direction = check_left_right(self.style_array[row], fade)
                            if fade_direction == 'both':
                                pinch_insert_correction += 14
                            else:
                                pinch_insert_correction += 7

                    else:
                        pinch_insert_correction =  pinch_insert_correction


                    
                    #Figure out direction of pinch
                    direction = check_left_right(self.style_array[row], pinch)
                    #Calculate midpoint of next formation top
                    
                    
                    #Inserts the new data point into the polygon at the right location
                    if direction == 'left':
                        new_point = slope_calculator(self.formations_array, self.style_array, self.locations, row, pinch, direction, self.pinch_correction_dict[row][1+midpoint_correction_index])
                        midpoint_correction_index += 3
                        insert_location = pinch + pinch_insert_correction 
                        total_stack = np.insert(total_stack, insert_location, new_point.flatten(), axis=1)
                        pinch_insert_correction +=1
                        
                    #Adds the point to the right by adding one to the insert location index
                    elif direction == 'right':
                        new_point = slope_calculator(self.formations_array, self.style_array, self.locations, row, pinch, direction, self.pinch_correction_dict[row][1+midpoint_correction_index])
                        midpoint_correction_index += 3
                        insert_location = pinch + pinch_insert_correction + 1
                        total_stack = np.insert(total_stack, insert_location, new_point.flatten(), axis=1)
                        pinch_insert_correction +=1

                    #Combines the two methods from before to add in two points, one left and one right
                    elif direction == 'both':
                        new_point = slope_calculator(self.formations_array, self.style_array, self.locations, row, pinch, direction, self.pinch_correction_dict[row][1+midpoint_correction_index], self.pinch_correction_dict[row][4+midpoint_correction_index])
                        insert_location= pinch + pinch_insert_correction
                        left_stack = np.insert(total_stack, insert_location, new_point[0].flatten(), axis=1)
                        pinch_insert_correction +=1

                        insert_location = pinch + pinch_insert_correction + 1
                        total_stack = np.insert(left_stack, insert_location, new_point[1].flatten(), axis=1)
                        pinch_insert_correction +=1
                        midpoint_correction_index += 6
                    
            
                
        ########################################################################################################################################################

        #Calculates the polygons for formations that dont fade or pinch
            if ~np.any(self.style_array[row] == 'p') and ~np.any(self.style_array[row] == 'f'):
                
                #Checks if the next formation down pinches or fades
                if np.any(self.style_array[row+1] == 'f') or np.any(self.style_array[row+1] == 'p') or np.any(self.style_array[row+1] == 'c'):
                    #If it does, the index of where it pinches or fades will be used to replace the bottom value of the top formation with the bottom value
                    #of the lower formation, this is for ease of plotting later on.
                    total_stack = self.initial_polygon_list[row].copy()
                    bottom_replacements = (self.style_array[row+1] == 'f') | (self.style_array[row+1] == 'p')
                    total_stack[1][bottom_replacements] = self.initial_polygon_list[row+1][1][bottom_replacements]
                    #Lastly it creates the final polygon in the form of a 3-row 2D array and adds it to a list
                    if row != len(self.initial_polygon_list)-2 :
                        bottom_replacements = (self.style_array[row+2] == 'f') | (self.style_array[row+2] == 'p')
                        total_stack[1][bottom_replacements] = self.initial_polygon_list[row+2][1][bottom_replacements]
                    
                    
                    #Adjusts for the fact that when 'c' is in the style array the formations below will need to be connected and they will leave no value for this layer
                    #to grab as its bottom
                    connection_below = np.where(self.style_array[row+1] == 'c')[0]
                    for connection in connection_below:
                        if self.initial_polygon_list[row][1, connection - 1] < self.initial_polygon_list[row][1, connection + 1]:
                            total_stack[1, connection] = self.initial_polygon_list[row][1, connection - 1]
                        else:
                            total_stack[1, connection] = self.initial_polygon_list[row][1, connection + 1]
                            
                #Connect formation across data gaps, particularly below shallow wells this is important
                if total_stack.shape[0] == 2:
                    total_stack = np.vstack((total_stack, self.locations))
                
                if np.any(self.style_array[row] == 'c'):
                    connect_index = np.where(self.style_array[row] == 'c')
                    total_stack = np.delete(total_stack, connect_index, axis=1)
                    

            self.formation_polygons.append(total_stack)
        
######################################################################################################################################################################################################################################
########################################################################################################################################################################

    def export_as_excel(self):
        df_export = pd.DataFrame({
            'DIST_FT' : self.locations,
            'W_NUM' : self.w_num,
            'DEM_ELEV' : self.well_elev,
            'FORM_START': np.nan
            })
        
        for index in range(self.formations_array.shape[0]):
            df_export[str(self.formations_list[index])] = self.formations_array[index]
            
        df_export['STYLE_start'] = np.nan
        
        for index in range(self.formations_array.shape[0]):
            df_export[(str(self.formations_list[index]) + '_style')] = self.style_array[index]
            
        df_export['CORE_OR_CUTTINGS'] = self.core_or_cuttings
        
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File', '')
        save_path += '.xlsx'
        
        df_export.to_excel(save_path, index=False)
            


########################################################################################################################################################################
    def save_pdf (self):
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File', '')
        save_path += '.pdf'
        
        top_of_bottom = np.max(self.formations_array[-1])
        fig, ax = plt.subplots(figsize=(16, 8), dpi=300)
        ax.fill_between(self.distance, top_of_bottom, self.elev)
        ax.plot(self.distance, self.elev, color='k', linewidth=0.8)
        for formation in self.formation_polygons:
            ax.fill_between(formation[-1], formation[0], formation[1])
        for n in range(len(self.w_num)):
            ax.vlines(self.locations[n], color='k', ymin=(self.formations_array[-1, n] -10), ymax=self.well_elev[n])
            ax.annotate(self.w_num[n], (self.locations[n]-50, self.well_elev[n]+10))
        
        fig.savefig(save_path, format='pdf', dpi=300)
        
    def save_png (self):
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File', '')
        save_path += '.png'
        
        top_of_bottom = np.max(self.formations_array[-1])
        fig, ax = plt.subplots(figsize=(16, 8), dpi=300)
        ax.fill_between(self.distance, top_of_bottom, self.elev)
        ax.plot(self.distance, self.elev, color='k', linewidth=0.8)
        for formation in self.formation_polygons:
            ax.fill_between(formation[-1], formation[0], formation[1])
        for n in range(len(self.w_num)):
            ax.vlines(self.locations[n], color='k', ymin=(self.formations_array[-1, n] -10), ymax=self.well_elev[n])
            ax.annotate(self.w_num[n], (self.locations[n]-50, self.well_elev[n]+10))
        
        fig.savefig(save_path, format='png', dpi=300)
        
    def save_tiff (self):
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File', '')
        save_path += '.tiff'
        
        top_of_bottom = np.max(self.formations_array[-1])
        fig, ax = plt.subplots(figsize=(16, 8), dpi=300)
        ax.fill_between(self.distance, top_of_bottom, self.elev)
        ax.plot(self.distance, self.elev, color='k', linewidth=0.8)
        for formation in self.formation_polygons:
            ax.fill_between(formation[-1], formation[0], formation[1])
        for n in range(len(self.w_num)):
            ax.vlines(self.locations[n], color='k', ymin=(self.formations_array[-1, n] -10), ymax=self.well_elev[n])
            ax.annotate(self.w_num[n], (self.locations[n]-50, self.well_elev[n]+10))
        
        fig.savefig(save_path, format='tiff', dpi=300)    
        
    def save_jpeg (self):
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File', '')
        save_path += '.jpeg'
        
        top_of_bottom = np.max(self.formations_array[-1])
        fig, ax = plt.subplots(figsize=(16, 8), dpi=300)
        ax.fill_between(self.distance, top_of_bottom, self.elev)
        ax.plot(self.distance, self.elev, color='k', linewidth=0.8)
        for formation in self.formation_polygons:
            ax.fill_between(formation[-1], formation[0], formation[1])
        for n in range(len(self.w_num)):
            ax.vlines(self.locations[n], color='k', ymin=(self.formations_array[-1, n] -10), ymax=self.well_elev[n])
            ax.annotate(self.w_num[n], (self.locations[n]-50, self.well_elev[n]+10))
        
        fig.savefig(save_path, format='jpeg', dpi=300)
        
    def save_eps (self):
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File', '')
        save_path += '.eps'
        
        top_of_bottom = np.max(self.formations_array[-1])
        fig, ax = plt.subplots(figsize=(16, 8), dpi=300)
        ax.fill_between(self.distance, top_of_bottom, self.elev)
        ax.plot(self.distance, self.elev, color='k', linewidth=0.8)
        for formation in self.formation_polygons:
            ax.fill_between(formation[-1], formation[0], formation[1])
        for n in range(len(self.w_num)):
            ax.vlines(self.locations[n], color='k', ymin=(self.formations_array[-1, n] -10), ymax=self.well_elev[n])
            ax.annotate(self.w_num[n], (self.locations[n]-50, self.well_elev[n]+10))
        
        fig.savefig(save_path, format='eps', dpi=300)
        
##################################################################################################################################################



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('TheBox.png'))
    
    
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    
    sys.exit(app.exec_())