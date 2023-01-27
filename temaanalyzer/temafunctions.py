import csv
import pandas as pd
import re
import math


#the order of keys in these dictionaries determines the order in which columns appear
positionStrings = ['xPosition','yPosition','absPosition']
angleStrings = ['Angle']
velocityStrings = ['xVelocity','yVelocity','absVelocity']
angularVelocityStrings = ['AngularVelocity']
measurementDict = {'Position':positionStrings, 'Angle':angleStrings, 'Velocity':velocityStrings, 'AngularVelocity':angularVelocityStrings}

def getConversion(unit):
    '''
    Returns the cleaned, more intuitively labeled TEMA data file as a Pandas dataframe. This file has standardized units.

    :param unit: The unit prefix for a particular column extracted from the input file.
    :type unit: str

    :return: A tuple containing a scalar multiplier that will convert the data in the DataFrame from the original unit to the standard unit and the string abbreviation of the standard unit we are converting to.
    :rtype: (float,unit)
    '''
    if(unit=='s'): return ('s',1)
    elif(unit=='ms'): return ('s',.001)
    elif(unit=='us'): return ('s',.000001)
    elif(unit=='m'): return ('m',1)
    elif(unit=='mm'): return ('m',.001)
    elif(unit=='cm'): return ('m',.01)
    elif(unit=='rad'): return ('rad',1)
    elif(unit==chr(176)): return ('rad',math.pi/180)
    elif(unit=='degrees'): return ('rad',math.pi/180)
    elif(unit=='pixels'): return ('px',1)
    elif(unit=='px'): return ('px',1)
    else: return (unit,1)

def importTemaData(filename):
    '''
    Returns raw TEMA input data as a Pandas dataframe.

    :param filename: The unit prefix for a particular column extracted from the input file.
    :type filename: str
    :Returns: newDataFrame, a pandas Data Frame that contains the uncleaned content of the input.
    :rtype: DataFrame
    '''
    #construct the header
    with open(filename, newline='', encoding='latin-1', errors='ignore') as csvfile:
            rows = csv.reader(csvfile, delimiter='\t')
            #grab the first three rows
            firstRow = next(rows)
            secondRow = next(rows)
            thirdRow = next(rows)
            #and stitch them together in a single string
            headers = [firstRow[0] + ' ' + thirdRow[0]] + list(map(lambda x,y: x + ' ' + y,firstRow[1:],secondRow[1:]))
    #now read the whole csv, starting from row 3, adding NaNs and using the header constructed above. Drop the empty last column. Return.
    return pd.read_csv(filename,sep='\t',header=0,names=headers,skiprows=range(2),encoding_errors='ignore',dtype='float64',na_values=['X']).drop(columns=' ',errors='ignore')
        
    newDataframe = dataframe.copy()
def exportTemaData(filename,dataframe,columns=None,includeNaN=False):
    '''
    Returns a csv of the TEMA data where the columns have been relabeled and reorderd, and the data has been scaled to standard units.

    :param filename: The name you would like the exported output file to have.  
    :param dataframe: Pandas DataFrame that contains the cleaned and reorderd data.  
    :param columns: List of column names. Including this will result in a subset of the columns being included in the csv file. Default is None.  
    :param includeNAN: Boolean value that determines whether NAN values are included in the exported file. If true, NAN values are included in the exported csv. If false, the corresponding csv rows and columns will be stripped from the export. Default setting is false.
    :type filename: str
    :type dataframe: DataFrame
    :type columns: list
    :type includeNAN: bool
    :returns: None. Saves the cleaned TEMA data as a csv file.
    '''
    newDataframe = dataframe.copy()
    if columns:
        newDataframe = newDataframe[columns]
    #If we don't include NaNs, first strip all NaN-only cols, then strip all rows containing NaNs
    if not includeNaN:
        newDataframe = newDataframe.dropna(axis='columns', how='all')
        newDataframe = newDataframe.dropna(axis='index', how='any')
    newDataframe.to_csv(path_or_buf=filename, index=False)

