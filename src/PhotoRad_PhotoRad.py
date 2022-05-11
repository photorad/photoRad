"""This component contains the core classes and functions for PhotoRad. Drag this to
the canvas before proceeding.
    Inputs:
        _reload_: Set this to True to reload the component.

    Output:
"""

ghenv.Component.Name = "PhotoRad_PhotoRad"
ghenv.Component.NickName = 'PhotoRad'
ghenv.Component.Message = 'VER 0.0.04\nMar_29_2022'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.icon
ghenv.Component.Category = "PhotoRad"
ghenv.Component.SubCategory = "0 | PhotoRad"
try:
    ghenv.Component.AdditionalHelpFromDocStrings = "1"
except:
    pass

__author__ = "Sarith"
__version__ = "2022.03.29"

import rhinoscriptsyntax as rs
import scriptcontext as sc
import itertools
import statistics
import csv
import warnings

sc.sticky["photoRadDict"] = {}


class PlantData(object):
    _temps = range(-65, 70, 5)
    _tempRanges = [(-200, -65)] + [(_temps[idx], _temps[idx + 1]) for idx in
                                   range(len(_temps) - 1)] + [(65, 200)]
    _zones = list(
        itertools.chain(*[["%sa" % zoneId, "%sb" % zoneId] for zoneId in range(14)]))

    def __init__(self, plantName, dliValue, minTemp=None, maxTemp=None, hardZone=None,
                 photoPeriod=None, growingSeason=None):
        self.name = plantName
        self.dliValue = dliValue
        self.photoPeriod = photoPeriod

        minTemp, maxTemp, hardinessZones = self._calcTempHardiness(minTemp, maxTemp,
                                                                   hardZone)
        self.minTemp = minTemp
        self.maxTemp = maxTemp
        self.hardinessZone = hardinessZones
        self.growingSeason = growingSeason

    @property
    def dliValue(self):
        return self._dliValueList

    @dliValue.setter
    def dliValue(self, value):
        originalValue = value
        try:
            value = value.strip().split()
            value = list(sorted(map(float, value)))
            value = value if (len(value) == 2) else value * 2

        except (ValueError, AttributeError):
            value = [float(value)] * 2

        for num in value:
            assert 0 <= num, "The value for dli should be greater than 0. So the input " \
                             "%s is incorrect" % originalValue

        self._dliValueList = list(value)

    @property
    def growingSeason(self):
        return self._growingSeasonList

    @growingSeason.setter
    def growingSeason(self, value):
        originalValue = value

        if value:
            try:
                value = value.strip().split()
                value = list(sorted(map(int, value)))
            except (ValueError, AttributeError):
                value = [int(value)]

            for num in value:
                assert 1 <= num <= 12, "The value for growing season should be between " \
                                       "1(January) and 12(December). So the input %s " \
                                       "is incorrect" % originalValue
            self._growingSeasonList = value
        else:
            self._growingSeasonList = list(range(1, 13))

    @property
    def photoPeriod(self):
        return self._photoPeriod

    @photoPeriod.setter
    def photoPeriod(self, value):
        originalValue = value
        value = value if value is not None else 0

        try:
            value = value.strip().split()
            value = list(map(int, value))

            value = value if (len(value) == 1) else value * 12

        except (ValueError, AttributeError):
            value = [int(value)] * 12

        for num in value:
            assert num in range(1,
                                25), "The value for photoPeriod should not exceed 24 " \
                                     "hours. So the input %s is incorrect" % \
                                     originalValue

        self._photoPeriod = list(value)

    def _calcTempHardiness(self, minTemp, maxTemp, hardiness):

        if not any((minTemp, maxTemp, hardiness)):
            return (
            PlantData._tempRanges[0][0], PlantData._tempRanges[-1][-1], PlantData._zones)

        if (minTemp or maxTemp) and hardiness:
            print(
                "For the plant '%s', it appears that minTemp(%s),maxTemp(%s) and "
                "hardiness(%s) values have been provided" \
                ".\n\tThe values of minTemp and maxTemp will be used to set hardiness "
                "and the provided value will be overridden" % (
                self.name, minTemp, maxTemp, hardiness))

        if (minTemp or maxTemp):
            minTemp = minTemp if minTemp is not None else maxTemp
            maxTemp = maxTemp if maxTemp is not None else minTemp
            minTemp = float(minTemp)
            maxTemp = float(maxTemp)
            startZoneIdx = None
            endZoneIdx = None
            for idx, (minVal, maxVal) in enumerate(PlantData._tempRanges):
                if minVal <= minTemp <= maxVal:
                    startZoneIdx = idx
                if minVal <= maxTemp <= maxVal:
                    endZoneIdx = idx

            if startZoneIdx == endZoneIdx:
                endZoneIdx += 1

            return minTemp, maxTemp, PlantData._zones[startZoneIdx:endZoneIdx]
        elif hardiness:

            hardSplit = hardiness.split()

            hardSplit2 = sorted([value for value in hardSplit if len(value) == 2])
            hardSplit3 = sorted([value for value in hardSplit if len(value) == 3])
            hardSort = hardSplit2 + hardSplit3

            for hardinessValue in hardSort:
                assert hardinessValue in PlantData._zones, "The value for hardiness(" \
                                                           "%s) should be one among " \
                                                           "%s" % (
                hardinessValue, ",".join(PlantData._zones))

            if len(hardSort) == 1:
                hardinessIndex = PlantData._zones.index(hardSort[0])
                minTemp, maxTemp = PlantData._tempRanges[hardinessIndex]

            else:
                hardinessIndexLow = PlantData._zones.index(hardSort[0])
                hardinessIndexUp = PlantData._zones.index(hardSort[-1])
                minTemp = PlantData._tempRanges[hardinessIndexLow][0]
                maxTemp = PlantData._tempRanges[hardinessIndexUp][1]

            print(hardSort, self.name)
            return minTemp, maxTemp, hardSort

    @property
    def dliAvg(self):
        return int(statistics.mean(self._dliValueList))

    @property
    def dliMax(self):
        return max(self._dliValueList)

    @property
    def dliMin(self):
        return min(self._dliValueList)

    @property
    def photoPeriodAvg(self):
        return int(statistics.mean(self.photoPeriod))

    @property
    def photoPeriodMax(self):
        return max(self.photoPeriod)

    @property
    def photoPeriodMin(self):
        return min(self.photoPeriod)

    def ToString(self):
        return "Plant data for %s" % self.name

    @property
    def summary(self):
        summaryList = ["Plant data summary for '%s'\n" % self.name]
        try:
            summaryList.append("\tDLI value(s): %s" % ",".join(map(list, self.dliValue)))
        except TypeError:
            summaryList.append("\tDLI value(s): %s" % ",".join(map(str, self.dliValue)))
        summaryList.append(
            "\tGrowing Season(s): %s" % ",".join(map(str, self.growingSeason)))

        summaryList.append("\tMinimum Temp: %s" % self.minTemp)
        summaryList.append("\tMaximum Temp: %s" % self.maxTemp)
        summaryList.append("\tHardiness Zone(s): %s" % ",".join(self.hardinessZone))
        try:
            summaryList.append(
                "\tPhotoperiod(s): %s" % ",".join(map(list, self.photoPeriod)))
        except TypeError:
            summaryList.append(
                "\tPhotoperiod(s): %s" % ",".join(map(str, self.photoPeriod)))

        return "\n".join(summaryList)

    @property
    def csvString(self):
        dliValue = list(map(str, self.dliValue))
        csvStringList = [self.name]

        csvStringList.append(" ".join(dliValue))
        csvStringList.append(str(self.minTemp))
        csvStringList.append(str(self.maxTemp))
        csvStringList.append(" ".join(map(str, self.hardinessZone)))
        csvStringList.append(" ".join(map(str, self.photoPeriod)))
        csvStringList.append(" ".join(map(str, self.growingSeason)))
        return ",".join(csvStringList)

    def __str__(self):
        return self.ToString()


sc.sticky["photoRadDict"]["plantDataClass"] = PlantData