import numpy as np
import scipy.io
from pathlib import Path


def readMeta(metaPath):
    """adapted from https://github.com/AllenInstitute/ecephys_spike_sorting originally by jenniferColonell
    # =========================================================
    # Parse ini file returning a dictionary whose keys are the metadata
    # left-hand-side-tags, and values are string versions of the right-hand-side
    # metadata values. We remove any leading '~' characters in the tags to match
    # the MATLAB version of readMeta.
    #
    # The string values are converted to numbers using the "int" and "float"
    # fucntions. Note that python 3 has no size limit for integers.
    #
    """
    metaDict = {}
    if metaPath.exists():
        # print("meta file present")
        with metaPath.open() as f:
            mdatList = f.read().splitlines()
            # convert the list entries into key value pairs
            for m in mdatList:
                csList = m.split(sep='=')
                if csList[0][0] == '~':
                    currKey = csList[0][1:len(csList[0])]
                else:
                    currKey = csList[0]
                metaDict.update({currKey: csList[1]})
    else:
        print("no meta file")
        
    return(metaDict)

# =========================================================
# Return counts of each imec channel type that composes the timepoints
# stored in the binary files.
#
def ChannelCountsIM(meta):
    """adapted from https://github.com/AllenInstitute/ecephys_spike_sorting originally by jenniferColonell
    # =========================================================
    # Return counts of each imec channel type that composes the timepoints
    # stored in the binary files.
    #
    """
    chanCountList = meta['snsApLfSy'].split(sep=',')
    AP = int(chanCountList[0])
    LF = int(chanCountList[1])
    SY = int(chanCountList[2])
    
    return(AP, LF, SY)


def geomMapToGeom(metadict):
    """adapted from https://github.com/AllenInstitute/ecephys_spike_sorting originally by jenniferColonell
    """

    # read in the shank map   
    geomMap = metadict['snsGeomMap'].split(sep=')')
    # shankSep = geomMap[0].split(',')[-1]

    # there is an entry in the map for each saved channel
    # number of entries in map -- subtract 1 for header, one for trailing ')'
    nEntry = len(geomMap) - 2

    shankInd = np.zeros((nEntry,))
    xCoord = np.zeros((nEntry,))
    yCoord = np.zeros((nEntry,))
    connected = np.zeros((nEntry,))
    
    for i in range(nEntry):
        # get parameter list from this entry, skipping first header entry
        currEntry = geomMap[i+1]
        currEntry = currEntry[1:len(currEntry)]
        currList = currEntry.split(sep=':')
        shankInd[i] = int(currList[0])
        xCoord[i] = float(currList[1])
        yCoord[i] = float(currList[2])
        connected[i] = int(currList[3])

    # parse header for number of shanks
    currList = geomMap[0].split(',')
    nShank = int(currList[1]);
    shankPitch = float(currList[2]);
    shankWidth = float(currList[3]);
    
    return nShank, shankWidth, shankPitch, shankInd, xCoord, yCoord, connected#, shankSep


def CoordsToKSChanMap(metadict, chans, xCoord, yCoord, connected, shankInd, shankSep, baseName, savePath, buildPath=True ): 
    """adapted from https://github.com/AllenInstitute/ecephys_spike_sorting originally by jenniferColonell
    Mostly needed for double-length IMRO or other particular channel maps, for Kilosort to read properly.
    Feed in .meta file to get '.mat' channel map for kilosort, in GUI load in "Probe Layout". 
    """
    if buildPath:
        newName = baseName +'_kilosortChanMap.mat'
        saveFullPath = Path(savePath / newName)
    else:
        saveFullPath = savePath
    
    nChan = chans.size
    # channel map is the order of channels in the file, rather than the 
    # original indicies of the channels
    chanMap0ind = np.arange(0,nChan,dtype='float64')
    chanMap0ind = chanMap0ind.reshape((nChan,1))
    chanMap = chanMap0ind + 1
    
    connected = (connected==1)
    try:
        connected = connected.reshape((nChan,1))
    except ValueError:
        print(f"Error reshaping connected array: {connected.shape} to {(nChan,1)}")
        return

    xCoord = shankInd*shankSep + xCoord
    xCoord = xCoord.reshape((nChan,1))
    yCoord = yCoord.reshape((nChan,1))
    
    kcoords = shankInd + 1
    kcoords = kcoords.reshape((nChan,1))
    kcoords = kcoords.astype('float64')
    
    name = baseName
    
    mdict = {
            'chanMap':chanMap,
            'chanMap0ind':chanMap0ind,
            'connected':connected,
            'name':name,
            'xcoords':xCoord,
            'ycoords':yCoord,
            'kcoords':kcoords,
            }
    scipy.io.savemat(saveFullPath, mdict)