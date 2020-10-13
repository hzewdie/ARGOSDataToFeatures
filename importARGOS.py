##---------------------------------------------------------------------
## ImportARGOS.py
##
## Description: Read in ARGOS formatted tracking data and create a line
##    feature class from the [filtered] tracking points
##
## Usage: ImportArgos <ARGOS folder> <Output feature class> 
##
## Created: Fall 2018
## Author: Hiwot Zewdie (for ENV859)
##---------------------------------------------------------------------

# Import modules
import sys, os, arcpy

# Allow arcpy to overwrite oupputs
arcpy.env.overwriteOutput = True

# Set input variables (Hard-wired)
inputFile = 'V:/ARGOSTracking/Data/ARGOSData/1997dg.txt'
outputFC = "V:/ARGOSTracking/Scratch/ARGOStrack.shp"
outputSR = arcpy.SpatialReference(54002)

#create an empty feature class to which we will add features 
outPath, outName =os.path.split(outputFC)
arcpy.CreateFeatureclass_management(outPath,outName, "POINT",'','','',outputSR)

#add field to our new feature class

# Add TagID, LC, IQ, and Date fields to the output feature class
arcpy.AddField_management(outputFC,"TagID","LONG")
arcpy.AddField_management(outputFC,"LC","TEXT")
arcpy.AddField_management(outputFC,"Date","DATE")

# create an inset cursor: enable me to access files 
cur = arcpy.da.InsertCursor(outputFC,["Shape@", "TagID", "LC", "Date"])
#%% Construct a while loop to iterate through all lines in the datafile
#open the ARGOS datafile for reading

inputFileObj = open(inputFile, 'r')

#get the first line of data, so we can use the while lioop
lineString = inputFileObj.readline()

#start the line loop
while lineString:
    
     # Set code to run only if the line contains the string "Date: "
    if ("Date :" in lineString):
        
        # Parse the line into a list
        lineData = lineString.split()
        
        # Extract attributes from the datum header line
        tagID = lineData[0]
        date = lineData[3]
        time = lineData[4]
        LC = lineData[7]
        # Extract location info from the next line
        line2String = inputFileObj.readline()
        
        # Parse the line into a list
        line2Data = line2String.split()
        
        # Extract the date we need to variables
        obsLat = line2Data[2]
        obsLon= line2Data[5]
        
        try:
              # Convert raw coordinate strings to numbers
            if obsLat[-1] == 'N':
                obsLat = float(obsLat[:-1])
            else:
                obsLat = float(obsLat[:-1]) * -1
            if obsLon[-1] == 'E':
                obsLon = float(obsLon[:-1])
            else:
                obsLon = float(obsLon[:-1]) * -1
            
            #Create a point object 
            obsPoint = arcpy.Point()
            obsPoint.X = obsLon
            obsPoint.Y = obsLat
            
        except Exception as e:
            print(f"Error adding record {tagID} to the output")
            
        #convert point to a geometric point, with spatial reference 
        inputSR = arcpy.SpatialReference(4326)
        obsGeomPoint = arcpy.PointGeometry(obsPoint,inputSR)
        
        # add a feature using our insert cursor
        feature = cur.insertRow((obsGeomPoint,tagID,LC,date.replace(".","/") + " " + time))
        # Print results to see how we're doing
        #print (tagID, date,time,LC,"Lat:"+obsLat,"Long:"+obsLon)
        
    # Move to the next line so the while loop progresses
    lineString = inputFileObj.readline()
    
#Close the file object
inputFileObj.close()

#delete the cursor 
del cur