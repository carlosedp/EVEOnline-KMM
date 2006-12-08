@echo off

rem *** Used to create a Python exe  
 
echo ***** get rid of all the old files in the build folder 
rd /S /Q build 
rd /S /Q dist

 
echo ***** Creating the exe 
 
python genfiles.py
python setup.py py2exe

echo **** pause so we can see the exit codes 
pause "done...hit a key to exit" 