"""Calculate Daily Light Integral (DLI)
    Args:
        _radResults: The results from the AnnualIrradiance simulation run through
        HoneybeeRadiance.
        _dliConvFactor: Conversion factor used to calculate PAR from incident radiation. Defaults to 3.72.
        _run: Set this to True to run the component.

    Returns:
        dliData: A class containing calculated DLI values and summaries.
"""

ghenv.Component.Name = "PhotoRad_CalculateDLI"
ghenv.Component.NickName = 'Calculate_DLI'
ghenv.Component.Message = 'VER 0.0.04\nMay_24_2022'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.icon
ghenv.Component.Category = "PhotoRad"
ghenv.Component.SubCategory = "0 | PhotoRad"
try:
    ghenv.Component.AdditionalHelpFromDocStrings = "2"
except:
    pass

__author__ = "Sarith"
__version__ = "2022.05.24"

import rhinoscriptsyntax as rs

import sys
import math
import os
import calendar
from pprint import pprint
import tempfile


# Note: Rad file and rad refers to radiation data files that contain data in W/m2

class DLIdata(object):
    def __init__(self, radFile, ptsFile, conversionFactor=3.72):
        self.dliDailyData = self._calcDLI(radFile, ptsFile, conversionFactor)

    def _parseRadPtsFile(self, filePath, slicePositionStart=0, slicePositionEnd=None):
        """
        Parse multiple files in the rad format and return cleaned data. This function
        is for internal use only.
        """
        assert os.path.exists(filePath), "The file path (%s) was not found" % filePath

        dataList = []
        with open(filePath) as filestream:
            for idx, lines in enumerate(filestream):

                lineData = list(map(float, lines.strip().split()))

                if not idx:
                    slicePositionEnd = len(
                        lineData) if slicePositionEnd is None else slicePositionEnd
                lineData = lineData[slicePositionStart:slicePositionEnd]
                dataList.append(lineData)
        return dataList

    def _calcDLI(self, radFilePath, ptsFilePath, convFactor=3.72):

        assert os.path.exists(
            radFilePath), "The rad file (%s) was not found." % radFilePath

        assert os.path.exists(
            ptsFilePath), "The pts file (%s) was not found." % ptsFilePath

        radDataSet = self._parseRadPtsFile(radFilePath, 3)

        ptsLength = len(self._parseRadPtsFile(ptsFilePath))
        radLength = len(radDataSet[0])

        assert ptsLength == radLength, "The number of data points in points file (%s) " \
                                       "and rad file (%s) must be the same." % (
        ptsLength, radLength)

        # Convert from 8760 x numPoints to numPoints x 8760 matrix
        radDataSetTr = list(zip(*radDataSet))

        # Reduce the numPoints x 8760 matrix to numPoints x 365 matrix by averaging
        # dailiy raduminances.
        dliDataSetDailyAvg = []

        dliDailyData = []

        for ptsData in radDataSetTr:
            # calculate daily average raduminances
            ptsDataNew = [sum(ptsData[num * 24:(num + 1) * 24]) / 24 for num in
                          range(365)]

            # calculate dli
            parData = [(avgRad * convFactor) * 0.0864 for avgRad in ptsDataNew]

            dliDailyData.append(parData)

        return dliDailyData

    def avgDLIMonthly(self, monthNum):
        yearlyDLIdata = self.dliDailyData
        assert monthNum in range(1, 13), \
            "The input for monthNum (%s) must be a number between 1 (Jan) and 12 (Dec)"
        assert len(yearlyDLIdata[0]) == 365, \
            "The dataset provided as input has incorrect number of data (%s) per " \
            "point" % (
                len(yearlyDLIdata[0]))

        monthDates = [0] + [calendar.monthrange(2011, val)[-1] for val in range(1, 13)]

        monthDateSum = [sum(monthDates[:idx + 1]) for idx in range(len(monthDates))]

        monthSliceStart, monthSliceEnd = monthDateSum[monthNum - 1:monthNum + 1]

        avgMonthlyData = [sum(ptsData[monthSliceStart:monthSliceEnd]) / (
                    monthSliceEnd - monthSliceStart) for ptsData in yearlyDLIdata]

        return avgMonthlyData

    @property
    def dataSize(self):
        return (len(self.dliDailyData), len(self.dliDailyData[0]))

    @property
    def avgDLIAnnual(self):
        yearlyDLIdata = self.dliDailyData
        assert len(yearlyDLIdata[0]) == 365, \
            "The dataset provided as input has incorrect number of data (%s) per " \
            "point" % (
                len(yearlyDLIdata[0]))

        yearlyDLIdata = [sum(ptsData) / 365 for ptsData in yearlyDLIdata]

        return yearlyDLIdata

    def ToString(self):
        return "DLI data generated for %s points for %s days" % self.dataSize