def standardizeUnits(dataframe):
    '''
    Takes datafram with unknown, and variable units and converts data to standard units of m, s, radians.
    
    :param dataframe: A Pandas DataFrame containing the original, unaltered and unscaled TEMA data.
    :type dataframe: DataFrame
    :Returns: newDataFrame, a pandas DataFrame where the data has been converted to units of s, radians, and m, and the unit names are converted to SI base units.
    '''
    newDataframe = dataframe.copy()
    for col in newDataframe.columns.tolist():
        #extract the unit strings
        unitString = re.findall('\[.+\]', col)
        if(unitString):
            unitString = unitString[-1]
            unit = unitString.strip('[]')
            if '/' in unit:
                #if the unit is a rate, make a list of both units in the rate
                unit1 = re.findall('.*/', unit)[-1].strip('/')
                unit2 = re.findall('/.*', unit)[-1].strip('/')
                unit = [unit1,unit2]
            else:
                #otherwise the unit on its own
                unit = [unit]
            newCol = col
            unitConversion = 1
            for unitItem in unit:
                #for each unititem in the unit list
                unitConversionTuple = getConversion(unitItem)
                
                #replace the unititem name with the standardized equivalent
                newUnitString = unitString.replace(unitItem,unitConversionTuple[0])
                newCol = newCol.replace(unitString,newUnitString)
                
                #If the unititem is the first item in the unit list, assume multiplication
                if (unit[0] == unitItem): unitConversion *= unitConversionTuple[1]
                #If it's the second item, assume division
                else: unitConversion /= unitConversionTuple[1]
                
            newDataframe[col] = newDataframe[col].multiply(unitConversion)
            newDataframe = newDataframe.rename(columns = {col:newCol})
    return newDataframe
        
def stripColUnit(dataframe,columns=None):
    '''
    Returns a Pandas DataFrame of the TEMA data where the units of the columns have been removed. This function needs to be run on the data before it can be plotted using Altair.

    :param dataframe: Pandas DataFrame that contains cleaned and ordered data.
    :param columns: List of column names. Including this will result in a subset of the columns having their units stripped. Default is None.
    :type dataframe: DataFrame
    :type columns: list
    :Returns: newDataFrame, the cleaned TEMA data with the units removed from the column names.
    :rtype: DataFrame
    '''
    newDataframe = dataframe.copy()
    for col in newDataframe.columns.tolist():
        if(not columns or col in columns):
            #get the original unit string
            unitString = re.findall('\[.+\]', col)
            if(unitString):
                unitString = unitString[-1]
                newCol = col.replace(unitString,'')
                newDataframe = newDataframe.rename(columns = {col:newCol})
    return newDataframe
        
def changeColUnit(dataframe,newUnit,columns,scaleFactor=1,inPlace=True):
    '''
    Changes the units of a Pandas DataFrame to be anything other than the standard s, m, radians. Returns a Pandas DataFrame of the TEMA data where the units of the columns have been changed to a user specified input and the data has been scaled accordingly.

    :param dataframe: Pandas DataFrame that contains the cleaned and reorderd data.
    :param columns: List of column names. Including this will result in a subset of the columns having their units stripped. You must include the columns.
    :param newUnit: The new unit as a string that goes in the square brakets of the column label (i.e. [us]).
    :param scaleFactor: The number you multiply the current column values by to get the new, converted values.
    :param inPlace: Determines whether the column values are updated or if you make a new column. Default value is True so the values are updated in place.
    :type dataframe: DataFrame
    :type columns: list
    :type newUnit: str
    :type scaleFactor: float
    :type inPlace: bool
    :Returns: newDataFrame, a Pandas DataFrame of the TEMA data rescaled and relabeled to use the desired units.
    :rtype: DataFrame
    '''
    newDataframe = dataframe.copy()
    for col in newDataframe.columns.tolist():
        if(col in columns):
            #if newUnit is a list, match it to the column
            if isinstance(newUnit,list):
                colNewUnit = newUnit[columns.index(col)]
            else:
                #otherwise, assume all columns use the same newUnit
                colNewUnit = newUnit
            
            #get the original unit string
            unitString = re.findall('\[.+\]', col)
            if(unitString):
                unitString = unitString[-1]
                newCol = col.replace(unitString,'['+colNewUnit+']')
            else:
                newCol = col + colNewUnit
                
            #if in place replacement, rename. Otherwise, add a new column
            if inPlace:
                newDataframe = newDataframe.rename(columns = {col:newCol})
            else:
                newDataframe[newCol] = newDataframe[col]
            
            #if the scale factor is a list, match it to the column
            if isinstance(scaleFactor,list):
                colScaleFactor = scaleFactor[columns.index(col)]
            #otherwise, assume all columns use the same scale factor
            else:
                colScaleFactor = scaleFactor
            
            #multiply the column by the scale factor
            newDataframe[newCol] = newDataframe[newCol].multiply(colScaleFactor)
    return newDataframe
        
