import arcpy, os, shutil, zipfile, datetime

arcpy.AddMessage ("""
    #-------------------------------------------------------------------------------
    # Name:        YorkCounty_DataExtractor.py
    # Purpose:     Extracts county data to a file geodatabase, zips the geodatabase
    #              at the following location: O:\IS\DataRequests\Extractor
    #
    # Authors:     Joseph Simora (York)
    #
    # Created:     December 04, 2017
    # Updated:     December 27, 2017
    # Copyright:   (c) York County Planning Commission (YCPC)
    #-------------------------------------------------------------------------------
    """)

# definition function to copy GDB file to a zipfile
def dir_zip(dirPath=None, zipFilePath=None, includeDirInZip=True):
    """Create a zip archive from a directory."""
    if not zipFilePath:
        zipFilePath = dirPath + ".zip"
    if not os.path.isdir(dirPath):
        raise OSError("dirPath argument must point to a directory. "
            "'%s' does not." % dirPath)
    parentDir, dirToZip = os.path.split(dirPath)

    def trimPath(path):
        """Prepare the proper archive path"""
        archivePath = path.replace(parentDir, "", 1)
        if parentDir:
            archivePath = archivePath.replace(os.path.sep, "", 1)
        if not includeDirInZip:
            archivePath = archivePath.replace(dirToZip + os.path.sep, "", 1)
        return os.path.normcase(archivePath)

    outFile = zipfile.ZipFile(zipFilePath, "w", compression=zipfile.ZIP_DEFLATED)
    for (archiveDirPath, dirNames, fileNames) in os.walk(dirPath):
        for fileName in fileNames:
            filePath = os.path.join(archiveDirPath, fileName)
            outFile.write(filePath, trimPath(filePath))
        #Make sure we get empty directories as well
        if not fileNames and not dirNames:
            zipInfo = zipfile.ZipInfo(trimPath(archiveDirPath) + "/")
            outFile.writestr(zipInfo, "")
    outFile.close()

arcpy.env.overwriteOutput = 1
arcpy.env.workspace = r"O:\IS\GIS_Connections\GIS@York.sde"


# variable used in Select by Attibute step (Line
feature_select = "Feature_Select"
# First Parameter in Script. Selects Layer that you will be clipping data
clip_feature = arcpy.GetParameterAsText(1)
# Splits Directory path of clip features
clip_name = clip_feature.split("\\")[-1]
# Directory/Folder of GDB that script creates
outfolder = r"O:\IS\Model\Extractor\Test_Extractor.gdb"
# Variable to add buffer distance
BufferDist = arcpy.GetParameterAsText(3)

# Local variables:
York_Edit_GIS_Land_Base_CAMA = os.path.join(arcpy.env.workspace, r"York.GIS.Land_Base_CAMA")
GIS_Land_Base_CAMA_View = "GIS.Land_Base_CAMA_View"
GIS_Land_Base_CAMA_View__2_ = GIS_Land_Base_CAMA_View
Parcels = os.path.join(outfolder,"Parcels")
CAMA_Records = os.path.join(outfolder,"CAMA_Records")
CAMA_Records_Parcels = os.path.join(outfolder,"CAMA_Records_Parcels")

arcpy.AddMessage("Prepping Temporary File GDB at {}...\n".format(outfolder))
# Deletes existing Temp GDB
arcpy.Delete_management(outfolder, "Workspace")
# Creates a new File GDB
arcpy.CreateFileGDB_management("O:\IS\Model\Extractor", "Test_Extractor.gdb", arcpy.GetParameterAsText(7))

# Select By Attribute Steps
arcpy.MakeFeatureLayer_management(clip_feature, feature_select, "")
arcpy.SelectLayerByAttribute_management(feature_select, "NEW_SELECTION", arcpy.GetParameterAsText(2))

# Steps to add feature to for loop
Features = arcpy.GetParameterAsText(4)
FeatureTypeList = Features.split(";")

# Creates Buffer
arcpy.AddMessage("Creating Buffer Feature From Clipped Feature....\n")
buffer_featureclass = os.path.join(outfolder, "Buffered_Area")
arcpy.Buffer_analysis(feature_select, buffer_featureclass, BufferDist)

