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
    def __init__(self, iPlotFrame, iXAxisItem, iYAxisItem, iZAxisItem=None):
        self.m_PlotPanels = [iPlotFrame.m_PlotPanel]

        self.m_KeepAlive = True
        self.m_XAxisItem = iXAxisItem
        self.m_YAxisItem = iYAxisItem
        self.m_ZAxisItem = iZAxisItem
        self.m_Lock = threading.Lock()

        self.m_SimulatorSamples = None
        self.m_LearnerSamples = None

        self.m_Sleep = False

        self.m_Parser = None
        self.m_ParserThread = None


    def plotBayesactSim(self, iSamples):
        if (None == iSamples):
            return

        self.m_SimulatorSamples = iSamples[eTurn.learner]
        self.m_LearnerSamples = iSamples[eTurn.simulator]

        # To plot only a certain number of samples
        for i in range(len(self.m_LearnerSamples)):
            self.m_LearnerSamples[i] = self.m_LearnerSamples[i][:cPlotConstants.m_MaxPlotSamples]

        for i in range(len(self.m_SimulatorSamples)):
            self.m_SimulatorSamples[i] = self.m_SimulatorSamples[i][:cPlotConstants.m_MaxPlotSamples]

        for plotPanel in self.m_PlotPanels:

            #with plotPanel.m_Lock

            if (2 == plotPanel.m_NumAxes):
                self.plotOnAxes2D(plotPanel)
            if (3 <= plotPanel.m_NumAxes and None != self.m_ZAxisItem):
                self.plotOnAxes3D(plotPanel)


    def sleepProcess(self):
        self.m_Sleep = True
        self.m_Parser.sleepProcess()


    def continueProcess(self):
        self.m_Sleep = False
        self.m_Parser.continueProcess()


    def killProcess(self):
        self.sleepProcess()
        self.m_Parser.m_KeepAlive = False


    def getSentimentEPAIndex(self, iEPA, iSentiment):
        return iEPA + (cEPAConstants.m_Dimensions * iSentiment)


    def plotOnAxes3D(self, iPlotPanel):
        # Learner's sentiments on self and other, green and pink respectively
        iPlotPanel.plotScatter(
            self.m_LearnerSamples[self.getSentimentEPAIndex(self.m_XAxisItem, cEPAConstants.m_SelfMultiplier)],
            self.m_LearnerSamples[self.getSentimentEPAIndex(self.m_YAxisItem, cEPAConstants.m_SelfMultiplier)],
            self.m_LearnerSamples[self.getSentimentEPAIndex(self.m_ZAxisItem, cEPAConstants.m_SelfMultiplier)],
            iRedraw=True, iUpdate=False, marker="o", s=50, c="green", alpha=1, animated=False)

        iPlotPanel.plotScatter(
            self.m_LearnerSamples[self.getSentimentEPAIndex(self.m_XAxisItem, cEPAConstants.m_OtherMultiplier)],
            self.m_LearnerSamples[self.getSentimentEPAIndex(self.m_YAxisItem, cEPAConstants.m_OtherMultiplier)],
            self.m_LearnerSamples[self.getSentimentEPAIndex(self.m_ZAxisItem, cEPAConstants.m_OtherMultiplier)],
            iRedraw=False, iUpdate=False, marker="o", s=50, c="pink", alpha=1, animated=False)

        # Simulator's sentiments on self and other, goldenrod and blue respectively
        iPlotPanel.plotScatter(
            self.m_SimulatorSamples[self.getSentimentEPAIndex(self.m_XAxisItem, cEPAConstants.m_SelfMultiplier)],
            self.m_SimulatorSamples[self.getSentimentEPAIndex(self.m_YAxisItem, cEPAConstants.m_SelfMultiplier)],
            self.m_SimulatorSamples[self.getSentimentEPAIndex(self.m_ZAxisItem, cEPAConstants.m_SelfMultiplier)],
            iRedraw=False, iUpdate=False, marker="o", s=50, c="goldenrod", alpha=1, animated=False)

        iPlotPanel.plotScatter(
            self.m_SimulatorSamples[self.getSentimentEPAIndex(self.m_XAxisItem, cEPAConstants.m_OtherMultiplier)],
            self.m_SimulatorSamples[self.getSentimentEPAIndex(self.m_YAxisItem, cEPAConstants.m_OtherMultiplier)],
            self.m_SimulatorSamples[self.getSentimentEPAIndex(self.m_ZAxisItem, cEPAConstants.m_OtherMultiplier)],
            iRedraw=False, iUpdate=False, marker="o", s=50, c="blue", alpha=1, animated=False)

        iPlotPanel.m_Axes.set_xlabel(cEPAConstants.m_EPALabels[self.m_XAxisItem])
        iPlotPanel.m_Axes.set_ylabel(cEPAConstants.m_EPALabels[self.m_YAxisItem])
        iPlotPanel.m_Axes.set_zlabel(cEPAConstants.m_EPALabels[self.m_ZAxisItem])
        iPlotPanel.redrawAxes()


    def plotOnAxes2D(self, iPlotPanel, iXAxisItem, iYAxisItem):
        # Learner's sentiments on self and other, green and pink respectively
        iPlotPanel.plotScatter(
            self.m_LearnerSamples[self.getSentimentEPAIndex(self.m_XAxisItem, cEPAConstants.m_SelfMultiplier)],
            self.m_LearnerSamples[self.getSentimentEPAIndex(self.m_YAxisItem, cEPAConstants.m_SelfMultiplier)],
            iRedraw=True, iUpdate=False, marker="o", s=50, c="green", alpha=1, animated=False)

        iPlotPanel.plotScatter(
            self.m_LearnerSamples[self.getSentimentEPAIndex(self.m_XAxisItem, cEPAConstants.m_OtherMultiplier)],
            self.m_LearnerSamples[self.getSentimentEPAIndex(self.m_YAxisItem, cEPAConstants.m_OtherMultiplier)],
            iRedraw=False, iUpdate=False, marker="o", s=50, c="pink", alpha=1, animated=False)

        # Simulator's sentiments on self and other, goldenrod and blue respectively
        iPlotPanel.plotScatter(
            self.m_SimulatorSamples[self.getSentimentEPAIndex(self.m_XAxisItem, cEPAConstants.m_SelfMultiplier)],
            self.m_SimulatorSamples[self.getSentimentEPAIndex(self.m_YAxisItem, cEPAConstants.m_SelfMultiplier)],
            iRedraw=False, iUpdate=False, marker="o", s=50, c="goldenrod", alpha=1, animated=False)

        iPlotPanel.plotScatter(
            self.m_SimulatorSamples[self.getSentimentEPAIndex(self.m_XAxisItem, cEPAConstants.m_OtherMultiplier)],
            self.m_SimulatorSamples[self.getSentimentEPAIndex(self.m_YAxisItem, cEPAConstants.m_OtherMultiplier)],
            iRedraw=False, iUpdate=False, marker="o", s=50, c="blue", alpha=1, animated=False)

        iPlotPanel.m_Axes.set_xlabel(cEPAConstants.m_EPALabels[self.m_XAxisItem])
        iPlotPanel.m_Axes.set_ylabel(cEPAConstants.m_EPALabels[self.m_YAxisItem])
        iPlotPanel.redrawAxes()

    # Axis items are the enumerations of the elements in eEPA, so they're basically numbers
    def setAxis(iXAxisItem, iYAxisItem, iZAxisItem=None):
        self.m_XAxisItem = iXAxisItem
        self.m_YAxisItem = iYAxisItem
        if (None != iZAxisItem):
            self.m_ZAxisItem = iZAxisItem


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


    def runOnPlot(self):
        # It is possible that you may preload data for the plot in the buffer
        # and then assign this plotter to a plot
        # This statement here prevents it though
        if (None == self.m_PlotPanels[0]):
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