def scalePxToDist(dataframe,scaleFactor,columns=None,metersPerPixel=False,inPlace=True):
    '''
    Returns a Pandas DataFrame of the TEMA data where the data has been scaled based on a pixels to meters conversion.

    :param dataframe: Pandas DataFrame that contains the cleaned and reorderd data.
    :param scaleFactor: The number you need to multiply each value in the column by to convert it to meters from pixels. Note that scaleFactor should be in terms of pixels/meter
    :param columns: List of column names. Including this will result in a subset of the columns having their units scaled by the pixel to meter conversion. Default is None.
    :param metersPerPixel: Determines whether you are converting from pixels to meters or meters to pixel. Default value is false, so you are converting using pixels per meter.
    :param inPlace: Determines whether the column values are updated or if you make a new column. Default value is True so the values are updated in place.
    :type dataframe: DataFrame
    :type scaleFactor: float
    :type columns: list
    :type metersPerPixel: bool
    :type inPlace: bool
    :Returns: newDataFrame, a Pandas DataFrame containing the original data scaled by the user-inputted pixel to meter conversion.
    :rtype: DataFrame
    '''
    #default scaleFactor is in pixels per meter
    newDataframe = dataframe.copy()
    for col in newDataframe.columns.tolist():
        if(not columns or col in columns):
            unitString = re.findall('\[.*px.*\]', col)
            #verify that the column is in some factor of pixels
            if (unitString):
                unitString = unitString[-1]
                
                newUnitString = unitString.replace('px','m')
                newCol = col.replace(unitString,newUnitString)
                
                #rename if in-place replacement, else create a new column
                if inPlace:
                    newDataframe = newDataframe.rename(columns = {col:newCol})
                else:
                    newDataframe[newCol] = newDataframe[col]
                
                #if scalefactor is a list, match the scalefactor to the column
                if isinstance(scaleFactor,list):
                    colScaleFactor = scaleFactor[columns.index(col)]
                else:
                    colScaleFactor = scaleFactor
                
                #if our unit is flipped, divide by 1
                if metersPerPixel:
                    colScaleFactor = 1/colScaleFactor
                
                #if px is a numerator unit, divide by the scale factor
                if (re.findall('.*px.*/', unitString) or not '/' in unitString):
                    newDataframe[newCol] = newDataframe[newCol].multiply(1/colScaleFactor)
                #otherwise multiply by the scale factor
                else:
                    newDataframe[newCol] = newDataframe[newCol].multiply(colScaleFactor)
    return newDataframe
        
