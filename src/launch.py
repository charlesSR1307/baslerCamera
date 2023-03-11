import cv2
import time
import json
import serial
import sys, os
import platform 
import numpy as np
import pandas as pd
from pypylon import pylon
from .camera import baslerCamera
from .basler import Ui_MainWindow
from multiprocessing import Process
from matplotlib import pyplot as plt
from PyQt5 import QtCore, QtGui, QtWidgets
from newWindows import mywindow2

class mywindow(QtWidgets.QMainWindow): 
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.camObject = baslerCamera()
        self.outputImage = None
        self.outputConverter = None
        self.transmissionImage = None
        self.transmissionConverter = None
        self.histCtrl = 0

        self.ui.gainScrollCalibration.valueChanged.connect(self.changeGainCal)
        self.ui.gainEditCalibration.returnPressed.connect(self.changeScrollGainCal)
        self.ui.setpointScrollCalibration.valueChanged.connect(self.changeSetpointCal)
        self.ui.exposureScrollCalibration.valueChanged.connect(self.changeExposureCal)
        self.ui.setpointEditCalibration.returnPressed.connect(self.changeScrollSetpointCal)
        self.ui.exposureEditCalibration.returnPressed.connect(self.changeScrollExposureCal) 
        # Led call section
        self.ui.redLed.stateChanged.connect(self.redLed)
        self.ui.blueLed.stateChanged.connect(self.blueLed)
        self.ui.cyanLed.stateChanged.connect(self.cyanLed)
        self.ui.greenLed.stateChanged.connect(self.greenLed)
        self.ui.wheelLed.stateChanged.connect(self.wheelLed)
        self.ui.violetLed.stateChanged.connect(self.violetLed)
        self.ui.yellowLed.stateChanged.connect(self.yellowLed)
        self.ui.deepredLed.stateChanged.connect(self.deepredLed)
        self.ui.infraredLed.stateChanged.connect(self.infraredLed)
        self.ui.chartreuseLed.stateChanged.connect(self.chartreuseLed)
        self.ui.ultravioletLed.stateChanged.connect(self.ultravioletLed)
  
        # Camera call section
        self.ui.dial.valueChanged.connect(self.pwmValue)
        self.ui.stopButton.clicked.connect(self.stopVideo)
        self.ui.checkBoxAFR.stateChanged.connect(self.AFR)
        
        self.ui.ledsOffButton.clicked.connect(self.off)
        self.ui.stopButton2.clicked.connect(self.stopVideo)
        self.ui.stopCamera.clicked.connect(self.stopCamera)
        self.ui.stopButton3.clicked.connect(self.stopVideo)
        self.ui.stopCamera2.clicked.connect(self.stopCamera)
        self.ui.snapshot.clicked.connect(self.snapshotImage)
        self.ui.startButton.clicked.connect(self.startCapture)
        self.ui.saveSnapshot.clicked.connect(self.saveSnapshot)
        self.ui.startButton2.clicked.connect(self.setCalibration)
        self.ui.pushButtonConnect.clicked.connect(self.camConnect)
        self.ui.pushButtonSetParameters.clicked.connect(self.camSet)
        self.ui.loadCalibration.clicked.connect(self.loadCalibration)
        #self.ui.startButton3.clicked.connect(self.liveVideoFeed)
        self.ui.calibrateSaveFile.clicked.connect(self.saveCalibration)        
        self.ui.automaticSavePath.clicked.connect(self.sequenceSavePath)
        self.ui.startAutomaticSequence.clicked.connect(self.sequenceStart)
        self.ui.saveAutomaticSequence.clicked.connect(self.saveAutomaticSequence)
        self.ui.loadAutomaticSequence.clicked.connect(self.loadAutomaticSequence)

    def camConnect(self):
        try:
            self.camObject.openCamera()
            self.ui.editGain.setText(str(self.camObject.gain))
            self.ui.editWidth.setText(str(self.camObject.width))
            self.ui.editGamma.setText(str(self.camObject.gamma))
            self.ui.editHeight.setText(str(self.camObject.height))
            self.ui.labelCameraInfo.setText(self.camObject.cameraInfo)
            self.ui.editFrameRate.setText(str(self.camObject.frameRate))
            self.ui.editExposure.setText(str(self.camObject.exposureTime))

            if self.camObject.digitalShift == 1:
                self.ui.comboBoxGain.setCurrentIndex(0)
            elif self.camObject.digitalShift == 2:
                self.ui.comboBoxGain.setCurrentIndex(1)                
            elif self.camObject.digitalShift == 3:
                self.ui.comboBoxGain.setCurrentIndex(2)                
            elif self.camObject.digitalShift == 4:
                self.ui.comboBoxGain.setCurrentIndex(3)
                self.camObject.digitalShift = 4

            if self.camObject.gainAuto == "Off":
                self.ui.comboBoxGain.setCurrentIndex(0)
            elif self.camObject.gainAuto == "On":
                self.ui.comboBoxGain.setCurrentIndex(1)

            if self.camObject.exposureAuto == "Continuous":
                self.ui.comboBoxExposure.setCurrentIndex(0)
            elif self.camObject.exposureAuto == "Off":
                self.ui.comboBoxExposure.setCurrentIndex(1)
            elif self.camObject.exposureAuto == "Once":
                self.ui.comboBoxExposure.setCurrentIndex(2)

            if self.camObject.pixelFormat== "Mono8":
                self.ui.comboBoxPixelFormat.setCurrentIndex(0)
            elif self.camObject.pixelFormat == "Mono12":
                self.ui.comboBoxPixelFormat.setCurrentIndex(1)
            elif self.camObject.pixelFormat == "Mono12p":
                self.ui.comboBoxPixelFormat.setCurrentIndex(2)

            self.ui.pushButtonSetParameters.setEnabled(True)
            QtWidgets.QMessageBox
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Camera connected")
            msg.setWindowTitle("Information")
            msg.exec_()

        except:
            QtWidgets.QMessageBox
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Camera not connected")
            msg.setWindowTitle("Error")
            msg.exec_()

    def camSet(self):
        self.camObject.gain = float(self.ui.editGain.text())
        self.camObject.width = int(self.ui.editWidth.text())
        self.camObject.gamma = float(self.ui.editGamma.text())
        self.camObject.height = int(self.ui.editHeight.text())
        if self.ui.checkBoxAFR.isChecked():
            self.camObject.frameRate = float(self.ui.editFrameRate.text())
        else:
            pass
        self.camObject.exposureTime = float(self.ui.editExposure.text())

        if self.ui.comboBoxGain.currentIndex() == 0:
            self.camObject.gainAuto = "Off"
        elif self.ui.comboBoxGain.currentIndex() == 1:
            self.camObject.gainAuto = "On"
        
        if self.ui.comboBoxExposure.currentIndex() == 0:
            self.camObject.exposureAuto = "Continuous"
        elif self.ui.comboBoxExposure.currentIndex() == 1:
            self.camObject.exposureAuto = "Off"
        elif self.ui.comboBoxExposure.currentIndex() == 2:
            self.camObject.exposureAuto = "Once"

        if self.ui.comboBoxPixelFormat.currentIndex() == 0:
            self.camObject.pixelFormat = "Mono8"
        elif self.ui.comboBoxPixelFormat.currentIndex() == 1:
            self.camObject.pixelFormat = "Mono12"
        elif self.ui.comboBoxPixelFormat.currentIndex() == 2:
            self.camObject.pixelFormat = "Mono12p"

        if self.ui.comboBoxFormat.currentIndex() == 0:
            self.format = ".png"
        elif self.ui.comboBoxFormat.currentIndex() == 1:
            self.format = ".tiff"
        elif self.ui.comboBoxFormat.currentIndex() == 2:
            self.format = ".raw"

        if self.ui.comboBoxDigitalShift.currentIndex() == 0:
            self.camObject.digitalShift = 1
        elif self.ui.comboBoxDigitalShift.currentIndex() == 1:
            self.camObject.digitalShift = 2
        elif self.ui.comboBoxDigitalShift.currentIndex() == 2:
            self.camObject.digitalShift = 3
        elif self.ui.comboBoxDigitalShift.currentIndex() == 3:
            self.camObject.digitalShift = 4

        self.camObject.setParameters()

        self.ui.gainEditCalibration.setText(self.ui.editGain.text())
        self.ui.exposureEditCalibration.setText(self.ui.editExposure.text())

        QtWidgets.QMessageBox
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Camera paramets defined")
        msg.setWindowTitle("Information")
        msg.exec_()

    def AFR(self):
        if self.ui.checkBoxAFR.isChecked():
            self.ui.editFrameRate.setEnabled(True)
        else:
            self.ui.editFrameRate.setEnabled(False)

    def startCapture(self):
        if self.camObject.camera.IsGrabbing():
            pass
        else:
            self.camObject.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
            self.outputConverter = pylon.ImageFormatConverter()
            self.transmissionConverter = pylon.ImageFormatConverter()
            # Output conversion
            if self.ui.comboBoxOutputBit.setCurrentIndex(0):
                self.outputConverter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
            if self.ui.comboBoxOutputBit.setCurrentIndex(1):
                self.outputConverter.OutputBitAlignment = pylon.OutputBitAlignment_LsbAligned

            self.transmissionConverter.OutputPixelFormat = pylon.PixelType_Mono8
            self.transmissionConverter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        
        # Transmission convertion 
        while self.camObject.camera.IsGrabbing():
            self.ui.manualModeVideoState.setTitle("Online video feed")
            self.grabResult =  self.camObject.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)            

            if self.grabResult.GrabSucceeded():
                self.transmissionImage = self.transmissionConverter.Convert(self.grabResult)
                self.img = self.transmissionImage.GetArray()
                self.resizedImage = cv2.resize(self.img, (531, 431))
                #cv2.imshow('Basler', self.resizedImage)
            
            QtWidgets.QApplication.processEvents()
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.displayVideoStream)
            self.timer.start(3)

            self.grabResult.Release()

    def displayVideoStream(self):
        frame = self.resizedImage
        #frame = cv2.flip(frame, 1)
        image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], 
                       frame.strides[0], QtGui.QImage.Format_Grayscale8)
        self.ui.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))

    def displayVideoStream2(self):
        frame = self.resizedImage2
        #frame = cv2.flip(frame, 1)
        image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], 
                       frame.strides[0], QtGui.QImage.Format_Grayscale8)
        self.ui.calibrationImage.setPixmap(QtGui.QPixmap.fromImage(image))
        
    def displayVideoStream3(self):
        cv2.imshow('Basler', self.resizedImage2)
        cv2.waitKey(1)
            
    def liveVideoFeed(self):
        if self.camObject.camera.IsGrabbing():
            pass
        else:
            self.camObject.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
            self.transmissionConverter2 = pylon.ImageFormatConverter()
            self.transmissionConverter2.OutputPixelFormat = pylon.PixelType_Mono8
            self.transmissionConverter2.OutputBitAlignment = pylon.OutputBitAlignment_LsbAligned
        
        # Transmission convertion 
        while self.camObject.camera.IsGrabbing():
            self.grabResult2 =  self.camObject.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)            

            if self.grabResult2.GrabSucceeded():
                self.transmissionImage2 = self.transmissionConverter2.Convert(self.grabResult2)
                self.img2 = self.transmissionImage2.GetArray()          
                self.resizedImage2 = cv2.resize(self.img2, (531, 431))
                
            QtWidgets.QApplication.processEvents()
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.displayVideoStream3)
            self.timer.start(1)

            self.grabResult2.Release()

    def stopVideo(self):
        if self.ui.manualModeVideoState.title() == "Online video feed":
            self.ui.manualModeVideoState.setTitle("No video feed")
        if self.ui.calibrationModeVideoState.title() == "Online video feed":
            self.ui.calibrationModeVideoState.setTitle("No video feed")
        self.camObject.camera.StopGrabbing()
        self.histCtrl = 0
        plt.close(1)
        cv2.destroyAllWindows()

    def stopCamera(self):
        self.camObject.camera.StopGrabbing()
        cv2.destroyAllWindows()
        #self.camObject.camera.Close()

    def snapshotImage(self):
        self.resizedImage2 = cv2.resize(self.img, (521, 421))
        cv2.imshow('Snapshot', self.resizedImage2)
        cv2.waitKey(0)
        cv2.destroyAllWindows
    
    def saveSnapshot(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(None, 'Test Dialog', os.getcwd(), 'All Files(*.*)')
        img = pylon.PylonImage()
        img.AttachGrabResultBuffer(self.grabResult)
        
        if platform.system() == 'Windows':
            # The JPEG format that is used here supports adjusting the image
            # quality (100 -> best quality, 0 -> poor quality).
            ipo = pylon.ImagePersistenceOptions()
            quality = 90 * 10
            ipo.SetQuality(quality)
            if self.format == ".png":
                filename = str(filename[0]) + self.format % quality
                img.Save(pylon.ImageFileFormat_Png, filename, ipo)
            elif self.format == ".raw":
                filename = str(filename[0]) + self.format % quality
                img.Save(pylon.ImageFileFormat_Raw, filename, ipo)
            elif self.format == ".tiff":
                filename = str(filename[0]) + self.format % quality
                img.Save(pylon.ImageFileFormat_Tiff, filename, ipo)
        else:
            if self.format == ".png":
                filename = str(filename[0]) + self.format
                img.Save(pylon.ImageFileFormat_Png, filename)
            elif self.format == ".raw":
                filename = str(filename[0]) + self.format
                img.Save(pylon.ImageFileFormat_Raw, filename)
            elif self.format == ".tiff":
                filename = str(filename[0]) + self.format
                img.Save(pylon.ImageFileFormat_Tiff, filename)

        QtWidgets.QMessageBox
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("File saved")
        msg.setWindowTitle("Information")
        msg.exec_()
    
    def changeSetpointCal(self):
        val = self.ui.setpointScrollCalibration.value()
        self.ui.setpointEditCalibration.setText(str(val))
        
    def changeScrollSetpointCal(self):
        val = self.ui.setpointEditCalibration.text()
        self.ui.setpointScrollCalibration.setValue(int(val))

    def changeGainCal(self):
        val = self.ui.gainScrollCalibration.value()
        self.ui.gainEditCalibration.setText(str(val))

    def changeScrollGainCal(self):
        val = self.ui.gainEditCalibration.text()
        self.ui.gainScrollCalibration.setValue(int(val))

    def changeExposureCal(self):
        val = self.ui.exposureScrollCalibration.value()
        self.ui.exposureEditCalibration.setText(str(val))

    def changeScrollExposureCal(self):
        val = self.ui.exposureEditCalibration.text()
        self.ui.exposureScrollCalibration.setValue(int(val))

    def setCalibration(self):
        if self.camObject.camera.IsGrabbing():
            pass
        else:
            #self.ui.imageLabel.setPixmap(QtGui.QPcamera.Open()ixmap('/home/vlad/venom.jpg'))
            self.camObject.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
            self.outputConverter = pylon.ImageFormatConverter()
            self.transmissionConverter = pylon.ImageFormatConverter()
            # Output conversion
            if self.ui.comboBoxOutputBit.setCurrentIndex(0):
                self.outputConverter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
            if self.ui.comboBoxOutputBit.setCurrentIndex(1):
                self.outputConverter.OutputBitAlignment = pylon.OutputBitAlignment_LsbAligned

            self.transmissionConverter.OutputPixelFormat = pylon.PixelType_Mono8
            self.transmissionConverter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        
        # Transmission convertion 
        self.histCtrl = 1
        fig, ax = plt.subplots()
        ax.set_title('Histogram (grayscale)')
        ax.set_xlabel('intensity')
        ax.set_ylabel('Frequency')
        lw = 3
        alpha = 0.5
        if self.camObject.pixelFormat == "Mono8":
            bins = 256
        if self.camObject.pixelFormat == "Mono12":
            bins = 4096
        lineGray, = ax.plot(np.arange(bins), np.zeros((bins,1)), c='k', lw=lw)
        ax.set_xlim(0, bins-1)
        ax.set_ylim(0, 0.1)
        plt.ion() 
        plt.show()
        
        while self.camObject.camera.IsGrabbing():
            self.ui.calibrationModeVideoState.setTitle("Online video feed")
            self.grabResult =  self.camObject.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if self.grabResult.GrabSucceeded():
                self.transmissionImage = self.transmissionConverter.Convert(self.grabResult)
                self.img = self.transmissionImage.GetArray()
                self.resizedImage2 = cv2.resize(self.img, (531, 331))
                #cv2.imshow('Basler', self.resizedImage)
                if self.histCtrl == 1:
                    numPixels = np.prod(self.img.shape[:])
                    histogram = cv2.calcHist([self.img], [0], None, [bins], [0, 255]) / numPixels
                    lineGray.set_ydata(histogram)
                    fig.canvas.draw()
                
                if self.ui.checkBoxcalibrate.isChecked():
                    if self.ui.setpointEditCalibration.text() == '':
                        self.ui.checkBoxcalibrate.setChecked(False)
                        QtWidgets.QMessageBox
                        msg = QtWidgets.QMessageBox()
                        msg.setIcon(QtWidgets.QMessageBox.Critical)
                        msg.setText("Setpoint not defined!")
                        msg.setWindowTitle("Error")
                        msg.exec_()

                    else:
                        setpoint = int(self.ui.setpointEditCalibration.text())
                        gain = float(self.ui.gainEditCalibration.text())
                        self.camObject.camera.Gain.SetValue(gain)
                        if self.camObject.pixelFormat == "Mono8":
                            imgMean = np.mean(self.img)
                        elif self.camObject.pixelFormat == "Mono12":
                            output = pylon.PylonImage()
                            output.AttachGrabResultBuffer(self.grabResult)
                            img2 = output.GetArray()
                            imgMean = np.mean(img2)
                            print(imgMean)
                            
                        offset = setpoint - imgMean
                        exposure = self.camObject.camera.ExposureTime.GetValue()
                        if offset < -30:
                            self.camObject.camera.ExposureTime.SetValue(exposure - 30)
                        elif offset > 30:
                                self.camObject.camera.ExposureTime.SetValue(exposure + 30)
                        elif offset < -1 and offset >= -30:
                            self.camObject.camera.ExposureTime.SetValue(exposure - 2)
                        elif offset > 1 and offset <= 30:
                            self.camObject.camera.ExposureTime.SetValue(exposure + 2)
                        elif offset >= -1 and offset <= 1:
                            self.camObject.camera.ExposureTime.SetValue(exposure)
                            self.ui.exposureEditCalibration.setText(str(exposure))
                            self.ui.checkBoxcalibrate.setChecked(False)

                            QtWidgets.QMessageBox
                            msg = QtWidgets.QMessageBox()
                            msg.setIcon(QtWidgets.QMessageBox.Information)
                            msg.setText("Calibration done")
                            msg.setWindowTitle("Information")
                            msg.exec_()

            QtWidgets.QApplication.processEvents()
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.displayVideoStream2)
            self.timer.start(3)
            self.grabResult.Release()

    def saveCalibration(self):
        data = {'Setpoin': 0, 'Gain': 0, 'Exposure': 0}
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Test Dialog', os.getcwd(), 'JSON Files(*.json*)')
        setpoint = self.ui.setpointEditCalibration.text()
        gain = self.ui.gainEditCalibration.text()
        exposure = self.ui.exposureEditCalibration.text()
        data['Setpoin'] = setpoint
        data['Gain'] = gain
        data['Exposure'] = exposure
        with open(filename[0], 'w') as outfile:
            json.dump(data, outfile)

    def loadCalibration(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Test Dialog', os.getcwd(), 'JSON Files(*.json*)')
        print(filename[0])
        with open(filename[0]) as json_file:  
            data = json.load(json_file)
        setpoint = data['Setpoin']
        gain = data['Gain']
        exposure = data['Exposure']
        self.ui.setpointEditCalibration.setText(str(setpoint))
        self.ui.gainEditCalibration.setText(str(gain))
        self.ui.exposureEditCalibration.setText(str(exposure))

    def sequenceSavePath(self):
        self.sequencePath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))

    def automaticCicle(self, imgNumber, path, led, exposure):
        if self.camObject.camera.IsGrabbing():
            self.camObject.camera.StopGrabbing()
        else:
            self.camObject.camera.ExposureTime.SetValue(exposure)
            self.camObject.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 

        i = 0

        while self.camObject.camera.IsGrabbing():
            self.ui.manualModeVideoState.setTitle("Online video feed")
            self.grabResult =  self.camObject.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            if self.grabResult.GrabSucceeded():
                output = pylon.PylonImage()
                output.AttachGrabResultBuffer(self.grabResult)

                if platform.system() == 'Windows':
                    ipo = pylon.ImagePersistenceOptions()
                    quality = 90 * 10
                    #self.pathName
                    ipo.SetQuality(quality)
                    if self.format == ".png":
                        filename = str(path) + led + str(i) + self.format
                        output.Save(pylon.ImageFileFormat_Png, filename)
                    elif self.format == ".raw":
                        filename = str(path) + led + str(i) + self.format
                        output.Save(pylon.ImageFileFormat_Raw, filename)
                    elif self.format == ".tiff":
                        filename = str(path) + led + str(i) + self.format
                        output.Save(pylon.ImageFileFormat_Tiff, filename)
                else:
                    if self.format == ".png":
                        filename = str(path) + led + str(i) + self.format
                        output.Save(pylon.ImageFileFormat_Png, filename)
                    elif self.format == ".raw":
                        filename = str(path) + led + str(i) + self.format
                        output.Save(pylon.ImageFileFormat_Raw, filename)
                    elif self.format == ".tiff":
                        filename = str(path) + led + str(i) + self.format
                        output.Save(pylon.ImageFileFormat_Tiff, filename)
                
                i = i + 1
                if i == imgNumber:
                    break
                
                output.Release()
            
            QtWidgets.QApplication.processEvents()
            self.grabResult.Release()
            
        self.camObject.camera.StopGrabbing()
        cv2.destroyAllWindows()

    def sequenceStart(self):
        pathName = self.sequencePath + '/' + self.ui.imagePrefixEdit.text()
        if self.ui.comboBoxLed0.currentIndex() != 0:
            pwm = self.ui.spinBoxPwm0.value()
            self.checkLedSequenceOn(self.ui.comboBoxLed0.currentIndex(), pwm)
            time.sleep(3)
            imagesNumber = int(self.ui.imagesEditAutomatic0.text())
            ledName = self.ui.comboBoxLed0.currentText()
            exposure = float(self.ui.exposureEditAutomatic0.text())
            self.stopVideo()
            self.automaticCicle(imagesNumber, pathName, ledName, exposure)
            self.checkLedSequenceOff(self.ui.comboBoxLed0.currentIndex(), pwm)
            print('Done ' + ledName)
            time.sleep(1)

        if self.ui.comboBoxLed1.currentIndex() != 0:
            pwm = self.ui.spinBoxPwm1.value()
            self.checkLedSequenceOn(self.ui.comboBoxLed1.currentIndex(), pwm)
            time.sleep(3)
            imagesNumber = int(self.ui.imagesEditAutomatic1.text())
            ledName = self.ui.comboBoxLed1.currentText()
            exposure = float(self.ui.exposureEditAutomatic1.text())
            self.automaticCicle(imagesNumber, pathName, ledName, exposure)
            self.checkLedSequenceOff(self.ui.comboBoxLed1.currentIndex(), pwm)
            print('Done ' + ledName)
            time.sleep(1)

        if self.ui.comboBoxLed2.currentIndex() != 0:
            pwm = self.ui.spinBoxPwm2.value()
            self.checkLedSequenceOn(self.ui.comboBoxLed2.currentIndex(), pwm)
            time.sleep(3)
            imagesNumber = int(self.ui.imagesEditAutomatic2.text())
            ledName = self.ui.comboBoxLed2.currentText()
            exposure = float(self.ui.exposureEditAutomatic2.text())
            self.automaticCicle(imagesNumber, pathName, ledName, exposure)
            self.checkLedSequenceOff(self.ui.comboBoxLed2.currentIndex(), pwm)
            print('Done ' + ledName)
            time.sleep(1)

        if self.ui.comboBoxLed3.currentIndex() != 0:
            pwm = self.ui.spinBoxPwm3.value()
            self.checkLedSequenceOn(self.ui.comboBoxLed3.currentIndex(), pwm)
            time.sleep(3)
            imagesNumber = int(self.ui.imagesEditAutomatic3.text())
            ledName = self.ui.comboBoxLed3.currentText()
            exposure = float(self.ui.exposureEditAutomatic3.text())
            self.automaticCicle(imagesNumber, pathName, ledName, exposure)
            self.checkLedSequenceOff(self.ui.comboBoxLed3.currentIndex(), pwm)
            print('Done ' + ledName)
            time.sleep(1)

        if self.ui.comboBoxLed4.currentIndex() != 0:
            pwm = self.ui.spinBoxPwm4.value()
            self.checkLedSequenceOn(self.ui.comboBoxLed4.currentIndex(), pwm)
            time.sleep(3)
            imagesNumber = int(self.ui.imagesEditAutomatic4.text())
            ledName = self.ui.comboBoxLed4.currentText()
            exposure = float(self.ui.exposureEditAutomatic4.text())
            self.automaticCicle(imagesNumber, pathName, ledName, exposure)
            self.checkLedSequenceOff(self.ui.comboBoxLed4.currentIndex(), pwm)
            print('Done ' + ledName)
            time.sleep(1)

        if self.ui.comboBoxLed5.currentIndex() != 0:
            pwm = self.ui.spinBoxPwm5.value()
            self.checkLedSequenceOn(self.ui.comboBoxLed5.currentIndex(), pwm)
            time.sleep(3)
            imagesNumber = int(self.ui.imagesEditAutomatic5.text())
            ledName = self.ui.comboBoxLed5.currentText()
            exposure = float(self.ui.exposureEditAutomatic5.text())
            self.automaticCicle(imagesNumber, pathName, ledName, exposure)
            self.checkLedSequenceOff(self.ui.comboBoxLed5.currentIndex(), pwm)
            print('Done ' + ledName)
            time.sleep(1)

        if self.ui.comboBoxLed6.currentIndex() != 0:
            pwm = self.ui.spinBoxPwm6.value()
            self.checkLedSequenceOn(self.ui.comboBoxLed6.currentIndex(), pwm)
            time.sleep(3)
            imagesNumber = int(self.ui.imagesEditAutomatic6.text())
            ledName = self.ui.comboBoxLed6.currentText()
            exposure = float(self.ui.exposureEditAutomatic6.text())
            self.automaticCicle(imagesNumber, pathName, ledName, exposure)
            self.checkLedSequenceOff(self.ui.comboBoxLed6.currentIndex(), pwm)
            print('Done ' + ledName)
            time.sleep(1)

        if self.ui.comboBoxLed7.currentIndex() != 0:
            pwm = self.ui.spinBoxPwm7.value()
            self.checkLedSequenceOn(self.ui.comboBoxLed7.currentIndex(), pwm)
            time.sleep(3)
            imagesNumber = int(self.ui.imagesEditAutomatic7.text())
            ledName = self.ui.comboBoxLed7.currentText()
            exposure = float(self.ui.exposureEditAutomatic7.text())
            self.stopVideo()
            self.automaticCicle(imagesNumber, pathName, ledName, exposure)
            self.checkLedSequenceOff(self.ui.comboBoxLed7.currentIndex(), pwm)
            print('Done ' + ledName)
            time.sleep(1)

        if self.ui.comboBoxLed8.currentIndex() != 0:
            pwm = self.ui.spinBoxPwm8.value()
            self.checkLedSequenceOn(self.ui.comboBoxLed8.currentIndex(), pwm)
            time.sleep(3)
            imagesNumber = int(self.ui.imagesEditAutomatic8.text())
            ledName = self.ui.comboBoxLed8.currentText()
            exposure = float(self.ui.exposureEditAutomatic8.text())
            self.automaticCicle(imagesNumber, pathName, ledName, exposure)
            self.checkLedSequenceOff(self.ui.comboBoxLed8.currentIndex(), pwm)
            print('Done ' + ledName)
            time.sleep(1)

        if self.ui.comboBoxLed9.currentIndex() != 0:
            pwm = self.ui.spinBoxPwm9.value()
            self.checkLedSequenceOn(self.ui.comboBoxLed9.currentIndex(), pwm)
            time.sleep(3)
            imagesNumber = int(self.ui.imagesEditAutomatic9.text())
            ledName = self.ui.comboBoxLed9.currentText()
            exposure = float(self.ui.exposureEditAutomatic9.text())
            self.automaticCicle(imagesNumber, pathName, ledName, exposure)
            self.checkLedSequenceOff(self.ui.comboBoxLed9.currentIndex(), pwm)
            print('Done ' + ledName)
            time.sleep(1)
            
        if self.ui.comboBoxLed10.currentIndex() != 0:
            pwm = self.ui.spinBoxPwm10.value()
            self.checkLedSequenceOn(self.ui.comboBoxLed10.currentIndex(), pwm)
            time.sleep(3)
            imagesNumber = int(self.ui.imagesEditAutomatic10.text())
            ledName = self.ui.comboBoxLed10.currentText()
            exposure = float(self.ui.exposureEditAutomatic10.text())
            self.automaticCicle(imagesNumber, pathName, ledName, exposure)
            self.checkLedSequenceOff(self.ui.comboBoxLed10.currentIndex(), pwm)
            print('Done ' + ledName)
            time.sleep(1)

    def saveAutomaticSequence(self):
        data = []
        data = pd.DataFrame(np.zeros((10, 0)))
        pd.Series()
        data.index.name = 'Data'
        columns = {'Led', 'PWM', 'Setpoint', 'Images', 'Gain', 'Exposure'}
        data = pd.DataFrame(columns=columns)
        
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save sequence', os.getcwd(), 'JSON Files(*.json*)')
        led = self.ui.comboBoxLed0.currentIndex()
        pwm = self.ui.spinBoxPwm0.value()
        setpoint = self.ui.setpointEditAutomatic0.text()
        images = self.ui.imagesEditAutomatic0.text()
        gain = self.ui.gainEditAutomatic0.text()
        exposure = self.ui.exposureEditAutomatic0.text()
        data = data.append({'Led': led,
                            'PWM': pwm, 
                            'Setpoint': setpoint,
                            'Images': images,
                            'Gain': gain,
                            'Exposure': exposure},
                             ignore_index=True)

        led = self.ui.comboBoxLed1.currentIndex()
        pwm = self.ui.spinBoxPwm1.value()
        setpoint = self.ui.setpointEditAutomatic1.text()
        images = self.ui.imagesEditAutomatic1.text()
        gain = self.ui.gainEditAutomatic1.text()
        exposure = self.ui.exposureEditAutomatic1.text()
        data = data.append({'Led': led,
                            'PWM': pwm, 
                            'Setpoint': setpoint,
                            'Images': images,
                            'Gain': gain,
                            'Exposure': exposure},
                             ignore_index=True)

        led = self.ui.comboBoxLed2.currentIndex()
        pwm = self.ui.spinBoxPwm2.value()
        setpoint = self.ui.setpointEditAutomatic2.text()
        images = self.ui.imagesEditAutomatic2.text()
        gain = self.ui.gainEditAutomatic2.text()
        exposure = self.ui.exposureEditAutomatic2.text()
        data = data.append({'Led': led,
                            'PWM': pwm, 
                            'Setpoint': setpoint,
                            'Images': images,
                            'Gain': gain,
                            'Exposure': exposure},
                             ignore_index=True)

        led = self.ui.comboBoxLed3.currentIndex()
        pwm = self.ui.spinBoxPwm3.value()
        setpoint = self.ui.setpointEditAutomatic3.text()
        images = self.ui.imagesEditAutomatic3.text()
        gain = self.ui.gainEditAutomatic3.text()
        exposure = self.ui.exposureEditAutomatic3.text()
        data = data.append({'Led': led,
                            'PWM': pwm, 
                            'Setpoint': setpoint,
                            'Images': images,
                            'Gain': gain,
                            'Exposure': exposure},
                             ignore_index=True)

        led = self.ui.comboBoxLed4.currentIndex()
        pwm = self.ui.spinBoxPwm4.value()
        setpoint = self.ui.setpointEditAutomatic4.text()
        images = self.ui.imagesEditAutomatic4.text()
        gain = self.ui.gainEditAutomatic4.text()
        exposure = self.ui.exposureEditAutomatic4.text()
        data = data.append({'Led': led,
                            'PWM': pwm, 
                            'Setpoint': setpoint,
                            'Images': images,
                            'Gain': gain,
                            'Exposure': exposure},
                             ignore_index=True)

        led = self.ui.comboBoxLed5.currentIndex()
        pwm = self.ui.spinBoxPwm5.value()
        setpoint = self.ui.setpointEditAutomatic5.text()
        images = self.ui.imagesEditAutomatic5.text()
        gain = self.ui.gainEditAutomatic5.text()
        exposure = self.ui.exposureEditAutomatic5.text()
        data = data.append({'Led': led,
                            'PWM': pwm, 
                            'Setpoint': setpoint,
                            'Images': images,
                            'Gain': gain,
                            'Exposure': exposure},
                             ignore_index=True)

        led = self.ui.comboBoxLed6.currentIndex()
        pwm = self.ui.spinBoxPwm6.value()
        setpoint = self.ui.setpointEditAutomatic6.text()
        images = self.ui.imagesEditAutomatic6.text()
        gain = self.ui.gainEditAutomatic6.text()
        exposure = self.ui.exposureEditAutomatic6.text()
        data = data.append({'Led': led,
                            'PWM': pwm, 
                            'Setpoint': setpoint,
                            'Images': images,
                            'Gain': gain,
                            'Exposure': exposure},
                             ignore_index=True)

        led = self.ui.comboBoxLed7.currentIndex()
        pwm = self.ui.spinBoxPwm7.value()
        setpoint = self.ui.setpointEditAutomatic7.text()
        images = self.ui.imagesEditAutomatic7.text()
        gain = self.ui.gainEditAutomatic7.text()
        exposure = self.ui.exposureEditAutomatic7.text()
        data = data.append({'Led': led,
                            'PWM': pwm, 
                            'Setpoint': setpoint,
                            'Images': images,
                            'Gain': gain,
                            'Exposure': exposure},
                             ignore_index=True)

        led = self.ui.comboBoxLed8.currentIndex()
        pwm = self.ui.spinBoxPwm8.value()
        setpoint = self.ui.setpointEditAutomatic8.text()
        images = self.ui.imagesEditAutomatic8.text()
        gain = self.ui.gainEditAutomatic8.text()
        exposure = self.ui.exposureEditAutomatic8.text()
        data = data.append({'Led': led,
                            'PWM': pwm, 
                            'Setpoint': setpoint,
                            'Images': images,
                            'Gain': gain,
                            'Exposure': exposure},
                             ignore_index=True)

        led = self.ui.comboBoxLed9.currentIndex()
        pwm = self.ui.spinBoxPwm9.value()
        setpoint = self.ui.setpointEditAutomatic9.text()
        images = self.ui.imagesEditAutomatic9.text()
        gain = self.ui.gainEditAutomatic9.text()
        exposure = self.ui.exposureEditAutomatic9.text()
        data = data.append({'Led': led,
                            'PWM': pwm, 
                            'Setpoint': setpoint,
                            'Images': images,
                            'Gain': gain,
                            'Exposure': exposure},
                             ignore_index=True)
        
        led = self.ui.comboBoxLed10.currentIndex()
        pwm = self.ui.spinBoxPwm10.value()
        setpoint = self.ui.setpointEditAutomatic10.text()
        images = self.ui.imagesEditAutomatic10.text()
        gain = self.ui.gainEditAutomatic10.text()
        exposure = self.ui.exposureEditAutomatic10.text()
        data = data.append({'Led': led,
                            'PWM': pwm, 
                            'Setpoint': setpoint,
                            'Images': images,
                            'Gain': gain,
                            'Exposure': exposure},
                             ignore_index=True)

        data.to_json(filename[0] + '.json', double_precision=1, orient='records')

    def loadAutomaticSequence(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Test Dialog', os.getcwd(), 'JSON Files(*.json*)')
        dfJ = json.loads(open(filename[0]).read())
        
        led = dfJ[0]['Led']
        pwm = dfJ[0]['PWM']
        setpoint = dfJ[0]['Setpoint']
        images = dfJ[0]['Images']
        gain = dfJ[0]['Gain']
        exposure = dfJ[0]['Exposure']
        self.ui.comboBoxLed0.setCurrentIndex(led)
        self.ui.spinBoxPwm0.setValue(pwm)
        self.ui.setpointEditAutomatic0.setText(setpoint)
        self.ui.imagesEditAutomatic0.setText(images)
        self.ui.gainEditAutomatic0.setText(gain)
        self.ui.exposureEditAutomatic0.setText(exposure)

        led = dfJ[1]['Led']
        pwm = dfJ[1]['PWM']
        setpoint = dfJ[1]['Setpoint']
        images = dfJ[1]['Images']
        gain = dfJ[1]['Gain']
        exposure = dfJ[1]['Exposure']
        self.ui.comboBoxLed1.setCurrentIndex(led)
        self.ui.spinBoxPwm1.setValue(pwm)
        self.ui.setpointEditAutomatic1.setText(setpoint)
        self.ui.imagesEditAutomatic1.setText(images)
        self.ui.gainEditAutomatic1.setText(gain)
        self.ui.exposureEditAutomatic1.setText(exposure)

        led = dfJ[2]['Led']
        pwm = dfJ[2]['PWM']
        setpoint = dfJ[2]['Setpoint']
        images = dfJ[2]['Images']
        gain = dfJ[2]['Gain']
        exposure = dfJ[2]['Exposure']
        self.ui.comboBoxLed2.setCurrentIndex(led)
        self.ui.spinBoxPwm2.setValue(pwm)
        self.ui.setpointEditAutomatic2.setText(setpoint)
        self.ui.imagesEditAutomatic2.setText(images)
        self.ui.gainEditAutomatic2.setText(gain)
        self.ui.exposureEditAutomatic2.setText(exposure)

        led = dfJ[3]['Led']
        pwm = dfJ[3]['PWM']
        setpoint = dfJ[3]['Setpoint']
        images = dfJ[3]['Images']
        gain = dfJ[3]['Gain']
        exposure = dfJ[3]['Exposure']
        self.ui.comboBoxLed3.setCurrentIndex(led)
        self.ui.spinBoxPwm3.setValue(pwm)
        self.ui.setpointEditAutomatic3.setText(setpoint)
        self.ui.imagesEditAutomatic3.setText(images)
        self.ui.gainEditAutomatic3.setText(gain)
        self.ui.exposureEditAutomatic3.setText(exposure)

        led = dfJ[4]['Led']
        pwm = dfJ[4]['PWM']
        setpoint = dfJ[4]['Setpoint']
        images = dfJ[4]['Images']
        gain = dfJ[4]['Gain']
        exposure = dfJ[4]['Exposure']
        self.ui.comboBoxLed4.setCurrentIndex(led)
        self.ui.spinBoxPwm4.setValue(pwm)
        self.ui.setpointEditAutomatic4.setText(setpoint)
        self.ui.imagesEditAutomatic4.setText(images)
        self.ui.gainEditAutomatic4.setText(gain)
        self.ui.exposureEditAutomatic4.setText(exposure)

        led = dfJ[5]['Led']
        pwm = dfJ[5]['PWM']
        setpoint = dfJ[5]['Setpoint']
        images = dfJ[5]['Images']
        gain = dfJ[5]['Gain']
        exposure = dfJ[5]['Exposure']
        self.ui.comboBoxLed5.setCurrentIndex(led)
        self.ui.spinBoxPwm5.setValue(pwm)
        self.ui.setpointEditAutomatic5.setText(setpoint)
        self.ui.imagesEditAutomatic5.setText(images)
        self.ui.gainEditAutomatic5.setText(gain)
        self.ui.exposureEditAutomatic5.setText(exposure)

        led = dfJ[6]['Led']
        pwm = dfJ[6]['PWM']
        setpoint = dfJ[6]['Setpoint']
        images = dfJ[6]['Images']
        gain = dfJ[6]['Gain']
        exposure = dfJ[6]['Exposure']
        self.ui.comboBoxLed6.setCurrentIndex(led)
        self.ui.spinBoxPwm6.setValue(pwm)
        self.ui.setpointEditAutomatic6.setText(setpoint)
        self.ui.imagesEditAutomatic6.setText(images)
        self.ui.gainEditAutomatic6.setText(gain)
        self.ui.exposureEditAutomatic6.setText(exposure)

        led = dfJ[7]['Led']
        pwm = dfJ[7]['PWM']
        setpoint = dfJ[7]['Setpoint']
        images = dfJ[7]['Images']
        gain = dfJ[7]['Gain']
        exposure = dfJ[7]['Exposure']
        self.ui.comboBoxLed7.setCurrentIndex(led)
        self.ui.spinBoxPwm7.setValue(pwm)
        self.ui.setpointEditAutomatic7.setText(setpoint)
        self.ui.imagesEditAutomatic7.setText(images)
        self.ui.gainEditAutomatic7.setText(gain)
        self.ui.exposureEditAutomatic7.setText(exposure)

        led = dfJ[8]['Led']
        pwm = dfJ[8]['PWM']
        setpoint = dfJ[8]['Setpoint']
        images = dfJ[8]['Images']
        gain = dfJ[8]['Gain']
        exposure = dfJ[8]['Exposure']
        self.ui.comboBoxLed8.setCurrentIndex(led)
        self.ui.spinBoxPwm8.setValue(pwm)
        self.ui.setpointEditAutomatic8.setText(setpoint)
        self.ui.imagesEditAutomatic8.setText(images)
        self.ui.gainEditAutomatic8.setText(gain)
        self.ui.exposureEditAutomatic8.setText(exposure)

        led = dfJ[9]['Led']
        pwm = dfJ[9]['PWM']
        setpoint = dfJ[9]['Setpoint']
        images = dfJ[9]['Images']
        gain = dfJ[9]['Gain']
        exposure = dfJ[9]['Exposure']
        self.ui.comboBoxLed9.setCurrentIndex(led)
        self.ui.spinBoxPwm9.setValue(pwm)
        self.ui.setpointEditAutomatic9.setText(setpoint)
        self.ui.imagesEditAutomatic9.setText(images)
        self.ui.gainEditAutomatic9.setText(gain)
        self.ui.exposureEditAutomatic9.setText(exposure)
        
        led = dfJ[10]['Led']
        pwm = dfJ[10]['PWM']
        setpoint = dfJ[10]['Setpoint']
        images = dfJ[10]['Images']
        gain = dfJ[10]['Gain']
        exposure = dfJ[10]['Exposure']
        self.ui.comboBoxLed10.setCurrentIndex(led)
        self.ui.spinBoxPwm10.setValue(pwm)
        self.ui.setpointEditAutomatic10.setText(setpoint)
        self.ui.imagesEditAutomatic10.setText(images)
        self.ui.gainEditAutomatic10.setText(gain)
        self.ui.exposureEditAutomatic10.setText(exposure)
    
    def checkLedSequenceOn(self, ctrl, pwm):
        if ctrl == 1:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "1" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        elif ctrl == 2:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "3" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        elif ctrl == 3:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "9" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        elif ctrl == 4:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "6" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        elif ctrl == 5:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "2" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        elif ctrl == 6:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "7" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        elif ctrl == 7:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "5" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        elif ctrl == 8:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "8" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        elif ctrl == 9:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "0" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        elif ctrl == 10:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "4" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        elif ctrl == 11:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = "1r"
            ard.write(ardString.encode())

    def checkLedSequenceOff(self, ctrl, pwm):
        if ctrl == 1:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "1" + "o"
            ard.write(ardString.encode())
        elif ctrl == 2:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "3" + "o"
            ard.write(ardString.encode())
        elif ctrl == 3:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "9" + "o"
            ard.write(ardString.encode())
        elif ctrl == 4:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "6" + "o"
            ard.write(ardString.encode())
        elif ctrl == 5:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "2" + "o"
            ard.write(ardString.encode())
        elif ctrl == 6:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "7" + "o"
            ard.write(ardString.encode())
        elif ctrl == 7:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "5" + "o"
            ard.write(ardString.encode())
        elif ctrl == 8:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "8" + "o"
            ard.write(ardString.encode())
        elif ctrl == 9:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "0" + "o"
            ard.write(ardString.encode())
        elif ctrl == 10:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = str(pwm) + "4" + "o"
            ard.write(ardString.encode())
        elif ctrl == 11:
            port = '/dev/ttyACM0'
            ard = serial.Serial(port,9600,timeout=5)
            time.sleep(1)
            ardString = "f"
            ard.write(ardString.encode())
    
    def pwmValue(self):
        pwm = self.ui.dial.value()
        self.ui.lcdPwm.display(pwm)

    def off(self):
        port = '/dev/ttyACM0'
        ard = serial.Serial(port,9600,timeout=5)
        pwm = self.ui.dial.value()
        time.sleep(1)
        if self.ui.blueLed.isChecked():
            ardString = str(pwm) + "1" + "o"
            ard.write(ardString.encode())

    def blueLed(self):
        port = '/dev/ttyACM0'
        ard = serial.Serial(port,9600,timeout=5)
        pwm = self.ui.dial.value()
        if self.ui.blueLed.isChecked():
            time.sleep(1)
            ardString = str(pwm) + "1" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        else:
            ardString = str(pwm) + '1' + 'o'
            time.sleep(1)
            ard.write(ardString.encode())
        
    def chartreuseLed(self):
        port = '/dev/ttyACM0'
        ard = serial.Serial(port,9600,timeout=5)
        pwm = self.ui.dial.value()
        if self.ui.chartreuseLed.isChecked():
            time.sleep(1)
            ardString = str(pwm) + "3" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        else:
            time.sleep(1)
            ardString = str(pwm) + "1" + "o"
            ard.write(ardString.encode())
    
    def cyanLed(self):
        port = '/dev/ttyACM0'
        ard = serial.Serial(port,9600,timeout=5)
        pwm = self.ui.dial.value()
        if self.ui.cyanLed.isChecked():
            time.sleep(1)
            ardString = str(pwm) + "9" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        else:
            time.sleep(1)
            ardString = str(pwm) + "1" + "o"
            ard.write(ardString.encode())

    def deepredLed(self):
        port = '/dev/ttyACM0'
        ard = serial.Serial(port,9600,timeout=5)
        pwm = self.ui.dial.value()
        if self.ui.deepredLed.isChecked():
            time.sleep(1)
            ardString = str(pwm) + "6" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        else:
            time.sleep(1)
            ardString = str(pwm) + "1" + "o"
            ard.write(ardString.encode())

    def greenLed(self):
        port = '/dev/ttyACM0'
        ard = serial.Serial(port,9600,timeout=5)
        pwm = self.ui.dial.value()
        if self.ui.greenLed.isChecked():
            time.sleep(1)
            ardString = str(pwm) + "2" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        else:
            time.sleep(1)
            ardString = str(pwm) + "1" + "0"
            ard.write(ardString.encode())

    def infraredLed(self):
        port = '/dev/ttyACM0'
        ard = serial.Serial(port,9600,timeout=5)
        pwm = self.ui.dial.value()
        if self.ui.infraredLed.isChecked():
            time.sleep(1)
            ardString = str(pwm) + "7" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        else:
            time.sleep(1)
            ardString = str(pwm) + "1" + "o"
            ard.write(ardString.encode())

    def redLed(self):
        port = '/dev/ttyACM0'
        ard = serial.Serial(port,9600,timeout=5)
        pwm = self.ui.dial.value()
        if self.ui.redLed.isChecked():
            time.sleep(1)
            ardString = str(pwm) + "5" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        else:
            time.sleep(1)
            ardString = str(pwm) + "1" + "o"
            ard.write(ardString.encode())

    def ultravioletLed(self):
        port = '/dev/ttyACM0'
        ard = serial.Serial(port,9600,timeout=5)
        pwm = self.ui.dial.value()
        if self.ui.ultravioletLed.isChecked():
            time.sleep(1)
            ardString = str(pwm) + "8" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        else:
            time.sleep(1)
            ardString = str(pwm) + "1" + "o"
            ard.write(ardString.encode())

    def violetLed(self):
        port = '/dev/ttyACM0'
        ard = serial.Serial(port,9600,timeout=5)
        pwm = self.ui.dial.value()
        if self.ui.violetLed.isChecked():
            time.sleep(1)
            ardString = str(pwm) + "0" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        else:
            time.sleep(1)
            ardString = str(pwm) + "1" + "o"
            ard.write(ardString.encode())

    def yellowLed(self):
        port = '/dev/ttyACM0'
        ard = serial.Serial(port,9600,timeout=5)
        pwm = self.ui.dial.value()
        if self.ui.yellowLed.isChecked():
            time.sleep(1)
            ardString = str(pwm) + "4" + "m"
            ard.write(ardString.encode())
            time.sleep(1) # uncomment
            ardString = "f"
            ard.write(ardString.encode())
        else:
            time.sleep(1)
            ardString = str(pwm) + "1" + "o"
            ard.write(ardString.encode())
    
    def wheelLed(self):
        port = '/dev/ttyACM0'
        ard = serial.Serial(port,9600,timeout=5)
        if self.ui.wheelLed.isChecked():
            time.sleep(1)
            ardString = "1r" #"1r"
            ard.write(ardString.encode())
        else:
            time.sleep(1)
            ardString = "f" #"010"
            ard.write(ardString.encode())
'''
def main():
    app = QtWidgets.QApplication([])
    application = mywindow()
    application.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
'''