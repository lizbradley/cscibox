These files are used to create a .app file from the latest github release of Calvin. It can be run anywhere on the computer, and it should still work. The .sh files are designed for running on the virtual machines we use for building the releases; the rest of this document will explain how to get the script working on a new computer. For information on how the scripts work, read through them, as they are heavily commented.

The only difference between these files are the filepaths; to get it to run on a new computer, simply duplicate make_dmg_10_9.sh and make the following changes:

* replace "/Users/cscience/Projects/Calvin" with the full path to the folder that houses the repository on your computer.

* replace "/Users/cscience/Projects/DMG_Creation" with the full path to the folder you want the DMG to appear in.

After using this script, the DMG must be formatted (by opening it, changing the size of it, positioning the icons correctly, etc.) and then the script that makes the DMG read only must be run.