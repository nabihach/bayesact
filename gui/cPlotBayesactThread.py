import threading
import cPlotEPA3D
from cPlotBayesactSim import cPlotBayesactSim
import wx
from cEnum import eEPA

class cPlotBayesactThread(object):
    def __init__(self):
        self.m_App = None
        self.m_PlotFrame = None

        self.m_PlotBayesactSim = None
        self.m_Thread = None
        self.m_ThreadExists = False

        self.m_LearnerSamples = []
        self.m_SimulatorSamples = []


    # Used when you want to just blatantly start a window and plot stuff on it, will probably be deprecated later
    def initFrame(self):
        self.m_App = wx.App(redirect=False)
        self.m_PlotFrame = cPlotEPA3D.cPlotFrame(None, title="Bayesact Simulator", size=(700, 550))
        self.m_PlotFrame.initPanel(iXAxisItem=eEPA.evaluation,
                                   iYAxisItem=eEPA.potency,
                                   iZAxisItem=eEPA.activity,
                                   style=wx.SIMPLE_BORDER, pos=(0, 0), size=(700, 550))
        return self.m_PlotFrame.m_PlotPanel


    # Used to bind the first plot panel
    def initPlotBayesactSim(self, iPlotPanel):
        self.m_PlotBayesactSim = cPlotBayesactSim(iPlotPanel)


    def addPanel(self, iPlotPanel):
        self.m_PlotBayesactSim.m_PlotEPAPanels.append(iPlotPanel)


    def setThread(self, iThread):
        self.m_Thread = iThread
        iThread.daemon = True
        self.m_ThreadExists = True


    def startThread(self):
        self.m_Thread.start()




    # Used for standalone simulations, that is, with the init frame
    def startApp(self):
        if (False == self.m_ThreadExists):
            print "ERROR: Thread has not been declared"
        else:
            self.m_Thread.start()
            self.m_PlotFrame.Show()
            self.m_App.MainLoop()


    def plot(self):
        self.m_PlotBayesactSim.plotBayesactSim([self.m_LearnerSamples, self.m_SimulatorSamples])

    def clearPlots(self):
        self.m_PlotBayesactSim.clearPlots()
