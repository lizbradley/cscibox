#!/bin/bash

#This is the script for Mac OSX 10.9, and it
#compiles the code and creates a DMG for the app.
#It's mostly the same for all versions of OSX, but 
#The paths are explicitly set up for the OSX 10.9 VM
#That we (the developers) have.

#Move to the correct directory
cd /Users/fernando/Projects/Cscience/src
#Make sure we have the most recent version
git pull
#Remove any old dist folders
rm -r /Users/fernando/Projects/Cscience/src/dist*
#Run the pyinstaller script. I didn't write this,
#and was told to ignore all errors
/Users/fernando/Projects/Cscience/src/pyinstaller_script_osx.sh
#Copy the correct icon onto the app
cp /Users/fernando/Projects/Cscience/icon.icns /Users/fernando/Projects/Cscience/src/dist/cscience.app/Contents/Resources/icon-windowed.icns


#The rest is copy and pasted, with small edits, from 
#http://asmaloney.com/2013/07/howto/packaging-a-mac-os-x-application-using-a-dmg/
#Go there for a tutorial on what it all means.

APP_NAME="CSciBox" #This is the only one that I would change
APP_EXE="${APP_NAME}.app/Contents/MacOS/${APP_NAME}"
VOL_NAME="${APP_NAME}"
DMG_TMP="${VOL_NAME}_temp.dmg"
DMG_FINAL="${VOL_NAME}.dmg"
STAGING_DIR="/Users/fernando/Projects/DMG_Creation/CSciBox"
    
rm -rf "${STAGING_DIR}" "${DMG_TMP}" "${DMG_FINAL}"

mkdir -p "${STAGING_DIR}"

mv /Users/fernando/Projects/Cscience/src/dist/cscience.app "${STAGING_DIR}"

SIZE=`du -sh "${STAGING_DIR}" | sed 's/\([0-9]*\)M\(.*\)/\1/'`
SIZE=`echo "${SIZE} + 1.0" | bc | awk '{print int($1+0.5)}'`
 
if [ $? -ne 0 ]; then
   echo "Error: Cannot compute size of staging dir"
   exit
fi
 
# create the temp DMG file
hdiutil create -srcfolder "${STAGING_DIR}" -volname "${VOL_NAME}" -fs HFS+ \
      -fsargs "-c c=64,a=16,e=16" -format UDRW -size ${SIZE}M "${DMG_TMP}"
 
echo "Created DMG: ${DMG_TMP}"
 
# mount it and save the device
DEVICE=$(hdiutil attach -readwrite -noverify "${DMG_TMP}" | \
         egrep '^/dev/' | sed 1q | awk '{print $1}')
 
sleep 2

# add a link to the Applications dir
echo "Add link to /Applications"
pushd /Volumes/"${VOL_NAME}"
ln -s /Applications
popd
 
sync

# unmount it
hdiutil detach "${DEVICE}"

# clean up
rm -rf "${DMG_TMP}"
rm -rf "${STAGING_DIR}"

rm /Users/fernando/Projects/DMG_Creation/CSciBox*

mv /Users/fernando/Projects/Cscience/src/CSciBox.dmg /Users/fernando/Projects/DMG_Creation
 
echo 'Done.'

exit

#At this point, what you have to do is edit the DMG in the finder window
#to have the right size and setup, and then run the "make DMG read only" script.
#Then zip that new DMG, and that's everything you need to know to distribute this thing.