def calculateVelocity(dataframe,column):
    '''
    Calculated the velocity of a particle based on the x, y and absolute positions. Returns a new Pandas DataFrame where the velocity of the same type (i.e. x, y, abs) as the input position is added as a column to the DataFrame. If the column called does not have units or is already a velocity, the function will return the result as a rate. Function uses central difference velocity calculations

    :param dataframe: Pandas DataFrame that contains the position or input data.
    :param column: The name of the column that you wish to take the velocity or rate of.
    :type dataframe: DataFrame
    :type column: str
    :Returns: newDataFrame, a Pandas DataFrame containing the position or input data as well as the calculated velocity or rate data as an added column.
    :rtype: DataFrame
    '''
    newDataframe = dataframe.copy()
    newColumnName = ''
    newColumnType = ''
    if 'Position' in column:
        #if it's a position, the new velocity will be of the same type
        for string in positionStrings:
            if string in column:
                newColumnName = velocityStrings[positionStrings.index(string)]
                newColumnType = 'Velocity'
    elif 'Angle' in column:
        newColumnName = 'AngularVelocity'
        newColumnType = 'AngularVelocity'
    else:
        #if it's neither an angle nor a position, the new quantity will be a rate of the source column
        newColumnName = re.findall('[^(\[.*\])]*',column)[0] + 'Rate'
    
    newMeasurementIndex = ''
    #get the new measurement's index if not a rate - always 1 more than the existing max index
    if newColumnType:
        maxIndexNumber = 0
        for col in newDataframe.columns.tolist():
            for string in measurementDict[newColumnType]:
                indexNumber = re.findall(string+'[0-9]+',col)
                if indexNumber:
                    indexNumber = int(re.findall('[0-9]+',indexNumber[-1])[-1])
                    if indexNumber > maxIndexNumber: maxIndexNumber = indexNumber
        newMeasurementIndex = str(maxIndexNumber+1)
    
    #get the new measurement's units, if both time and the source column have units
    newUnitString = ''
    timeUnitString = re.findall('\[.+\]', newDataframe.columns[0])
    unitString = re.findall('\[.+\]', column)
    if timeUnitString and unitString:
        newUnitString = '[' + unitString[-1].strip('[]') + '/' + timeUnitString[-1].strip('[]') + ']'
        
    #build the new column name
    newColumnName = newColumnName+newMeasurementIndex+newUnitString
    
    #central difference - assume even spacing
    backwardsDiff = newDataframe[column].diff()
    forwardsDiff = newDataframe[column].diff(periods=-1).multiply(-1)
    backwardsDeltaT = newDataframe[newDataframe.columns[0]].diff()
    forwardsDeltaT = newDataframe[newDataframe.columns[0]].diff(periods=-1).multiply(-1)
    centralDiff = backwardsDiff + forwardsDiff
    totalDeltaT = backwardsDeltaT + forwardsDeltaT
    rate = centralDiff.divide(totalDeltaT)
    
    #assign values to the new column
    newDataframe[newColumnName] = rate
    
    return newDataframe

def standardizeColFormat(dataframe):
    '''
    Returns the intuitively labeled TEMA data file as a Pandas dataframe

    :param dataframe: The name of the Pandas DataFrame you wish to import. At this stage, the DF should be converted to standard units and its units relabeled.
    :type dataframe: DataFrame
    :Returns: newDataFrame, a pandas DataFrame where the column names have been restructured so that they are more intuitive. They should show the expression being shown (position, velocity, etc), component of that expression (x,y), particle number, and unit.
    :rtype: DataFrame
    '''
    newDataframe = dataframe.copy()
    #construct dictionaries to match substrings in the original name to substrings in the new name
    componentPatterns = {' y':'y', ' x':'x', ' abs':'abs'}
    expressionPatterns = {'angular speed':'AngularVelocity', 'Angle':'Angle', 'Velocity':'Velocity', 'Point':'Position', 'Time':'Time', 'Distance':'InterPointDistance'}

    for col in newDataframe.columns.tolist():
        unitString = re.findall('\[.+\]', col)
        if (unitString):
            unitString = unitString[-1]
        else:
            unitString = ''
        
        colNum = re.findall('#[0-9]+', col)
        if colNum:
            colNum = colNum[-1].strip('#')
        else:
            colNum = ''
        
        component = ''
        for componentString in componentPatterns.keys():
            if componentString in col:
                component = componentPatterns[componentString]
                break
        
        expression = 'Unknown'
        for expressionString in expressionPatterns.keys():
            if expressionString in col:
                expression = expressionPatterns[expressionString]
                break

        newColName = component+expression+colNum+unitString
        newDataframe = newDataframe.rename(columns = {col:newColName})
    return newDataframe
    
