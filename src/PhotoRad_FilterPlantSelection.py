"""Performing filtering of plants based on DLI levels.
    Inputs:
        _dliData: The output from the dliData component.
        _dliFilterResult: The dliFilterResult output from the PhotoRad AnalyzePlantSelection component.
    Output:
        allOptions: Generates an indexed list of all the combinations(without repetition) of the plants.
        selection: Provides the selection made for a specific grid/space.
        selectionGrid: Provides a list of indicies corresponding to the selection made. A single selection is applied to the entire grid.
        selectionGridNodal: Provides a list of indicies corresponding to the selection made. The selection is applied according to individual nodes instead of the entire grid.
        selectComboNames: The subset of combinations (allOptions) that were used to make the plant selections. This can be used to create a chart title.
"""

from __future__ import division

ghenv.Component.Name = "PhotoRad_FilterPlantSelection"
ghenv.Component.NickName = 'FilterPlantSelection'
ghenv.Component.Message = 'VER 0.0.04\nMay_29_2022'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.icon
ghenv.Component.Category = "PhotoRad"
ghenv.Component.SubCategory = "2 | Analysis"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


__author__ = "SarithS"
__version__ = "2022.05.29"

import rhinoscriptsyntax as rs
import itertools

def selectPlants(dliFilterResult,dliData):
    dliNameList=[]

    nameListFinal=[[]]*dliData.dataSize[0]
    for result in dliFilterResult:
        if result.dliData==dliData:
            nameList=[[result.plantInstance.name] if val==1 else [] for val in result.dliRangeList]
            nameListFinal=[val+nameList[idx] for idx,val in enumerate(nameListFinal)]
    nameListFinal=[tuple(sorted(val)) for val in nameListFinal]
    nameListFinalSet=list(set(nameListFinal))

    plantList=sorted(set([val.plantInstance.name for val in dliFilterResult]))
    combinations=list(itertools.chain(*[list(itertools.combinations(plantList,len(plantList)-idx)) for \
            idx,plant in enumerate(plantList)]))+[()]
    comboWithID=list(enumerate(combinations))
    plantDLICombo=[val for val in dliFilterResult if val.dliData==dliData]
    selection=tuple(sorted([val.plantInstance.name for val in plantDLICombo if val.selection]))
    selectionIndex=combinations.index(selection)
    nameListFinal=[combinations.index(val) for val in nameListFinal]
    nameListFinalSet="\n".join(["%02d: %s"%(combinations.index(val),", ".join(val) if val else "None") for val in nameListFinalSet])
    print(nameListFinalSet)
    gridSize=dliData.dataSize[0]
    selectionGrid=[selectionIndex]*gridSize

    return {'allOptions':comboWithID,'selection':selection,'selectionGrid':selectionGrid,'nameListFinal':nameListFinal,'selectedCombo':nameListFinalSet}

if _dliFilterResult and _dliData:
    results=selectPlants(_dliFilterResult,_dliData)
    allOptions=results['allOptions']
    selection=results['selection']
    selectionGrid=results['selectionGrid']
    selectionGridNodal=results['nameListFinal']
    selectComboNames=results["selectedCombo"]