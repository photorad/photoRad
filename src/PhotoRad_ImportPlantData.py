"""Use this component to import multiple plant data from a text panel or a csv file.
    Inputs:
        _plantDataCsv_: Path of the csv file containing plant data.
        _plantDataList_: A text panel where plant data are specified in individual lines. Each line is of the format: PlantName, DLI value, min Temp, max Temp, HardinessZone, Photoperiod, GrowingSeason.
    Output:
        plantDataList: Multiple instances of PlantData that were imported from the csv file and text panel"""

ghenv.Component.Name = "PhotoRad_ImportPlantData"
ghenv.Component.NickName = 'ImportPlantData'
ghenv.Component.Message = 'VER 0.0.04\nMar_29_2022'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.icon
ghenv.Component.Category = "PhotoRad"
ghenv.Component.SubCategory = "02 | Plants"
try:
    ghenv.Component.AdditionalHelpFromDocStrings = "2"
except:
    pass
__author__ = "Sarith"
__version__ = "2022.03.29"

import rhinoscriptsyntax as rs
import rhinoscriptsyntax as rs
import csv
import scriptcontext as sc
import os

assert "photoRadDict" in sc.sticky, "The core component was not found. Please drag it canvas."


# Create hardiness zones and temeprature ranges corresponding to USDA
def main(csvFilePath, plantDataList):
    PlantData = sc.sticky["photoRadDict"]["plantDataClass"]

    plantList = []
    if csvFilePath:
        assert os.path.exists(
            csvFilePath), "The path for the file %s is not valid" % csvFilePath
        with open(csvFilePath, "rb") as csvStream:
            for idx, lines in enumerate(csvStream):
                if idx:
                    if lines.strip():
                        lineList = lines.strip().split(",")
                        if lineList[0]:
                            plantInstance = PlantData(*lines.strip().split(","))
                            plantList.append(plantInstance)
                            print("Loaded %s from the file %s" % (
                            plantInstance, csvFilePath))

    if plantDataList:
        for lines in plantDataList.split("\n"):
            if lines.strip():
                lineList = lines.strip().split(",")
                if lineList[0]:
                    plantInstance = PlantData(*lineList)
                    plantList.append(plantInstance)
                    print("Loaded %s from the intput _plantDataList_" % (plantInstance))

    return plantList


if _plantDataCsv_ or _plantDataList_:
    plantDataList = main(_plantDataCsv_, _plantDataList_)
