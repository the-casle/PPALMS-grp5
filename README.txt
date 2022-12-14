-- PPALMS version 0.1 --
-- CSCI 5801 --
Jake Kaslewicz, Harrison Rowe, Muja Jama, Tyler Rife

*WARNING: THERE MAY BE BUGS WHEN RUNNING ON THE VIRTUAL ONLINE LINUX ENVIRONMENT (VOLE)*
*THIS IS UNLIKELY BUT BE COGNIZANT*

HOW TO USE
1. To run, use the terminal to navigate to the program folder.
   Then, enter "python3 main.py". The program should start.
   (If there is an error related to importing wx, enter
   "pip install -U wxPython" and try running again. If there is still an error related to
   EnableCheckBoxes(), enter "pip install --upgrade --force-reinstall wxPython" and try again.)
2. Select a desired file for annotation and question generation by clicking
   the "Select Source File" button.
3. Click "Open" in the file explorer after highlighting your desired file.
   You should see the name of your selected source file displayed. Click "Next".
4. You will see all the lines of your file displayed. Select individual lines
   for inclusion or exclusion using the "Switch to Inclusion/Exclusion" button.
5. After annotating, select "Next". Now, you can create groups by selecting "Add Group".
   You can add lines by selcting the group from the menu and then selecting the desired
   lines.
6. Click "Next". You can now flag groups based on question type. Once done, click "Finish".
