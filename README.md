York County Data Extractor Script (CD#1 and/or CD#2 Data)

Extracts York County Data to either a file geodatabase and/or shapefile, then creates a folder under the following directory:

O:\IS\DataRequests\Extractor

STEP #1- Choose Data Output Type (By Default Set to File Geodatabase)

- File Geodatabase

- Shapefile

- Both (File Geodatabase and Shapefile)

STEP #2- Set Input Feature to Clip

STEP #3- Select by Attribute from Input Feature (Step#2)

- Create a SQL statement on Input Feature

STEP #4- Select Buffer Distance

-Choose a Buffer Distance. This will be used to clip out the Features Participating in Step 5

STEP #5: Choose Features you want to Participate in the Extraction Process Features to Extract

STEP #6: Name Folder

- This Folder Name will be created under O:\IS\DataRequest\Extractor

STEP #7: Name Outgoing GDB File

-This will be the name of the file geodatabase once Extractor Script is completed. Rename default name if wanted. This step is only important if choosing the file geodatabse or both options in Step 1

STEP #8:(optional) GDB Version

- If extracting to a file geodatabase, you can choose which file geodatabase version you want to export. You can choose from Current, 10.0, 9.3 or 9.2 

Step #9(optional) Check Box to Add CAMA Data

- Only an option if using File Geodatabase or Both Options under Step #1