#Loops thru Features (Line 54) provided
for items in FeatureTypeList:
    # Splits Directory Path of items(FeatureTypeList)
    name = items.split("\\")[-1]
    # Splits nae variable
    name_new = name.split(".")[-1]
    arcpy.AddMessage ("Starting to Clip {} Feature Class from {}.....".format(name_new, clip_name))
    # Joins Path for input location
    input_feature = os.path.join(arcpy.env.workspace,name_new)
    # Joins Path for output location
    out_feature_class = os.path.join(outfolder, name_new)
    # Buffer Steps
    if (BufferDist != 0):
          arcpy.Clip_analysis(input_feature, buffer_featureclass, out_feature_class)
          arcpy.AddMessage ("Completed Clipping {} Feature Class\n".format(name_new))
    else:
        arcpy.Clip_analysis(input_feature, buffer_featureclass, out_feature_class)
        arcpy.AddMessage ("Completed Clipping {} Feature Class\n".format(name_new))

del items

# Creates Boundary Layer
arcpy.Select_analysis(feature_select, os.path.join(outfolder,"Boundary"))

# Creates new folder
folder_name = ("O:\IS\DataRequests\Extractor\{}".format(arcpy.GetParameterAsText(5)))

if not os.path.exists(folder_name):
    arcpy.AddMessage ("Creating Extract Workspace at {}\n".format(folder_name))
    os.makedirs(folder_name)
else:
    arcpy.AddMessage ("Overwritting Workspace at {}\n".format(folder_name))
    shutil.rmtree(folder_name)
    os.makedirs(folder_name)

# Variable to add date time info to data
date_string = datetime.date.today().strftime("%Y%m%d")
# variable to add GDB Name
GDB_name = arcpy.GetParameterAsText(6)
# variable to create output GDB Location
output_GDB = os.path.join (folder_name, GDB_name + "_" + date_string + ".gdb")
# variable to create output zipfile Location
output_zip = os.path.join (folder_name, GDB_name + "_" + date_string + ".zip" )

