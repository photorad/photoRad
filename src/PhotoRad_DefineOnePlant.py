"""Use this component to define a single plant type. At the very least, the values for _name and _dli are required. 
If only one among (_minTemp_,_maxTemp_) or _hrdZone_ is provided then the other value be calculated from the provided input. e.g.
If _minTemp_,_maxTemp_ and _hrdZone_ are all provided, then the values for _minTemp_ and _maxTemp_ will be used to determine the _hrdZone_
    Inputs:
        _name: Name of the plant.
        _dli: A single value or a set of 12 space-separated values corresponding to the DLI requirement for the plant. 
        A single value implies that the DLI requirement is the same though out the year. 12 values imply that an individual input has
        been provided for every month of the year.
        _minTemp_: Minimum suitable temperature.
        _maxTemp_: Maximum suitable temperature.
        _hrdZone_: Hardiness zone.
        _photoPeriod_:A single value or a set of 12 space-separated values corresponding to the photoperiod requirement for the plant. 
        A single value implies that the photoPeriod requirement is the same though out the year. 12 values imply that an individual input has
        been provided for every month of the year.
                _growSeason_: Growing season expressed as months from 1 (Jan) to 12 (Dec). This can be a single value or multiple space separated values.
    Output:
        plantData: A single instance of the class containing PlantData that was defined as per the provided inputs."""


ghenv.Component.Name = "PhotoRad_DefineOnePlant"
ghenv.Component.NickName = 'Define_One_Plant'
ghenv.Component.Message = 'VER 0.0.05\nJun_02_2022'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.icon
ghenv.Component.Category = "PhotoRad"
ghenv.Component.SubCategory = "01 | Plants"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

__author__ = "SarithS"
__version__ = "2022.06.02"

#Notes to self:
#If multiple hardiness zones are provided choose the min and max temps based on the lowest and highest values for zones.
#The input for _dli can be a single value or 12 space separated values.
#If everything is provided, min and max temp will over-ride hardiness values.
#If no photoperiod is provided, set it 0, implying that no light is needed. This will prevent it from being filtered out.


import rhinoscriptsyntax as rs
import csv
import scriptcontext as sc

assert "photoRadDict" in sc.sticky,"The core component was not found. Please drag it canvas."
#Create hardiness zones and temeprature ranges corresponding to USDA

def main(_name,_dli,_minTemp_,_maxTemp_,_hrdZone_,_photoPeriod_,_growSeason_):
    _photoPeriod_=_photoPeriod_ or ""
    PlantData=sc.sticky["photoRadDict"]["plantDataClass"]
    return PlantData(_name,_dli,_minTemp_,_maxTemp_,_hrdZone_.split(),_photoPeriod_,_growSeason_)



if _name and _dli:
    plantData=main(_name,_dli,_minTemp_,_maxTemp_,_hrdZone_,_photoPeriod_,_growSeason_)