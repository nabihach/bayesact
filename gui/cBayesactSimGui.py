import threading
import cPlot3D as cPlt3D
from cPlotBayesactSim import cPlotBayesactSim
from cEnum import eEPA
import wx

class cBayesactSimGui(object):
    def __init__(self):
        self.m_App = wx.App(redirect=False)
        self.m_PlotFrame = cPlt3D.cPlotFrame(None, title="Bayesact Simulator", size=(700, 550))
        self.m_PlotFrame.initPanel(style=wx.SIMPLE_BORDER, pos=(0, 0), size=(700, 550))

        self.m_PlotBayesactSim = cPlotBayesactSim(self.m_PlotFrame, eEPA.evaluation, eEPA.potency, eEPA.activity)
        self.m_Thread = None
        self.m_ThreadExists = False

        self.m_LearnerSamples = []
        self.m_SimulatorSamples = []


    def setThread(self, iThread):
        self.m_Thread = iThread
        iThread.daemon = True
        self.m_ThreadExists = True


    def startApp(self):
        if (False == self.m_ThreadExists):
            print "ERROR: Thread has not been declared"
        else:
            self.m_Thread.start()
            self.m_PlotFrame.Show()
            self.m_App.MainLoop()


    def plot3D(self):
        self.m_PlotBayesactSim.plotBayesactSim([self.m_LearnerSamples, self.m_SimulatorSamples])