DataType = arcpy.GetParameterAsText(0)
Boolean = arcpy.GetParameterAsText(8)
if DataType == "File Geodatabase":
    if arcpy.Exists(os.path.join(outfolder, "Parcels")) and Boolean == 'true':
        arcpy.AddMessage("The check box was selected to include CAMA and Relationship Class added to Extracted Data. Adding CAMA Information\n")
        # Process: Make Table View
        arcpy.MakeTableView_management(York_Edit_GIS_Land_Base_CAMA, GIS_Land_Base_CAMA_View, "", "",\
         "OBJECTID OBJECTID VISIBLE NONE;\
         PIDN PIDN VISIBLE NONE;\
         DISTRICT DISTRICT VISIBLE NONE;\
         BLOCK BLOCK VISIBLE NONE;MAP MAP VISIBLE NONE;\
         PARCEL PARCEL VISIBLE NONE;\
         PARCEL_MAJOR PARCEL_MAJOR VISIBLE NONE;\
         PARCEL_MINOR PARCEL_MINOR VISIBLE NONE;\
         LEASEHD LEASEHD VISIBLE NONE;\
         PIDN_LEASE PIDN_LEASE VISIBLE NONE;\
         CARD_NO CARD_NO VISIBLE NONE;\
         MASTER MASTER VISIBLE NONE;\
         DEED_BK DEED_BK VISIBLE NONE;\
         DEED_PG DEED_PG VISIBLE NONE;\
         SITE_ST_NO SITE_ST_NO VISIBLE NONE;\
         SITE_ST_DIR SITE_ST_DIR VISIBLE NONE;\
         SITE_ST_NAME SITE_ST_NAME VISIBLE NONE;\
         SITE_ST_SUF SITE_ST_SUF VISIBLE NONE;\
         PROPADR PROPADR VISIBLE NONE;\
         OWNER_FULL OWNER_FULL VISIBLE NONE;\
         OWN_NAME1 OWN_NAME1 VISIBLE NONE;\
         OWN_NAME2 OWN_NAME2 VISIBLE NONE;\
         MAIL_ADDR_FULL MAIL_ADDR_FULL VISIBLE NONE;\
         MAIL_ADDR1 MAIL_ADDR1 VISIBLE NONE;\
         MAIL_ADDR2 MAIL_ADDR2 VISIBLE NONE;\
         MAIL_ADDR3 MAIL_ADDR3 VISIBLE NONE;\
         PREV_OWNER PREV_OWNER VISIBLE NONE;\
         CLASS CLASS VISIBLE NONE;\
         LUC LUC VISIBLE NONE;\
         ACRES ACRES VISIBLE NONE;\
         STYLE STYLE VISIBLE NONE;\
         NUM_STORIE NUM_STORIE VISIBLE NONE;\
         RES_LIVING_AREA RES_LIVING_AREA VISIBLE NONE;\
         YRBLT YRBLT VISIBLE NONE;\
         CLEAN_GREEN CLEAN_GREEN VISIBLE NONE;\
         HEATSYS HEATSYS VISIBLE NONE;\
         FUEL FUEL VISIBLE NONE;\
         UTILITY UTILITY VISIBLE NONE;\
         APRLAND APRLAND VISIBLE NONE;\
         APRBLDG APRBLDG VISIBLE NONE;\
         APRTOTAL APRTOTAL VISIBLE NONE;\
         SALEDT SALEDT VISIBLE NONE;\
         PRICE PRICE VISIBLE NONE;\
         PREV_PRICE PREV_PRICE VISIBLE NONE;\
         SCHOOL_DIS SCHOOL_DIS VISIBLE NONE;\
         COMM_STRUC COMM_STRUC VISIBLE NONE;\
         COMM_YEAR_BUILT COMM_YEAR_BUILT VISIBLE NONE;\
         COMM_BUILDING_SQ_FT COMM_BUILDING_SQ_FT VISIBLE NONE;\
         GRADE GRADE VISIBLE NONE;\
         CDU CDU VISIBLE NONE;\
         GlobalID GlobalID VISIBLE NONE;\
         HYPERLINK HYPERLINK VISIBLE NONE")

        # Process: Add Join
        arcpy.AddJoin_management(GIS_Land_Base_CAMA_View, "PIDN", Parcels, "PIDN", "KEEP_COMMON")

        # Process: Table Select
        arcpy.TableSelect_analysis(GIS_Land_Base_CAMA_View, CAMA_Records, "")

        # Process: Create Relationship Class
        arcpy.CreateRelationshipClass_management(CAMA_Records, Parcels, CAMA_Records_Parcels, "SIMPLE", "Parcels", "CAMA_Records", "BOTH", "ONE_TO_ONE", "NONE", "OBJECTID", "OBJECTID", "", "")

        #Process: Remove Join
        arcpy.RemoveJoin_management(GIS_Land_Base_CAMA_View)

    else:
        arcpy.AddMessage("The check box was not selected to include CAMA and Relationship Class added to Extracted Data\n")

    if arcpy.Exists(os.path.join(outfolder, "Contours_2FT")):
        arcpy.AddMessage ("Selecting 10FT Contours and Creating {}\n".format(os.path.join(outfolder, "Contours_10FT")))
        arcpy.MakeFeatureLayer_management(os.path.join(outfolder, "Contours_2FT"),GIS_Land_Base_CAMA_View,"CONT_TYPE = 'INDEX DEPRESSION' OR CONT_TYPE = 'INDEX CONTOUR'")
        arcpy.Select_analysis(GIS_Land_Base_CAMA_View,os.path.join(outfolder, "Contours_10FT"))
        arcpy.Delete_management(GIS_Land_Base_CAMA_View)

    arcpy.AddMessage ("Copying Extract GDB from {} to Extract Folder Location Workspace at {}\n".format(outfolder,folder_name))
    #Coppies GDB in Temp Location to New Folder
    shutil.copytree(outfolder,output_GDB)
    arcpy.AddMessage ("Zipping File GDB from {} and creating zip file:\n {}\n ".format(output_GDB,output_zip))
    # Step to zip GDB in New Folder Location
    dir_zip(output_GDB, output_zip, True)

if DataType == "Shapefile":
    arcpy.env.workspace = outfolder
    if arcpy.Exists(os.path.join(outfolder, "Contours_2FT")):
        arcpy.AddMessage ("Selecting 10FT Contours and Creating {}\n".format(os.path.join(outfolder, "Contours_10FT")))
        arcpy.MakeFeatureLayer_management(os.path.join(outfolder, "Contours_2FT"),GIS_Land_Base_CAMA_View,"CONT_TYPE = 'INDEX DEPRESSION' OR CONT_TYPE = 'INDEX CONTOUR'")
        arcpy.Select_analysis(GIS_Land_Base_CAMA_View,os.path.join(outfolder, "Contours_10FT"))
        arcpy.Delete_management(GIS_Land_Base_CAMA_View)
    ConvertFeatures = arcpy.ListFeatureClasses()
    arcpy.AddMessage ("Starting Converting to Shapefile....")
    for FC in ConvertFeatures:
        arcpy.AddMessage ("Converting {} Feature Class to Shapefile....\n".format(FC))
        arcpy.FeatureClassToShapefile_conversion(FC,folder_name)