def consolidate_results(results, sun_hours):
    """Locate all the files required for the calculation."""
    assert os.path.exists(results), 'The results file %s was not found. Are the paths ' \
                                    'correct?' % results

    dirPath, resFile = os.path.split(results)

    rootFolder = (os.path.dirname(os.path.dirname(dirPath)))

    # need this for locating the pts file.
    resId, ext = os.path.splitext(resFile)

    weaFilePath = [os.path.join(rootFolder, val) for val in os.listdir(rootFolder) if
                   val.lower().endswith('.wea')][0]

    ptsFilePath = os.path.join(rootFolder, 'model', 'grid', '%s.pts' % resId)

    return {'rad_rad': results, 'wea': weaFilePath, 'sun_hours': sun_hours,
            'pts': ptsFilePath,
            'root_dir': rootFolder}


def prep_rad_file(res_dict, output_path=None):
    sun_hours_path = res_dict['sun_hours']
    rad_rad_path = res_dict['rad_rad']
    wea_path = res_dict['wea']
    pts_path = res_dict['pts']
    output_path = output_path or tempfile.mktemp(dir=res_dict['root_dir'], suffix='.rad')

    with open(sun_hours_path) as sunData:
        sunList = list(map(float, sunData.read().split()))

    radList = []
    with open(rad_rad_path) as radData:
        for lines in radData:
            if lines.strip():
                lineList = lines.strip().split()
                radList.append(list(map(float, lineList)))

    ptsListLen = len(radList)
    radList = list(zip(*radList))

    totalHourList = [idx + 0.5 for idx in range(8760)]

    weaHourList = []
    with open(wea_path) as weaData:
        for lines in weaData:
            try:
                lineSplit = list(map(float, lines.strip().split()))
                weaHourList.append(lineSplit[:3])
            except ValueError:
                pass  #

    finalRadList = []
    for idx, hourVal in enumerate(weaHourList):
        currentHour = totalHourList[idx]
        if currentHour in sunList:
            hourIdx = sunList.index(currentHour)
            radHourList = [rad for rad in radList[hourIdx]]
            finalRadList.append(list(hourVal) + radHourList)
        else:
            finalRadList.append(hourVal + [0] * ptsListLen)

    with open(output_path, 'w') as output_stream:
        for lines in finalRadList:
            write_val = " ".join(map(str, lines))
            output_stream.write(write_val + '\n')

    print('The temporary results file was saved as %s' % output_path)

    return output_path, pts_path


if _radResults and _run:
    #Assuming that the last file is always the sunhours.
    sunHoursPath=_radResults[-1]
    #Create a separate list of ill files.
    resPaths=_radResults[:-1]

    _dliConvFactor_=_dliConvFactor_ if _dliConvFactor_ else 3.72
    # Initiate a new list for DLI data.
    dliData=[]
    for resPath in resPaths:
        res_dict = consolidate_results(resPath, sunHoursPath)

        radFilePath, ptsFilePath = prep_rad_file(res_dict)

        dliData.append(DLIdata(radFilePath, ptsFilePath, _dliConvFactor_))








