# rdd_like_filr_organizer
This program supports merging html/md file in a single html file, with support for math function in md. 
All style section of each html file would be stripped, ideally only pass in the body secction. 
main.html is reset after each operation in the GUI, so makesure to save the desired main.html before each modification. 

instruction:
1. install all packages in requirement
2. run organizer.py
3. press button to add/remove file, press and drag items to change the order of files, press updaet to update the changes in files to main file
4. press save and close the window. The merged file is in main.html
   
instruction on adding breakpoint(child_item in menu):
copy and paste the followin into the html or md file thaat you want to add:
<!-- BREAKPOINT: ChildItemName -->
currently it only supports 2 level of child items, which can be found in breakpoint.txt

Included are 3 files for testing, try adding them into the main.html. 