if DataType == "Both":
    if arcpy.Exists(os.path.join(outfolder, "Parcels")) and Boolean == 'true':
        arcpy.AddMessage("The check box was selected to include CAMA and Relationship Class added to Extracted Data. Adding CAMA Information\n")
        # Process: Make Table View
        arcpy.MakeTableView_management(York_Edit_GIS_Land_Base_CAMA, GIS_Land_Base_CAMA_View, "", "",\
         "OBJECTID OBJECTID VISIBLE NONE;\
         PIDN PIDN VISIBLE NONE;\
         DISTRICT DISTRICT VISIBLE NONE;\
         BLOCK BLOCK VISIBLE NONE;MAP MAP VISIBLE NONE;\
         PARCEL PARCEL VISIBLE NONE;\
         PARCEL_MAJOR PARCEL_MAJOR VISIBLE NONE;\
         PARCEL_MINOR PARCEL_MINOR VISIBLE NONE;\
         LEASEHD LEASEHD VISIBLE NONE;\
         PIDN_LEASE PIDN_LEASE VISIBLE NONE;\
         CARD_NO CARD_NO VISIBLE NONE;\
         MASTER MASTER VISIBLE NONE;\
         DEED_BK DEED_BK VISIBLE NONE;\
         DEED_PG DEED_PG VISIBLE NONE;\
         SITE_ST_NO SITE_ST_NO VISIBLE NONE;\
         SITE_ST_DIR SITE_ST_DIR VISIBLE NONE;\
         SITE_ST_NAME SITE_ST_NAME VISIBLE NONE;\
         SITE_ST_SUF SITE_ST_SUF VISIBLE NONE;\
         PROPADR PROPADR VISIBLE NONE;\
         OWNER_FULL OWNER_FULL VISIBLE NONE;\
         OWN_NAME1 OWN_NAME1 VISIBLE NONE;\
         OWN_NAME2 OWN_NAME2 VISIBLE NONE;\
         MAIL_ADDR_FULL MAIL_ADDR_FULL VISIBLE NONE;\
         MAIL_ADDR1 MAIL_ADDR1 VISIBLE NONE;\
         MAIL_ADDR2 MAIL_ADDR2 VISIBLE NONE;\
         MAIL_ADDR3 MAIL_ADDR3 VISIBLE NONE;\
         PREV_OWNER PREV_OWNER VISIBLE NONE;\
         CLASS CLASS VISIBLE NONE;\
         LUC LUC VISIBLE NONE;\
         ACRES ACRES VISIBLE NONE;\
         STYLE STYLE VISIBLE NONE;\
         NUM_STORIE NUM_STORIE VISIBLE NONE;\
         RES_LIVING_AREA RES_LIVING_AREA VISIBLE NONE;\
         YRBLT YRBLT VISIBLE NONE;\
         CLEAN_GREEN CLEAN_GREEN VISIBLE NONE;\
         HEATSYS HEATSYS VISIBLE NONE;\
         FUEL FUEL VISIBLE NONE;\
         UTILITY UTILITY VISIBLE NONE;\
         APRLAND APRLAND VISIBLE NONE;\
         APRBLDG APRBLDG VISIBLE NONE;\
         APRTOTAL APRTOTAL VISIBLE NONE;\
         SALEDT SALEDT VISIBLE NONE;\
         PRICE PRICE VISIBLE NONE;\
         PREV_PRICE PREV_PRICE VISIBLE NONE;\
         SCHOOL_DIS SCHOOL_DIS VISIBLE NONE;\
         COMM_STRUC COMM_STRUC VISIBLE NONE;\
         COMM_YEAR_BUILT COMM_YEAR_BUILT VISIBLE NONE;\
         COMM_BUILDING_SQ_FT COMM_BUILDING_SQ_FT VISIBLE NONE;\
         GRADE GRADE VISIBLE NONE;\
         CDU CDU VISIBLE NONE;\
         GlobalID GlobalID VISIBLE NONE;\
         HYPERLINK HYPERLINK VISIBLE NONE")

        # Process: Add Join
        arcpy.AddJoin_management(GIS_Land_Base_CAMA_View, "PIDN", Parcels, "PIDN", "KEEP_COMMON")

        # Process: Table Select
        arcpy.TableSelect_analysis(GIS_Land_Base_CAMA_View, CAMA_Records, "")

        # Process: Create Relationship Class
        arcpy.CreateRelationshipClass_management(CAMA_Records, Parcels, CAMA_Records_Parcels, "SIMPLE", "Parcels", "CAMA_Records", "BOTH", "ONE_TO_ONE", "NONE", "OBJECTID", "OBJECTID", "", "")

        #Process: Remove Join
        arcpy.RemoveJoin_management(GIS_Land_Base_CAMA_View)

    else:
        arcpy.AddMessage("The check box was not selected to include CAMA and Relationship Class added to Extracted Data\n")

    if arcpy.Exists(os.path.join(outfolder, "Contours_2FT")):
        arcpy.AddMessage ("Selecting 10FT Contours and Creating {}\n".format(os.path.join(outfolder, "Contours_10FT")))
        arcpy.MakeFeatureLayer_management(os.path.join(outfolder, "Contours_2FT"),GIS_Land_Base_CAMA_View,"CONT_TYPE = 'INDEX DEPRESSION' OR CONT_TYPE = 'INDEX CONTOUR'")
        arcpy.Select_analysis(GIS_Land_Base_CAMA_View,os.path.join(outfolder, "Contours_10FT"))
        arcpy.Delete_management(GIS_Land_Base_CAMA_View)

    arcpy.AddMessage ("Copying Extract GDB from {} to Extract Folder Location Workspace at {}\n".format(outfolder,folder_name))
    #Copies GDB in Temp Location to New Folder
    shutil.copytree(outfolder,output_GDB)
    arcpy.env.workspace = outfolder
    ConvertFeatures = arcpy.ListFeatureClasses()
    arcpy.AddMessage ("Starting Converting to Shapefile....")
    for FC in ConvertFeatures:
        arcpy.AddMessage ("Converting {} Feature Class to Shapefile....\n".format(FC))
        arcpy.FeatureClassToShapefile_conversion(FC,folder_name)
    arcpy.AddMessage ("Zipping File GDB from {} and creating zip file:\n {}\n ".format(output_GDB,output_zip))
    # Step to zip GDB in New Folder Location
    dir_zip(output_GDB, output_zip, True)

