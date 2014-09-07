#!/bin/bash
pyinstaller --windowed --noconfirm --onefile --clean cscience.py --hidden-import=scipy.special._ufuncs_cxx

echo "Deleting build folder..."
rm -rf build
echo "Installer successfully generated!"
