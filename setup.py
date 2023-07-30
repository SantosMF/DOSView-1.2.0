#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
path = os.path.dirname(os.path.realpath(__file__))
os.system("sudo apt install python3-pip -y")
os.system("sudo apt install qt6-base-dev -y")
os.system("python3 -m pip install numpy")
os.system("python3 -m pip install pyqt6")
os.system("python3 -m pip install matplotlib")
os.system("chmod u+x edosv.py")

texto = f"""[Desktop Entry]
Name=EDOSView
Exec=bash -c "$(dirname $(realpath $(echo %k | sed -e 's/^file:\/\///')))/main.py -url %U"
Icon={path}/temps/icon1.png
Type=Application
Terminal=false
Categories=Science;Chemistry;Physics;Education;
MimeType=outhers
X-GNOME-SingleWindow=true
Name[pt_BR]=edosv
"""
with open (path+"/edosv.desktop", 'w') as saida:
    saida.write(texto)
print(" rm  ~/.local/share/applications/edosv.desktop")
os.system(" rm  ~/.local/share/applications/edosv.desktop")
print(f"ln -s {path}/edosv.desktop  ~/.local/share/applications/edosv.desktop")
os.system(f"ln -s {path}/edosv.desktop  ~/.local/share/applications/edosv.desktop")
print("done")

