# Plots bayesactsim by parsing it
import subprocess
import os
import re
import time
import signal
import threading
import wx
from cBayesactSimBuffer import cBayesactSimBuffer
from cEnum import eAxes, eTurn
from cConstants import cPlotConstants, cEPAConstants

class cPlotBayesactSim(object):
    # The axis items are enumerations of the EPA
    def __init__(self, iPlotEPAPanel):
        self.m_PlotEPAPanels = [iPlotEPAPanel]

        self.m_KeepAlive = True
        self.m_Lock = threading.Lock()

        self.m_SimulatorSamples = []
        self.m_LearnerSamples = []

        self.m_Sleep = False

        self.m_Parser = None
        self.m_ParserThread = None


    def plotBayesactSim(self, iSamples):
        if (None == iSamples):
            return

        self.m_LearnerSamples = iSamples[eTurn.simulator]
        self.m_SimulatorSamples = iSamples[eTurn.learner]

        # To plot only a certain number of samples
        for i in range(len(self.m_LearnerSamples)):
            self.m_LearnerSamples[i] = self.m_LearnerSamples[i][:cPlotConstants.m_MaxPlotSamples]

        for i in range(len(self.m_SimulatorSamples)):
            self.m_SimulatorSamples[i] = self.m_SimulatorSamples[i][:cPlotConstants.m_MaxPlotSamples]

        for plotPanel in self.m_PlotEPAPanels:

            #with plotPanel.m_Lock

            if (2 == plotPanel.m_NumAxes):
                plotPanel.plotEPA(self.m_LearnerSamples, self.m_SimulatorSamples)
            if (3 <= plotPanel.m_NumAxes):
                plotPanel.plotEPA(self.m_LearnerSamples, self.m_SimulatorSamples)


    def sleepProcess(self):
        self.m_Sleep = True
        self.m_Parser.sleepProcess()


    def continueProcess(self):
        self.m_Sleep = False
        self.m_Parser.continueProcess()


    def killProcess(self):
        self.sleepProcess()
        self.m_Parser.m_KeepAlive = False



    def bufferData(self):
        self.m_Parser = cBayesactSimBuffer()
        self.m_ParserThread = threading.Thread(target=self.m_Parser.run)
        self.m_ParserThread.daemon=True
        self.m_ParserThread.start()
        while(self.m_Parser.m_BufferThreshold < len(self.m_Parser.m_SamplesBuffer)):
            print self.m_Parser.m_BufferThreshold


    def plotBufferedData(self):
        while(0 < len(self.m_Parser.m_SamplesBuffer)):
            self.plotBayesactSim()
            print self.m_Parser.m_BufferThreshold


    def plotFile(self, iFileName):
        self.m_Parser = cBayesactSimBuffer()
        self.m_Parser.parseFile(iFileName)
        self.plotBufferedData()


    def clearPlots(self):
        for panel in self.m_PlotEPAPanels:
            panel.clearAxes()
            panel.redrawAxes()


    def runOnPlot(self):
        # It is possible that you may preload data for the plot in the buffer
        # and then assign this plotter to a plot
        # This statement here prevents it though
        if (None == self.m_PlotEPAPanels[0]):
            # Thread ends
            return

        self.m_Parser = cBayesactSimBuffer()
        self.m_ParserThread = threading.Thread(target=self.m_Parser.run, kwargs={"iFileName" : None})
        self.m_ParserThread.daemon=True
        self.m_ParserThread.start()
        while(self.m_KeepAlive):
            while (not(self.m_Sleep)):
                self.plotBayesactSim(self.m_Parser.getSamples())
        self.killProcess()
        #self.m_ParserThread.join()
