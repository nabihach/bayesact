from cConstants import cEPAConstants
from cEnum import eEPA
import cPlot2D


class cPlotFrame(cPlot2D.cPlotFrame):
    def __init__(self, iParent, **kwargs):
        cPlot2D.cPlotFrame.__init__(self, iParent, **kwargs)

    def initPanel(self, *args, **kwargs):
        self.m_PlotPanel = cPlotPanel(self, **kwargs)


class cPlotPanel(cPlot2D.cPlotPanel):

    def __init__(self, iParent, iXAxisItem=eEPA.evaluation, iYAxisItem=eEPA.potency, **kwargs):
        cPlot2D.cPlotPanel.__init__(self, iParent, **kwargs)

        self.m_XAxisItem = iXAxisItem
        self.m_YAxisItem = iYAxisItem


    def getSentimentEPAIndex(self, iEPA, iSentiment):
        return iEPA + (cEPAConstants.m_Dimensions * iSentiment)


    # Axis items are the enumerations of the elements in eEPA, so they're basically numbers
    def setAxis(iXAxisItem, iYAxisItem):
        self.m_XAxisItem = iXAxisItem
        self.m_YAxisItem = iYAxisItem


    def plotEPA(self, iLearnerSamples, iSimulatorSamples):
        self.clearAxes()

        if (0 < len(iLearnerSamples)):
            # Learner's sentiments on self and other, green and pink respectively
            self.plotScatter(
                iLearnerSamples[self.getSentimentEPAIndex(self.m_XAxisItem, cEPAConstants.m_SelfMultiplier)],
                iLearnerSamples[self.getSentimentEPAIndex(self.m_YAxisItem, cEPAConstants.m_SelfMultiplier)],
                iAutoScaling=False, iRedraw=False, iUpdate=False, marker="o", s=50, c="green", alpha=1, animated=False)

            self.plotScatter(
                iLearnerSamples[self.getSentimentEPAIndex(self.m_XAxisItem, cEPAConstants.m_OtherMultiplier)],
                iLearnerSamples[self.getSentimentEPAIndex(self.m_YAxisItem, cEPAConstants.m_OtherMultiplier)],
                iAutoScaling=False, iRedraw=False, iUpdate=False, marker="o", s=50, c="pink", alpha=1, animated=False)

        if (0 < len(iSimulatorSamples)):
            # Simulator's sentiments on self and other, goldenrod and blue respectively
            self.plotScatter(
                iSimulatorSamples[self.getSentimentEPAIndex(self.m_XAxisItem, cEPAConstants.m_SelfMultiplier)],
                iSimulatorSamples[self.getSentimentEPAIndex(self.m_YAxisItem, cEPAConstants.m_SelfMultiplier)],
                iAutoScaling=False, iRedraw=False, iUpdate=False, marker="o", s=50, c="goldenrod", alpha=1, animated=False)

            self.plotScatter(
                iSimulatorSamples[self.getSentimentEPAIndex(self.m_XAxisItem, cEPAConstants.m_OtherMultiplier)],
                iSimulatorSamples[self.getSentimentEPAIndex(self.m_YAxisItem, cEPAConstants.m_OtherMultiplier)],
                iAutoScaling=False, iRedraw=False, iUpdate=False, marker="o", s=50, c="blue", alpha=1, animated=False)

        self.m_Axes.set_xlabel(cEPAConstants.m_EPALabels[self.m_XAxisItem])
        self.m_Axes.set_ylabel(cEPAConstants.m_EPALabels[self.m_YAxisItem])
        self.redrawAxes()


