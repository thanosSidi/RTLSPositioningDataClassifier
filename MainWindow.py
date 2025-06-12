import sys
import math
import copy

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QSlider, QLabel, QGridLayout, QSlider, QPushButton, QPlainTextEdit, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5 import QtCore,QtGui

# Matplotlib imports for embedding in PyQt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from matplotlib.patches import Rectangle
import matplotlib.cm as cm
import numpy as np
import csv

from .ClusterMerger import plot_clusters_with_flow, merge_all_within_threshold, classesToClusterDictionary
from .PointClassifier import classify_points_latest_only, drop_clusters_with_low_number_of_points
from .trilateration import calculateListOfPoints
from PIL import Image
import matplotlib.image as mpimg

############################
# PyQt Main Window
############################
def readPointsFromCSV(filename):
    xyPoints = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        
        # If your CSVs have headers like "x,y", uncomment the next line:
        # next(reader, None)  # skip header row
        next(reader, None)

        for row in reader:
            # Each row is expected to have two columns: x, y
            if len(row) < 2:
                continue
            x_val, y_val = float(row[0]), float(row[1])
            xyPoints.append((x_val,y_val))
    return xyPoints
def plotPointsWithOptions():
    None
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=10, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        
        self.axes = self.fig.add_subplot(111)
        self.parent = parent
        self.start_point = None
        self.rect_patch = None
        self.drawing = False

        super(MplCanvas, self).__init__(self.fig)
        self.mpl_connect('button_press_event', self.on_press)
        self.mpl_connect('motion_notify_event', self.on_motion)
        self.mpl_connect('button_release_event', self.on_release)
        
    def on_press(self, event):
        if event.inaxes != self.axes:
            return
        self.start_point = (event.xdata, event.ydata)
        self.drawing = True

        # Create a rectangle with 0 width and height initially
        self.rect_patch = Rectangle(self.start_point, 0, 0,
                                    linewidth=1, edgecolor='r', facecolor='none')
        self.axes.add_patch(self.rect_patch)
        self.draw()

    def on_motion(self, event):
        if not self.drawing or event.inaxes != self.axes or self.start_point is None:
            return

        x0, y0 = self.start_point
        x1, y1 = event.xdata, event.ydata
        width = x1 - x0
        height = y1 - y0

        self.rect_patch.set_width(width)
        self.rect_patch.set_height(height)
        self.rect_patch.set_xy((x0, y0))  # In case the origin changes
        self.draw()

    def on_release(self, event):
        if not self.drawing or event.inaxes != self.axes:
            return
        
        self.parent.rectSelectionFeedback(self.start_point,(event.xdata, event.ydata))
        self.drawing = False
        self.start_point = None
        self.draw()  # Final update

    
def calculateClusters(threshold, minPointsPerClass):
    None
