"""This component provides a summary of the DLI values calculated through the calculateDLI component.
   Average and cummulative DLI values are calculated by averaging and summing (respectively) daily values.
    Inputs:
        _dliData: Connect the dliData output from the CalculateDLI component here.
        _monthIndex: The month for which the monthly DLI should be displayed. Valid inputs are 1 to 12 (corresponding to Jan to Dec respectively).
        _doyIndex: The day of the year for which DLI should be displayed.Valid inputs are 1 to 365.
        trnAnnualHourlyMtx_: Transpose the annualHourlyDLI output to a matrix of size (365 x No. of Points). The default output size is (No. of Points x 365).
    Output:
        annualHourlyDLI: A matrix containing DLI values for every grid point, mapped across the entire year. The size of the matrix is (No. of Points x 365)
        doyDLI: The DLI for every point in the grid, corresponding to the day of the year specified through the _doyIndex input.
        monthlyDLI: The average monthly DLI for every point in the grid, corresponding to the month of the year specified through the _monthIndex input.
        annualAverageDLI: Average yearly DLI for every point in the grid.
        monthlyCmuDLI: The cumulative monthly DLI for every point in the grid, corresponding to the month of the year specified through the _monthIndex input.
        annualCmuDLI: Annual cumulative yearly DLI for every point in the grid.
"""

ghenv.Component.Name = "PhotoRad_SummarizeDLI"
ghenv.Component.NickName = 'SummarizeDLI'
ghenv.Component.Message = 'VER 0.0.05\nJun_02_2022'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.icon
ghenv.Component.Category = "PhotoRad"
ghenv.Component.SubCategory = "0 | PhotoRad"
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

__author__ = "Sarith"
__version__ = "2022.06.02"

import rhinoscriptsyntax as rs
import calendar
import datetime

if _dliData:

    assert _doyIndex_ in range(1,366),"The value for _doyIndex_ (%s) must be value between 1 and 365"%_doyIndex_

    assert _monthIndex_ in range(1,13),"The value for _monthIndex_(%s) must be a value between 1 and 12"%_monthIndex_

    annualData=_dliData.dliDailyData
    annualDataInv=list(zip(*annualData))

    monthIndex=_monthIndex_
    doyIndex=_doyIndex_-1
    dateForDisplay=datetime.datetime(2013,1,1)+datetime.timedelta(_doyIndex_-1)


    if trnAnnualHourlyMtx_:
        print("The variable annualHourlyDLI is of the format (%s,%s)"%_dliData.dataSize)
        annualHourlyDLI=annualDataInv

    else:
        print("The variable annualHourlyDLI is of the format (%s,%s)"%(_dliData.dataSize[-1],_dliData.dataSize[0]))
        annualHourlyDLI=list(annualData)

    monthlyDLI=_dliData.avgDLIMonthly(monthIndex)
    monthlyCmuDLI=_dliData.cmuDLIMonthly(monthIndex)
    annualAverageDLI=_dliData.avgDLIAnnual
    doyDLI=annualDataInv[_doyIndex_-1]
    annualCmuDLI=_dliData.cmuDLIAnnual
    print("The monthly data 'monthlyDLI'(_monthIndex_:%s) corresponds to %s"%(_monthIndex_,calendar.month_name[_monthIndex_]))


    print("The data displayed for doyDLI(_doyIndex_:%s) corresponds to %s"%(_doyIndex_,dateForDisplay.strftime("%B-%d")))