from sys import platform as _platform


class cWindowsOSConstants:
    m_ProcessTerminate = 1

class cSystemConstants:
    m_OS = 0

    m_LinuxOS = 0b0001
    m_MacOS = 0b0010
    m_WindowsOS = 0b0100

    if "linux" == _platform or "linux2" == _platform:
        m_OS |= 0b0001
    elif "darwin" == _platform:
        m_OS |= 0b0010
    elif "win32" == _platform:
        m_OS |= 0b0100


class cColourConstants:
    m_Colours = ["blue", "green", "red", "pink", "cyan", "magenta",
                 "yellow", "goldenrod", "black", "white"]


class cEPAConstants:
    m_EPALabels = ["Evaluation", "Potency", "Activity"]
    m_Dimensions = 3
    m_SelfMultiplier = 0
    m_ActionMultiplier = 1
    m_OtherMultiplier = 2

    m_NumAttributes = 9


class cPlotConstants:
    # Adjust how many samples of each agent to plot
    m_MaxPlotSamples = 100

    m_ZoomKey = "ctrl+="
    m_UnZoomKey = "ctrl+-"
    m_ResetAxesKey = "ctrl+d"

    m_IncreaseXAxisKey = "ctrl+q"
    m_DecreaseXAxisKey = "ctrl+w"
    m_IncreaseYAxisKey = "ctrl+a"
    m_DecreaseYAxisKey = "ctrl+s"
    m_IncreaseZAxisKey = "ctrl+z"
    m_DecreaseZAxisKey = "ctrl+x"

    # 3 represents right click
    m_MousePanButton = 3

    m_DefaultXAxisMin = -4.3
    m_DefaultXAxisMax = 4.3
    m_DefaultYAxisMin = -4.3
    m_DefaultYAxisMax = 4.3
    m_DefaultZAxisMin = -4.3
    m_DefaultZAxisMax = 4.3

    m_BackgroundColour = "WHITE"

    m_ShiftAxesSensitivity = 0.1
    m_ScrollSensitivity = 1.0
    m_KeyZoomSensitivity = 2.0


class cPlot2DConstants:
    m_MouseDragSensitivity = 1
    m_PanSensitivity = 1.0 / (m_MouseDragSensitivity * 100)


    m_FigSize = (10,7)

    # Left, Bottom, Width, Height, all fractions of figure width and height in range [0,1]
    m_Rect = [0.1, 0.1, 0.8, 0.8]


class cPlot3DConstants:
    # 1 represents left click
    m_MouseRotateButton = 1

    m_DefaultElev = 30
    m_DefaultAzim = -60

    m_MouseDragSensitivity = 10.0
    m_PanSensitivity = 1.0 / (m_MouseDragSensitivity * 10)


class cParseConstants:
    m_Command = "cd ../\npython bayesactsim.py -v"
    #m_Command = "python bayesactsim.py"

    m_IterationPhrase = "-d-d-d-d-d-d-d-d-d-d iter"
    m_SamplesPhrase = "!!!!!! unweighted set:"
    m_MeanLearnerPhrase1 = "learner f is:"
    m_MeanLearnerPhrase2 = "learner average f:"
    m_MeanSimulatorPhrase1 = "simulator f is:"
    m_MeanSimulatorPhrase2 = "simulator average:"
    m_fValuesPhrase = "^f : \["
