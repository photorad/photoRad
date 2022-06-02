"""

A component to consolidate, view and export PlantData.
    Inputs:
        _plantDataList: List of plantData. The input for this will typically be the output from the component PhotoRad_ImportPlantData
        _indxForSmry_: The index of the plant from the _plantDataList whose summary is to be displayed in indSummary.
        opCsvPath_:Output csv file path to which the plant data is to be exported.
        _overWrtExistCsv_:Is set to True, then if the file already exists, it will be overwritten.
    Output:
        loadedList: List of all the loaded plants.
        indSummary: Individual summary of a single plant."""



ghenv.Component.Name = "PhotoRad_ConsolidatePlantData"
ghenv.Component.NickName = 'Consolidate_Plant_Data'
ghenv.Component.Message = 'VER 0.0.05\nJun_02_2022'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.icon
ghenv.Component.Category = "PhotoRad"
ghenv.Component.SubCategory = "02 | Plants"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

__author__ = "Sarith"
__version__ = "2022.06.02"

import rhinoscriptsyntax as rs
import warnings
import Grasshopper.Kernel as gh
import os
import shutil

def loadPlantList(plantDataList):
    plantList=[]

    for plantInst in plantDataList:
        plantList.append(plantInst.name)

    return plantList

def writeCsvFile(plantDataList,opCsvPath,overWriteExisting):

    if os.path.exists(opCsvPath):
        if overWriteExisting:
            shutil.copy(opCsvPath,opCsvPath+"bak")
            msg="The file %s was overwritten. A backup has been stored at %s"%(opCsvPath,opCsvPath+"bak")
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        else:
            raise Exception("The path %s already exists. Either provide a different path or set the input _overWrtExistCsv_ to True"%opCsvPath)


    with open(opCsvPath,"w") as outputStream:
        outputStream.write("PlantSpecies,DLI,minTemp,maxTemp,HardinessZone,Photoperiod,GrowingSeason\n")
        for plantInst in plantDataList:
            outputStream.write("%s\n"%plantInst.csvString)

    print("The details of %s plants has been exported to %s"%(len(plantDataList),opCsvPath))


if _plantDataList:
    loadedList=loadPlantList(_plantDataList)

    if _indxForSmry_>=len(_plantDataList):
        msg="The value for _indxForSmry_(%s) exceeds the total number of entries (%s) in _plantDataList"%(_indxForSmry_,len(_plantDataList))
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        _indxForSmry_=len(_plantDataList)-1

    indSummary=_plantDataList[_indxForSmry_].summary

    if opCsvPath_:
        writeCsvFile(_plantDataList,opCsvPath_,_overWrtExistCsv_)