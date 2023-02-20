
import matplotlib.pyplot as plt
from SoLoCalc.util.files.paths import FileObj,Directory
import pandas as pd

allFiles=Directory(r"C:\Users\SarithS\Downloads\Compressed\equatorialskies-master"
                   r"\datasets").fileNamesAbsolute(filterLettersInclude='.csv')

allObjs=[FileObj(fn) for fn in allFiles]
allNames=[fo.nameOnly.split('-') for fo in allObjs]
allNameStamp=["%s_%s"%(fo[-1],fo[0]) for fo in allNames]

fig, ax = plt.subplots(figsize=(10, 8))

def calcEffectivePPFD(wavSPD):
    avo=6.022E+23
    pla=6.626E-34
    lig=2.998*(10**8)
    nm=10**-9
    mol_m2_s1=wavSPD['wv']*wavSPD['spd']*nm/(avo*pla*lig)
    return sum(mol_m2_s1)

for idx,fn in enumerate(allFiles):
    if '13Dec' in allNameStamp[idx]:
        a = pd.read_csv(fn)[40:-80]
        relSPD=a['spd']/max(a['spd'])
        effectiveSPD = calcEffectivePPFD(a)
        spdNum,dig=str(effectiveSPD).split('e-')

        label=allNameStamp[idx]+f'_{spdNum[:4]}e-{dig}'
        ax.plot(a['wv'],relSPD,label=label)


plt.xlabel('Wavelength (nm)')
plt.ylabel('Relative SPD')
plt.title(f'Daylight Source SPDs) for Singapore')
ax.legend()
plt.show()