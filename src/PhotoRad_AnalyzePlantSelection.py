"""Select plants based on DLI and Location data.
    Inputs:
        _plantData: List of plantData classes which are to be analyzed.
        _locationData: The output from the locationData component.
        _dliData: The output from the dliData component.
        _plantIndex: The index of the plant, from the _plantData input, which is to be analyzed.
        _filterBySoilTemp_: If set to True, then those plants whose soil temperature requirements are not compatible with the current location will be rejected.
        _dliUpToTol_: Upper limit of tolerance in DLI levels. Defaults to 1.05
        _dliLowToTol_: Lower limit of tolerance in DLI levels. Defaults to 0.95
    Output:
        plantSummary: Data summary of the plant being analyzed.
        growSeasonSiteDLI: The average grid-based DLI of the site that relates to the growing season of the plant being analyzed.
        DLIrangeList: A list containing 0s, 1s and 2s that indicates the number of grid points that are within the tolerance range of the plant being analyzed. For a particular grid-point, 0 implies below range, 1 implies within range and 2 implies above range.
        chartTitleAna: Chart-title for tolerance-range-based visualization.
        legendTitleAna: Legend-title for tolerance-range-based visualization.
        chartTitleDLI: Chart-title for DLI visualization.
        legendTitleDLI: Legend-title for DLI visualization.
        growSeasonSiteDLI: The grid-based average DLI for the site corresponding to the growingSeason for the selected plant.
        plantSummary: Details of the plant considered for analysis.
        """

from __future__ import division

ghenv.Component.Name = "PhotoRad_AnalyzePlantSelection"
ghenv.Component.NickName = 'AnalyzePlantSelection'
ghenv.Component.Message = 'VER 0.0.04\nMar_29_2022'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.icon
ghenv.Component.Category = "PhotoRad"
ghenv.Component.SubCategory = "3 | Analysis"
try:
    ghenv.Component.AdditionalHelpFromDocStrings = "2"
except:
    pass

__author__ = "Sarith"
__version__ = "2022.03.29"

import rhinoscriptsyntax as rs
import Grasshopper.Kernel as gh
import statistics
import calendar


