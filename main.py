from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt6 import uic
import sys
from speed_camera import detection

# UI window class
class Overlay(QMainWindow):

    # variables holding the absolute path to files
    speedMeasurementPath = ""
    licensePlatePath = ""

    #constructor - for on initialization purposes
    def __init__(self):
        super().__init__()
        uic.loadUi('./ui/overlay.ui', self)

        self.btn1.clicked.connect(self.btnStart)
        self.btn2.clicked.connect(self.btnExit)
        self.speedViewBtn.clicked.connect(self.btnSpeedFile)
        self.licensePlateViewBtn.clicked.connect(self.btnLicensePlateFile)

    # function to get from the ui neccessary parameters for resizing OpenCV windows
    def getScale(self):
        return float(self.editScale.text())

    # function to get from the ui neccessary parameters of the line which starts the speed measurement
    def getStart1(self):
        x1 = int(self.editX1Start.text())
        x2 = int(self.editX2Start.text())
        y = int(self.editYStart.text())

        return [(x1, y), (x2, y)]
    
    # function to get from the ui neccessary parameters of the line which ends the speed measurement
    def getEnd1(self):
        x1 = int(self.editX1End.text())
        x2 = int(self.editX2End.text())
        y = int(self.editYEnd.text())
 
        return [(x1, y), (x2, y)]

    # function to get from the ui neccessary parameters for the track length
    def getTrackLength(self):
        return int(self.editTrackLength.text())
    
    # function to get from the ui neccessary parameters for the velocity threshold
    def getVelocityConstraint(self):
        return int(self.editVelocityConstraint.text())

    # function to get from the ui path to speed measurement file
    def getSpeedFile(self):
        self.editSpeedFile.setText("")
        path = QFileDialog.getOpenFileName(self, "Select a file", "", "All Files (*)")
        return path[0]

    # function to get from the ui path to license plate file
    def getLicensePlateFile(self):
        self.editLicensePlateFile.setText("")
        path = QFileDialog.getOpenFileName(self, "Select a file", "", "All Files (*)")
        return path[0]

    # on click event which starts the main program
    def btnStart(self):
        scale = self.getScale()
        start1 = self.getStart1()
        end1 = self.getEnd1()
        track_length = self.getTrackLength()
        velocity_constraint = self.getVelocityConstraint()

        self.close()
        detection(scale, start1, end1, track_length, velocity_constraint, self.speedMeasurementPath, self.licensePlatePath)

    # on click event which gets the speed measurement file path
    def btnSpeedFile(self):
        self.speedMeasurementPath = self.getSpeedFile()

        self.editSpeedFile.setText(self.speedMeasurementPath.split("/")[-1])

    # on click event which gets the license plate file path
    def btnLicensePlateFile(self):
        self.licensePlatePath = self.getLicensePlateFile()

        self.editLicensePlateFile.setText(self.licensePlatePath.split("/")[-1])

    # on click event which exits the program
    def btnExit(self):
        sys.exit()


# instantiating the ui 
app = QApplication(sys.argv)
window = Overlay()
window.show()
app.exec()