class MainWindow(QMainWindow):
    def __init__(self, fileArg=None, image = None, points = [], pixelsPerMeter = 100 ):
        super().__init__()
        self.setWindowTitle("Positioning Data Classification")
        if image != None:
            self.img = mpimg.imread(image)
            self.pixelsPerMeter = pixelsPerMeter
        #Calculate the clusters based on the minPointsPerClass and 
        self.minPointsPerClass = 20
        self.PointClusteringthreshold = 1
        self.classMergingThreshold = 6
        self.grid = QGridLayout()
        self.image = None
        self.pixelsPerMeter = None
        self.arrowWidth = 0.02

        self.grid = QGridLayout()
        
        results = classify_points_latest_only(points, self.PointClusteringthreshold)
        results = drop_clusters_with_low_number_of_points(results, self.minPointsPerClass)
        self.clusters = classesToClusterDictionary(results)
        if ( image != None and pixelsPerMeter != None):
            self.image = Image.open(image)
            #self.image = self.image.rotate(90)
            self.pixelsPerMeter = pixelsPerMeter
            print("path")
        
        self.original_points = copy.deepcopy(points)  # keep original, unmerged

        self.canvas = MplCanvas(self, width=6, height=5, dpi=200)

        toolbar = NavigationToolbar(self.canvas, self)
        
        self.grid.addWidget(self.canvas)

        self.leftWidget = QWidget(self)
        self.leftWidget.setGeometry(QtCore.QRect(5,5,self.width()-200, self.height()-50))
        self.leftWidget.setLayout(self.grid)

        self.button1 = QPushButton("button1")
        
        self.arrowWidthSlider = QSlider(QtCore.Qt.Horizontal)
        self.arrowWidthSlider.setMaximum(100)
        self.arrowWidthSlider.setMinimum(1)
        self.arrowWidth = 0.05
        self.arrowWidthSlider.setValue(int(self.arrowWidth*100))
        self.arrowWidthSlider.setTickPosition(QSlider.TicksBelow)
        
        self.classLengthSlider  = QSlider(QtCore.Qt.Horizontal)
        self.classLengthSlider.setMaximum(40)
        self.classLengthSlider.setMinimum(1)
        self.classLengthSlider.setValue(self.minPointsPerClass)
        self.classLengthSlider.setTickPosition(QSlider.TicksBelow)

        self.thresholdSlider = QSlider(QtCore.Qt.Horizontal)
        self.thresholdSlider.setMaximum(100)
        self.thresholdSlider.setMinimum(1)
        self.thresholdSlider.setTickPosition(QSlider.TicksBelow)
        self.thresholdSlider.setValue(int(self.PointClusteringthreshold*100))

        self.chkBxClassifiedPointsOnly = QCheckBox("Show Only Class Points")
        self.showAnchors = QCheckBox("Show Anchors")
        self.showProcessFlow = QCheckBox("Show Process Flow")
        
        self.showGrid = QCheckBox("Show Grid")
        self.showMap = QCheckBox("Show Map")
        self.textArea = QPlainTextEdit()

        self.arrowWidthLabel = QLabel("Arrow Width:")
        self.classifyLabel = QLabel("Minimum Number of points to Classify:" + str(self.minPointsPerClass))
        self.threshold = QLabel("Point Clustering Range: " + str(self.PointClusteringthreshold) + "meters")
        
        self.classMergingSlider = QSlider(QtCore.Qt.Horizontal)
        self.classMergingSlider.setMaximum(20)
        self.classMergingSlider.setMinimum(1)
        self.classMergingSlider.setValue(self.minPointsPerClass)
        self.classMergingSlider.setTickPosition(QSlider.TicksBelow)

        self.classMergingSliderLabel = QLabel("Class Merging Radius:" + str(self.classMergingThreshold))
        
        self.verticalLayout = QVBoxLayout()
        #self.verticalLayout.addWidget(self.button1)
        self.verticalLayout.addWidget(self.classifyLabel)
        self.verticalLayout.addWidget(self.classLengthSlider)
        self.verticalLayout.addWidget(self.threshold)
        self.verticalLayout.addWidget(self.thresholdSlider)
        
        self.verticalLayout.addWidget(self.classMergingSliderLabel)
        self.verticalLayout.addWidget(self.classMergingSlider)
        
        self.verticalLayout.addWidget(self.arrowWidthLabel)
        self.verticalLayout.addWidget(self.arrowWidthSlider)

        self.verticalLayout.addWidget(self.chkBxClassifiedPointsOnly)
        self.verticalLayout.addWidget(self.showAnchors)
        self.verticalLayout.addWidget(self.showProcessFlow)
        self.verticalLayout.addWidget(self.showGrid)
        self.verticalLayout.addWidget(self.showMap)
        self.verticalLayout.addWidget(self.textArea)
        self.verticalLayout.addWidget(toolbar)
        self.verticalLayout.addStretch()

        self.rightWidget = QWidget(self)
        self.rightWidget.setGeometry(QtCore.QRect(self.width()-195, 5, 190, self.height()-10))
        self.rightWidget.setLayout(self.verticalLayout)

        
        self.thresholdSlider.sliderReleased.connect(self.PointClusteringThresholdSliderReleasedFunc)
        self.thresholdSlider.valueChanged.connect(self.PointClusteringThresholdSliderChangedFunc)

        self.classLengthSlider.valueChanged.connect(self.classLengthSliderChangedFunc)
        self.classLengthSlider.sliderReleased.connect(self.classLengthSliderReleasedFunc)
        
        self.classMergingSlider.valueChanged.connect(self.classMergingSliderChangedFunc)
        self.classMergingSlider.sliderReleased.connect(self.classMergingSliderReleasedFunc)
        # Initial plot
        self.update_plot()
    def rectSelectionFeedback(self, x, y):
        print("OK", x, y)
        plot_clusters_with_flow(self.clusters2, ax=self.canvas.axes)
    def classLengthSliderChangedFunc(self):
        val = self.classLengthSlider.value()
        self.minPointsPerClass = val
        self.classifyLabel.setText("Minimum Number of points to Classify:" + str(self.minPointsPerClass))
    def classLengthSliderReleasedFunc(self):
        self.update_plot()
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.leftWidget.setGeometry(QtCore.QRect(0,5,self.width()-270, self.height()-10))
        self.rightWidget.setGeometry(QtCore.QRect(self.width()-265, 20, 260, self.height()-10))
    def PointClusteringThresholdSliderChangedFunc(self):
        # Convert slider value to a float threshold
        val = (self.thresholdSlider.value()-1) / 10.0  #scale
        self.PointClusteringthreshold = val
        self.threshold.setText("Point Clustering Range:" + str(self.PointClusteringthreshold) + "meters")
        
    def classMergingSliderChangedFunc(self):
        self.classMergingThreshold = self.classMergingSlider.value()
        self.classMergingSliderLabel.setText("Class Merging Radius:" + str(self.classMergingThreshold))
    def classMergingSliderReleasedFunc(self):
        self.update_plot()
    def PointClusteringThresholdSliderReleasedFunc(self):
        self.update_plot()
    def update_plot(self):
        # Merge clusters with the given threshold
        points = copy.deepcopy(self.original_points)
        results = classify_points_latest_only(points, self.PointClusteringthreshold)
        results = drop_clusters_with_low_number_of_points(results, self.minPointsPerClass)
        self.clusters2 = classesToClusterDictionary(results)
        
        if self.classMergingThreshold > 0:
            clearPass = False
            while clearPass == False:
                self.clusters2, clearPass = merge_all_within_threshold(self.clusters2, self.classMergingThreshold)
            # Draw
        
        plot_clusters_with_flow(self.clusters2, ax=self.canvas.axes, image=self.img, pixelsPerMeter= self.pixelsPerMeter)


