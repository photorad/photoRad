"""Provides a scripting component.
    Args:
        _epwFile: The absolute file-path for the epw file.
    Returns:
        locationData: A class containing the details of the location, it's soil type
        and photoperiod.
        locationDailyPhotoperiod: Photoperiod for 365 days of the year. Photoperiod is
        for the number of hours for which visible light is present.

"""

ghenv.Component.NickName = 'ExtractLocationData'
ghenv.Component.Message = 'VER 0.0.04\nMar_29_2022'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.icon
ghenv.Component.Category = "PhotoRad"
ghenv.Component.SubCategory = "0 | PhotoRad"
try:
    ghenv.Component.AdditionalHelpFromDocStrings = "2"
except:
    pass

__author__ = "Sarith"
__version__ = "2022.03.29"

import rhinoscriptsyntax as rs
import scriptcontext as sc
import os
import System
import json
import sys
import calendar
import statistics


class LocationData(object):
    """Instantiate a class  """

    def __init__(self, epwFilePath, soilDataLBrelPath="soilData.json"):

        epwSourceDict = self._retrieveEPWdata(epwFilePath)
        soilDataDict = self._acquireSoilData(soilDataLBrelPath=soilDataLBrelPath)
        locationSoilDataDict = self._calcLocationSoilData(soilDataDict, epwSourceDict)

        self.sourceFile = epwFilePath
        self.soilData = soilDataDict
        self.longitude = epwSourceDict["longitude"]
        self.latitude = epwSourceDict["latitude"]
        self.location = epwSourceDict["location"]
        self.difRadData = epwSourceDict["difRadData"]
        self.hardinessZone = locationSoilDataDict["zone"]
        self.tmin = locationSoilDataDict["tmin"]
        self.tmax = locationSoilDataDict["tmax"]
        self.zipMatch = locationSoilDataDict["zipMatch"]
        self.longitudeMatch = locationSoilDataDict["lonMatch"]
        self.latitudeMatch = locationSoilDataDict["latMatch"]

    @property
    def sourceFile(self):
        return self._sourceFile

    @sourceFile.setter
    def sourceFile(self, epwPath):
        assert os.path.exists(
            epwPath), "The path provided for the epw file (%s) is not valid" % epwPath
        self._sourceFile = epwPath

    def _calcLocationSoilData(self, soilDict, epwDict):

        lon = epwDict["longitude"]
        lat = epwDict["latitude"]

        maxLonLatDiff = 99999

        hardinessZone = None
        hardinessTmin = None
        hardinessTmax = None
        hardinessZip = None
        for key, values in soilDict.items():
            try:
                currLon = values["lon"]
                currLat = values["lat"]
                lonDiff = abs(currLon - lon)
                latDiff = abs(currLat - lat)
                lonLat = lonDiff + latDiff

                if lonLat < maxLonLatDiff:
                    hardinessZone = values["zone"]
                    hardinessTmin = values["tMin"]
                    hardinessTmax = values["tMax"]
                    hardinessZip = key
                    longitudeMatch = currLon
                    latitudeMatch = currLat
                    maxLonLatDiff = lonLat
            except KeyError:
                pass

        return {"zone": hardinessZone, "tmin": hardinessTmin, "tmax": hardinessTmax,
                "zipMatch": hardinessZip, "lonMatch": longitudeMatch,
                "latMatch": latitudeMatch}

    def _acquireSoilData(self, soilDataLBrelPath="soilData.json"):
        """Check if the soil hardiness data exists and retrieve the zip-code based
        values from it."""

        ladybugFolder = sc.sticky["Ladybug_DefaultFolder"]
        assert os.path.exists(
            ladybugFolder), "The path for the Ladybug folder(%s) was not found on the " \
                            "disc" % ladybugFolder

        soilJsonPath = os.path.join(ladybugFolder, soilDataLBrelPath)

        if not os.path.exists(soilJsonPath):
            raise Exception(
                "The file containing soil data was not found at %s" % soilJsonPath)

        soilJsonData = None
        with open(soilJsonPath) as soilDataFile:
            soilJsonData = json.load(soilDataFile)
            if not soilJsonData:
                raise Exception("The file %s appears to be empty" % soilJsonPath)

        return soilJsonData

    def _retrieveEPWdata(self, epwFilePath):

        location = None
        longitude = None
        latitude = None

        epwSourceDict = {"location": None, "longitude": None, "latitude": None,
                         "difRadData": []}
        with open(epwFilePath) as epwData:
            for lines in epwData:
                if lines.strip():
                    lineSplit = lines.strip().split(',')
                    try:
                        yearCheck = float(lineSplit[0])
                        epwSourceDict["difRadData"].append(int(lineSplit[15]))
                    except ValueError:
                        if lineSplit[0].lower() == "location":
                            lineSplit[1:4] = [val.replace(" ", "_") for val in
                                              lineSplit[1:4]]
                            epwSourceDict["location"] = "%s-%s-%s" % (
                            lineSplit[1], lineSplit[2], lineSplit[3])
                            epwSourceDict["longitude"] = round(float(lineSplit[-3]), 3)
                            epwSourceDict["latitude"] = round(float(lineSplit[-4]), 3)

        return epwSourceDict

    @property
    def dailyPhotoPeriod(self):
        diffRadData = self.difRadData
        diffRadDataBinDaily = [diffRadData[idx * 24:(idx * 24) + 23] for idx in
                               range(365)]
        dailyPhotoPeriod = [len([num for num in dayList if num]) for dayList in
                            diffRadDataBinDaily]

        return dailyPhotoPeriod

    @property
    def monthlyPhotoPeriodAvg(self):
        dailyPhotoPeriod = self.dailyPhotoPeriod
        daysInMonths = [calendar.monthrange(2013, monthNum)[-1] for monthNum in
                        range(1, 13)]
        daysInMonthSum = [(sum(daysInMonths[:idx]), sum(daysInMonths[:idx + 1])) for idx
                          in range(12)]
        monthlyPhotoPeriods = [dailyPhotoPeriod[idx[0]:idx[1]] for idx in daysInMonthSum]
        monthlyPhotoPeriodAverage = [round(statistics.mean(monthHours), 2) for monthHours
                                     in monthlyPhotoPeriods]
        return monthlyPhotoPeriodAverage

    def ToString(self):
        """Placeholder for description about """
        summaryList = ["Geographical and Soil Data for %s\n" % self.location]
        summaryList.append(
            "\tLatitude:%0.2f , Longitude: %0.2f" % (self.latitude, self.longitude))
        summaryList.append("\tHardiness-Zone:%s , Tmin: %0.2f, Tmax: %0.2f" % (
        self.hardinessZone, self.tmin, self.tmax))
        summaryList.append("\tAvg Photoperiod(Jan to Dec): (%s)" % (
            ",".join(["%d" % val for val in self.monthlyPhotoPeriodAvg])))
        summaryList.append(
            "\n\nSoil-data matched in Database: Latitude:%0.2f , Longitude: %0.2f, ZipCode:%s" % (
            self.latitudeMatch, self.longitudeMatch, self.zipMatch))
        summaryList.append(
            "Average Photoperiod calculated from diffuse radiation data in EPW file")
        return "\n".join(summaryList)


if _epwFile:
    locationData = LocationData(_epwFile)
    locationDailyPhotoperiod = locationData.dailyPhotoPeriod
    print("Connect the output 'locationData' to text panel to view details")