def main(plantData, locationData, dliData, plantIndex, filterBySoilTemp):
    outputDict = {"dliRangeList": None, "growSeasonSiteDLI": None,
                  "legendTitleAna": None,
                  "chartTitleAna": None, "chartTitleDLI": None, "legendTitleDLI": None, }

    plantInst = plantData[plantIndex]
    growSeason = plantInst.growingSeason

    locTmin = locationData.tmin
    locTmax = locationData.tmax

    plantTmin = plantInst.minTemp
    plantTmax = plantInst.maxTemp

    plantName = plantInst.name
    growSeasonMonths = ",".join([calendar.month_name[val] for val in growSeason])

    growSeasonDLIList = []

    # growSeasonDLI=plantInst.growingSeasonDLI

    dliRangeUp = plantInst.dliValue[1]
    dliRangeLow = plantInst.dliValue[0]

    for month in growSeason:
        if not growSeasonDLIList:
            growSeasonDLIList.extend(dliData.avgDLIMonthly(month))
        else:
            for idx, val in enumerate(dliData.avgDLIMonthly(month)):
                growSeasonDLIList[idx] += val

    print("Grow season DLI calculated for months:%s" % ",".join(map(str, growSeason)))
    growSeasonDLIList = [val / len(growSeason) for val in growSeasonDLIList]

    quartileRangeData = list(sorted(growSeasonDLIList))

    firstQuartileIndex = int(len(quartileRangeData) / 4)
    SecThirdQuartileIndex = int(len(quartileRangeData) / 5) + firstQuartileIndex
    FourthQuartileIndex = len(quartileRangeData) - SecThirdQuartileIndex

    frstQ = statistics.mean(quartileRangeData[:firstQuartileIndex])
    secThrQ = statistics.mean(
        quartileRangeData[firstQuartileIndex:SecThirdQuartileIndex])
    frthQ = statistics.mean(quartileRangeData[SecThirdQuartileIndex:])

    plotTitle = "Report for: %s\n\n\n" % (plantName.upper())
    plotTitle += "Growing season (months): %s\n\n" % growSeasonMonths
    plotTitle += "Growing season Plant DLI Range: (%s,%s)\n\n" % (
    dliRangeLow, dliRangeUp)
    plotTitle += "Growing season Location DLI Averages (Q1,Q2-Q3,Q4):(%0.1f, %0.1f, %0.1f)\n\n" % (
    frstQ, secThrQ, frthQ)
    plotTitle += "Plant Temperature Range(min,max): (%s,%s)\n\n" % (plantTmin, plantTmax)

    chartTitleDLI = "Daily Light Integral Averaged for Growing Season months\n\n"
    chartTitleDLI += "Growing season months for %s: %s\n\n" % (
    plantName.upper(), growSeasonMonths)

    # If filtering by soil temperature has been set to then check if the limits for
    # the plant and location match.
    # If they don't exit by returning -1 as value for the DLI grid.
    if filterBySoilTemp:
        if not (plantTmin <= locTmin and plantTmax >= locTmax):
            plotTitle += "The plant temperature range (%s,%s) is not compatible with the location temperature range (%s,%s)" % (
            plantTmin, plantTmax, locTmin, locTmax)

            dliRangeList = [-1] * len(growSeasonDLIList)

            outputDict["dliRangeList"] = dliRangeList
            outputDict["growSeasonSiteDLI"] = growSeasonDLIList
            outputDict["legendTitleAna"] = "Not Applicable"
            outputDict["chartTitleAna"] = plotTitle
            outputDict["chartTitleDLI"] = chartTitleDLI
            outputDict["legendTitleDLI"] = "DLI"

            return outputDict

    dliRangeList = []

    for idx, val in enumerate(growSeasonDLIList):
        if val > dliRangeUp:
            dliRangeList.append(2)

        if dliRangeUp >= val >= dliRangeLow:
            dliRangeList.append(1)
        if val < dliRangeLow:
            dliRangeList.append(0)

    lowMatchMax = (dliRangeList.count(0), dliRangeList.count(1), dliRangeList.count(2))

    lowMatchMaxPct = tuple(
        ["%.1f%%" % (100 * val / len(growSeasonDLIList)) for val in lowMatchMax])

    plotTitle += "Site Temperature Range(min,max): (%s,%s)\n\n" % (locTmin, locTmax)

    outputDict["dliRangeList"] = dliRangeList
    outputDict["growSeasonSiteDLI"] = growSeasonDLIList
    outputDict[
        "legendTitleAna"] = "0: BelowRange(%s), 1: WithinRange(%s), 2: AboveRange(%s)" % (
    lowMatchMaxPct[0], lowMatchMaxPct[1], lowMatchMaxPct[2])
    outputDict["chartTitleAna"] = plotTitle
    outputDict["chartTitleDLI"] = chartTitleDLI
    outputDict["legendTitleDLI"] = "DLI"

    # {"dliRangeList":None,"growSeasonSiteDLI":None,"legendTitleAna":None,
    #    "chartTitleAna":None, "chartTitleDLI":None,"legendTitleDLI":None,}

    return outputDict


if _plantData and _locationData and _dliData and (_plantIndex is not None):

    if _plantIndex >= len(_plantData):
        msg = "The value for _indxForSmry_(%s) exceeds the total number of entries (%s) in _plantDataList" % (
        _plantIndex, len(_plantData))
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        _plantIndex = len(_plantData) - 1

    plantSummary = _plantData[_plantIndex].summary

    outputDict = main(_plantData, _locationData, _dliData, _plantIndex,
                      _filterBySoilTemp_)

    growSeasonSiteDLI = outputDict["growSeasonSiteDLI"]
    DLIrangeList = outputDict["dliRangeList"]
    chartTitleAna = outputDict["chartTitleAna"]
    legendTitleAna = outputDict["legendTitleAna"]
    chartTitleDLI = outputDict["chartTitleDLI"]
    legendTitleDLI = outputDict["legendTitleDLI"]