def transformPointDataFromAnyLogicSimulation(points , imageXzero = 35 , imageYzero = 36 , inverseY = True):
    newPoints = []
    if points != None:
        for i in range(0,len(points)):
            newX = points[i][0]- imageXzero
            newY = imageYzero - points[i][1]
            newPoints.append((newX, newY))
    return newPoints
############################
# Execution
############################

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    """clusters = {
        1: {
            "id": 1,
            "center": (1.0, 1.0),
            "points": [(1, 1)],
            # Suppose cluster 1 flows to clusters 2 and 3
            "flow_to": [2]
        },
        2: {
            "id": 2,
            "center": (2.0, 2.0),
            "points": [(2, 2), (2, 3)],
            # Suppose cluster 2 flows to cluster 4
            "flow_to": [3]
        },
        3: {
            "id": 3,
            "center": (5.0, 6.0),
            "points": [(5, 6)],
            "flow_to": [4]
        },
        4: {
            "id": 4,
            "center": (2.0, 2.0),
            "points": [(2, 2), (2, 2)],
            "flow_to": [5]
        },
        5: {
            "id": 5,
            "center": (9.0, 9.0),
            "points": [(9, 9)],
            "flow_to": [6]
        },
        6: {
            "id": 6,
            "center": (2.0, 2.0),
            "points": [(1.5, 1.5)],
            "flow_to": [7]
        },
        7: {
            "id": 7,
            "center": (5.0, 6.0),
            "points": [(5.5, 6.5)],
            "flow_to": [8]
        },
        8: {
            "id": 8,
            "center": (10, 10),
            "points": [(10, 10)],
            "flow_to": []
        }
    }"""
    
    #input_file = "C:\\Users\\thano\\OneDrive - Αριστοτέλειο Πανεπιστήμιο Θεσσαλονίκης\\PhD Dissertation\\PositioningDataClassifier\\TStransporter.txt"
    
    anchors_2d = [
        (0.1, 0.1),    # Anchor1
        (0.1, 42.8),   # Anchor2
        (59.0, 0.1)    # Anchor3
    ]

    #points = calculateListOfPoints(filepath=input_file, anchors = anchors_2d)

    input_file = "C:\\Users\\thano\\OneDrive - Αριστοτέλειο Πανεπιστήμιο Θεσσαλονίκης\\PhD Dissertation\\Job Shop1 with Positioning Data\\population4.csv"
    imageFile = "C:\\Users\\thano\\OneDrive - Αριστοτέλειο Πανεπιστήμιο Θεσσαλονίκης\\PhD Dissertation\\Job Shop1 with Positioning Data\\TopView.png"
    pixelsPerMeter = 24
    points = readPointsFromCSV(input_file)
    points = transformPointDataFromAnyLogicSimulation(points, imageXzero=35, imageYzero=36)

    print(points)
    window = MainWindow(points=points, image=imageFile, pixelsPerMeter=pixelsPerMeter)
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