arcpy.AddMessage ("""


                                        <xeee..
                                      ueeeeeu..^"*$e.
                               ur d$$$$$$$$$$$$$$Nu "*Nu
                             d$$$ "$$$$$$$$$$$$$$$$$$e."$c
                         u$$c   ""   ^"^**$$$$$$$$$$$$$b.^R:
                       z$$#""           `??$$$$$$$$$$$$$N.^
                     .$P                   ~!R$$$$$$$$$$$$$b
                    x$F                 **$b. '"R).$$$$$$$$$$
                   J^"                           #$$$$$$$$$$$$.
                  z$e                      ..      "**$$$$$$$$$
                 :$P           .        .$$$$$b.    ..  "  #$$$$
                 $$            L          ^*$$$$b   "      4$$$$L
                4$$            ^u    .e$$$$e."*$$$N.       @$$$$$
                $$E            d$$$$$$$$$$$$$$L "$$$$$  mu $$$$$$F
                $$&            $$$$$$$$$$$$$$$$N   "#* * ?$$$$$$$N
                $$F            '$$$$$$$$$$$$$$$$$bec...z$ $$$$$$$$
               '$$F             `$$$$$$$$$$$$$$$$$$$$$$$$ '$$$$E"$
                $$                  ^""""""`       ^"*$$$& 9$$$$N
                k  u$                                  "$$. "$$P r
                4$$$$L                                   "$. eeeR
                 $$$$$k                                   '$e. .@
                 3$$$$$b                                   '$$$$
                  $$$$$$                                    3$$"
                   $$$$$  dc                                4$F
                    RF** <$$                                J"
                     #bue$$$LJ$$$Nc.                        "
                      ^$$$$$$$$$$$$$r
                        `"*$$$$$$$$$
                $. .$ $~$ $~$ ~$~  $  $    $$$ $~$ $. .$ $~$  $  ~$~
                $$ $$ $ $ $ $  $  $.$ $    $   $ $ $$ $$ $.$ $.$  $
                $`$'$ $ $ $~k  $  $~$ $    $   $ $ $`$'$ $ $ $~$  $
                $ $ $ $o$ $ $  $  $ $ $oo  $$$ $o$ $ $ $ $o$ $ $  $

                """)
arcpy.AddMessage("York County Data Extractor Script Complete\n")