from temaanalyzer import temafunctions
import os
import pandas as pd
import numpy as np

filename = "notebook/temaanalyzer/tests/TEMATotalHeader.txt"
#filename2 = 
velocityTest1File = "notebook/temaanalyzer/tests/velocityTest1.txt"
velocityTest3File = "notebook/temaanalyzer/tests/velocityTest3.txt"
pxScaleTest1File = "notebook/temaanalyzer/tests/pxScaleTest1.txt"
print(os.getcwd())


#tests for importTemaData(filename)
def test_import():
    temaData = temafunctions.importTemaData(filename)
    assert not temaData.empty

#tests for getConversion(unit)
#Check we are getting the correct prefix and conversion from input unit to s, m, radians
def test_getConversion_s():
    assert temafunctions.getConversion('s') == ('s',1)
def test_getConversion_us():
    assert temafunctions.getConversion('us') == ('s',.000001)

#tests for standardizeunits(dataframe)
def test_standardizeUnits_time():
    importData = temafunctions.importTemaData(filename)
    standardUnitDf = temafunctions.standardizeUnits(importData)
    colNames = list(standardUnitDf.columns)
    assert colNames[0] == 'Time [s]'

def test_standardizeUnits_xVel():
    importData = temafunctions.importTemaData(filename)
    standardUnitDf = temafunctions.standardizeUnits(importData)
    colNames = list(standardUnitDf.columns)
    assert colNames[5] == 'Velocity (Default/Point#1) x[m/s]'

#tests for stripColUnit(dataframe, columns = None)
def test_stripColUnit():
    dataframe = temafunctions.cleanImportTemaData(filename)
    newdf = temafunctions.stripColUnit(dataframe,columns=None)
    expectedhead = ['Time','xPosition1','yPosition1','absPosition1','Angle1','xVelocity1','yVelocity1','absVelocity1','AngularVelocity1']
    assert list(newdf.columns) == expectedhead


#tests for changeColUnit(dataframe,columns,newUnit,scaleFactor=1,inPlace=True)
def test_changeColUnit():
    dataframe = temafunctions.cleanImportTemaData(filename)
    scaleddf = temafunctions.changeColUnit(dataframe, newUnit = 'us',columns = ['Time[s]'],scaleFactor=1/.000001,inPlace=True)
    expectedhead = ['Time[us]','xPosition1[m]','yPosition1[m]','absPosition1[m]','Angle1[rad]','xVelocity1[m/s]','yVelocity1[m/s]','absVelocity1[m/s]','AngularVelocity1[rad/s]']
    assert list(scaleddf.columns) == expectedhead

    #should make way for this function to automatically know the conversion
    #tldr this function needs some work.


#tests for standardizeColFormat(dataframe)
def test_standardizeColFormat():
    temaData = temafunctions.importTemaData(filename)
    standardUnitdf = temafunctions.standardizeUnits(temaData)
    standardFormatDF = temafunctions.standardizeColFormat(standardUnitdf)
    expectedhead = ['Time[s]','xPosition1[m]','yPosition1[m]','absPosition1[m]','absVelocity1[m/s]','xVelocity1[m/s]','yVelocity1[m/s]','Angle1[rad]','AngularVelocity1[rad/s]']
    assert list(standardFormatDF.columns) == expectedhead

#tests for standardizeColOrder(dataframe,renumber=False)
def test_standardizeColOrder():
    temaData = temafunctions.importTemaData(filename)
    standardUnitdf = temafunctions.standardizeUnits(temaData)
    standardFormatDF = temafunctions.standardizeColFormat(standardUnitdf)
    standardOrderDF = temafunctions.standardizeColOrder(standardFormatDF)
    expectedhead = ['Time[s]','xPosition1[m]','yPosition1[m]','absPosition1[m]','Angle1[rad]','xVelocity1[m/s]','yVelocity1[m/s]','absVelocity1[m/s]','AngularVelocity1[rad/s]']
    assert list(standardOrderDF.columns) == expectedhead


#tests for scalePxToDist(dataframe,scaleFactor,columns=None,metersPerPixel=False,inPlace=True)
#this makes sense to do here
def test_scalePxToDist():
    dataframe = temafunctions.cleanImportTemaData(pxScaleTest1File)
    scaleddf = temafunctions.scalePxToDist(dataframe,scaleFactor = 0.2,columns=None,metersPerPixel=False,inPlace=True)
    temafunctions.exportTemaData('notebook/temaanalyzer/tests/cleanedpxConvertTest1.csv',scaleddf,includeNaN=True) #uncomment to make a new file. 0s inserted into original file to avoid nan !=nan error
    #listOfPx = scaleddf['xVelocity1[m/s]'].tolist()
    #assert


#tests for calculateVelocity(dataframe,column)
#make fake file to calculate velocity with
def test_calculateVelocity_file1():
    dataframe = temafunctions.cleanImportTemaData(velocityTest1File)
    newdf = temafunctions.calculateVelocity(dataframe,column = 'xPosition1[m]')
    #temafunctions.exportTemaData('cleanedVelTest1.csv',newdf,includeNaN=True) #uncomment to make a new file. 0s inserted into original file to avoid nan !=nan error
    velocitydf = pd.read_csv('notebook/temaanalyzer/tests/cleanedVelTest1.csv')
    listofVelocities = velocitydf['xVelocity1[m/s]'].tolist()
    expectedV = [0.0,0.008,0.008,0.008,0.008,0.008,0.008,0.008,0.008,0.008,0.0]
    assert listofVelocities == expectedV

def test_calculateVelocity_file2():
    dataframe = temafunctions.cleanImportTemaData(velocityTest1File)
    newdf = temafunctions.calculateVelocity(dataframe,column = 'yPosition1[px]')
    #temafunctions.exportTemaData('cleanedVelTest2.csv',newdf,includeNaN=True) #uncomment to make a new file. 0s inserted into original file to avoid nan !=nan error
    velocitydf = pd.read_csv('notebook/temaanalyzer/tests/cleanedVelTest2.csv')
    listofVelocities = velocitydf['yVelocity1[px/s]'].tolist()
    expectedV = [0.0,8,8,8,8,8,8,8,8,8,0.0]
    assert listofVelocities == expectedV

def test_calculateVelocity_nonLinear():
    dataframe = temafunctions.cleanImportTemaData(velocityTest3File)
    newdf = temafunctions.calculateVelocity(dataframe,column = 'xPosition1[m]')
    #temafunctions.exportTemaData('notebook/temaanalyzer/tests/cleanedVelTest3.csv',newdf,includeNaN=True) #uncomment to make a new file. 0s inserted into original file to avoid nan !=nan error
    velocitydf = pd.read_csv('notebook/temaanalyzer/tests/cleanedVelTest3.csv')
    listofVelocities = velocitydf['xVelocity1[m/s]'].tolist()
    expectedV = [0.0,0.176,0.008,0.052,0.008,-0.18,0.008,-0.02,0.004,0.012,0.0]
    assert listofVelocities == expectedV

#test average velocity function