def standardizeColOrder(dataframe,renumber=False):
    '''
    Returns the cleaned, more intuitively labeled TEMA data file as a Pandas dataframe where the columns are reordered to put position first, followed by velocities, and etc.

    :param dataframe: The Pandas DataFrame containing the relabled, rescaled data.
    :param renumber: Parameter that allows you to renumber the default particle numbers to be in numerical order from 1. False as default. If false, particle numbers will appear exactly as generated in TEMA (i.e. numbers will be associated to particle number labels in TEMA and may skip integers like 1, 2, 4, 7, etc).
    :type dataframe: DataFrame
    :type renumber: bool
    :Returns: newDataFrame, a Pandas DataFrame that contains the TEMA data that is rescaled with the columns re-labeled and re-ordered.
    :rtype: DataFrame
    '''
    newDataframe = dataframe.copy()
    orderedColumns = []
    renumberDict = {}
    orderedColumns.append(newDataframe.columns.tolist()[0])
    
    trackerNumber = 0
    maxIndexNumber = 0
    #the order of keys in these dictionaries determines the order in which columns appear
    positionStrings = ['xPosition','yPosition','absPosition']
    angleStrings = ['Angle']
    velocityStrings = ['xVelocity','yVelocity','absVelocity']
    angularVelocityStrings = ['AngularVelocity']
    distanceStrings = ['xInterPointDistance', 'yInterPointDistance', 'absInterPointDistance']
    measurementDict = {'Position':positionStrings, 'Angle':angleStrings, 'InterPointDistance': distanceStrings,'Velocity':velocityStrings, 'AngularVelocity':angularVelocityStrings}
    
    #First loop over the columns to determine the max index number (we don't care what kind of measurement that number indexes, it's just an upper bound on iteration)
    for col in newDataframe.columns.tolist():
        for measurement in measurementDict.keys():
            indexNumber = re.findall(measurement+'[0-9]+',col)
            if indexNumber:
                indexNumber = int(re.findall('[0-9]+',indexNumber[-1])[-1])
                if indexNumber > maxIndexNumber: maxIndexNumber = indexNumber
    
    #for each type of measurement (position, angle, etc - IN ORDER)
    for measurement in measurementDict.keys():
        #reset the tracker for renumbering
        trackerNumber = 0
        #count up to the max index
        for i in range(1,maxIndexNumber+1):
            #check for each variety of each measurement
            for string in measurementDict[measurement]:
                res = [col for col in newDataframe.columns.tolist() if string+str(i) in col]
                #if it appears, extract it and add that column to the ordered column list
                if res:
                    res = res[0]
                    #double check for an exact match
                    if re.findall(string+str(i)+'\[.+\]',res):
                        orderedColumns.append(res)
                        #if we're also renumbering things, track the number of the measurement of this type and add it to a renumber dictionary
                        if renumber:
                            key = measurement+str(i)
                            if not key in renumberDict:
                                trackerNumber += 1
                                renumberDict[key] = measurement+str(trackerNumber)
    #reindex using new column order
    extraCols = [col for col in newDataframe.columns.tolist() if not col in orderedColumns]
    orderedColumns += extraCols
    newDataframe = newDataframe.reindex(columns=orderedColumns)
    
    #if renumbering, build a rename dictionary
    if renumber:
        renameDict = {}
        keys = renumberDict.keys()
        #for each column, see if there's a key in the renumber dictionary that's in the column name
        for col in newDataframe.columns.tolist():
            for key in keys:
                if key in col:
                    #if there is, add the column name as a key to the rename dictionary and the column name with the replacement applied as that key's entry
                    renameDict[col] = col.replace(key,renumberDict[key])
        #then use the rename dictionary to rename the columns
        newDataframe = newDataframe.rename(columns = renameDict)
    return newDataframe
    
def cleanImportTemaData(filename):
    '''
    Returns the cleaned, more intuitively labeled TEMA data file as a Pandas dataframe using default parameters. This file has standardized units.

    :param filename: The name of the TEMA .txt file you wish to import. Note that the imported file should be a tab delineated text file.
    :type filename: str
    :Returns: newDataFrame, a pandas Data Frame that contains the cleaned content of the input.
    :rtype: DataFrame
    '''
    return standardizeColOrder(
        standardizeColFormat(
            standardizeUnits(
                importTemaData(filename)
            )
        )
    )

    
