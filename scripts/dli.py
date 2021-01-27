import sys
import math
import os
import calendar




def _parseIllPtsFile(filePath,slicePositionStart=0,slicePositionEnd=None):
    assert os.path.exists(filePath),"The file path (%s) was not found"%filePath



    dataList=[]
    with open(filePath) as filestream:
        for idx, lines in enumerate(filestream):

            lineData = list(map(float, lines.strip().split()))

            if not idx:
                slicePositionEnd=len(lineData) if slicePositionEnd is None else slicePositionEnd
            lineData=lineData[slicePositionStart:slicePositionEnd]
            dataList.append(lineData)
    return dataList

def calcDLI(illFilePaths,ptsFilePaths,convFactor=20):

    illFilePaths=[illFilePaths] if isinstance(illFilePaths,str) else illFilePaths

    ptsFilePaths = [ptsFilePaths] if isinstance(ptsFilePaths, str) else ptsFilePaths

    ptsLengths=[len(_parseIllPtsFile(ptsFile)) for ptsFile in ptsFilePaths]

    illDataSet=[_parseIllPtsFile(illFilePath,3) for illFilePath in illFilePaths]


    for idx,dataSet in enumerate(illDataSet):
        ptsLen=ptsLengths[idx]
        illLen=len(illDataSet[idx][0])
        assert ptsLen==illLen,\
            "The number of points (%s) in the pts file (%s) are not equal to the " \
            "illuminance values per line (%s) in the file (%s)"%(ptsLen,ptsFilePaths[idx],illLen,illFilePaths[idx])

    #Convert from 8760 x numPoints to numPoints x 8760 matrix
    illDataSetTr=[list(zip(*illData)) for illData in illDataSet]



    #Reduce the numPoints x 8760 matrix to numPoints x 365 matrix by averaging dailiy illuminances.
    dliDataSetDailyAvg=[]


    for idx,illDataTr in enumerate(illDataSetTr):
        dliDailyData=[]
        for ptsData in illDataTr:
            # calculate daily average illuminances
            ptsDataNew=[sum(ptsData[num*24:(num+1)*24])/24 for num in range(365)]

            # calculate dli
            parData=[(avgIll*convFactor/1000)*0.0864 for avgIll in ptsDataNew]

            dliDailyData.append(parData)
        dliDataSetDailyAvg.append(dliDailyData)



    return dliDataSetDailyAvg


def avgDLIMonthly(yearlyDLIdata, monthNum):
    assert monthNum in range(1, 13), \
        "The input for monthNum (%s) must be a number between 1 (Jan) and 12 (Dec)"
    assert len(yearlyDLIdata[0]) == 365, \
        "The dataset provided as input has incorrect number of data (%s) per point" % (
            len(yearlyDLIdata[0]))

    monthDates = [0] + [calendar.monthrange(2011, val)[-1] for val in range(1, 13)]

    monthDateSum = [sum(monthDates[:idx + 1])  for idx in range(len(monthDates))]

    monthSliceStart,monthSliceEnd=monthDateSum[monthNum-1:monthNum+1]

    avgMonthlyData=[sum(ptsData[monthSliceStart:monthSliceEnd])/(monthSliceEnd-monthSliceStart) for ptsData in yearlyDLIdata]

    return  avgMonthlyData



def avgDLIAnnual(yearlyDLIdata):
    assert len(yearlyDLIdata[0]) == 365, \
        "The dataset provided as input has incorrect number of data (%s) per point" % (
            len(yearlyDLIdata[0]))

    yearlyDLIdata=[sum(ptsData)/365 for ptsData in yearlyDLIdata]

    return yearlyDLIdata


if __name__ == "__main__":
    x = calcDLI(r"C:\ladybug\HB_vs_HBP\annualSimulation\HB_vs_HBP_0.ill",
                r"C:\ladybug\HB_vs_HBP\annualSimulation\HB_vs_HBP_0.pts")
    y = avgDLIMonthly(x[0], 12)
    z=avgDLIAnnual(x[0])

    print(z)
