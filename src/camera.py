import sys
import cv2
from pypylon import pylon
from pypylon import genicam

class baslerCamera(object):
    def __init__(self):
        try:
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        except genicam.GenericException as e:
            pass

    def openCamera(self):
        try:
            self.camera.Open()
            self.gain = self.camera.Gain.GetValue()
            self.gamma = self.camera.Gamma.GetValue()
            self.width = self.camera.Width.GetValue()
            self.height = self.camera.Height.GetValue()
            self.gainAuto = self.camera.GainAuto.GetValue()
            self.pixelFormat = self.camera.PixelFormat.GetValue()
            self.exposureAuto = self.camera.ExposureAuto.GetValue()
            self.digitalShift = self.camera.DigitalShift.GetValue()
            self.exposureTime = self.camera.ExposureTime.GetValue()
            self.cameraInfo = self.camera.GetDeviceInfo().GetModelName()
            self.frameRate = self.camera.AcquisitionFrameRate.GetValue()
        except:
            pass

    def setParameters(self):
        self.camera.Gain.SetValue(self.gain)
        self.camera.Gamma.SetValue(self.gamma)
        self.camera.Width.SetValue(self.width)
        self.camera.Height.SetValue(self.height)
        self.camera.GainAuto.SetValue(self.gainAuto)
        self.camera.PixelFormat.SetValue(self.pixelFormat)
        self.camera.ExposureAuto.SetValue(self.exposureAuto)
        self.camera.DigitalShift.SetValue(self.digitalShift)
        self.camera.ExposureTime.SetValue(self.exposureTime)
        self.camera.AcquisitionFrameRate.SetValue(self.frameRate)
