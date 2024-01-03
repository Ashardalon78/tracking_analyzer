DESCRIPTION
------------------
This software visulizes movement data tracked by Google.
This repository contains the source code as well as a compiled executable for 64-bit Windows (by pyinstaller),
which can be found in the "dist" subfolder.



DEPENDENCIES
-------------------
When using the source code, you need the following software/libraries installed:

* Python 3.7.6 or graeter
* Numpy
* Matplotlib
* Pandas


USAGE
-------------------
* First, you have to download your Google lactaion history. You can do this from https://takeout.google.com/settings/takeout
* From the numerous download optins, the only one required is "Location History (Timeline)"
* Start the tool by executing main.py or calling the exe
*  Select "Load Location History" and selct the folder "Semantic Location History" in the dowloaded timeline (the folder should contain subfolders named as year dates) 
* Select means of transprtation in the dropdown menu on the right hand side and hit "Plot Data"