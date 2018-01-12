
Debian
====================
This directory contains files used to package bnetd/bnet-qt
for Debian-based Linux systems. If you compile bnetd/bnet-qt yourself, there are some useful files here.

## bnet: URI support ##


bnet-qt.desktop  (Gnome / Open Desktop)
To install:

	sudo desktop-file-install bnet-qt.desktop
	sudo update-desktop-database

If you build yourself, you will either need to modify the paths in
the .desktop file or copy or symlink your bnet-qt binary to `/usr/bin`
and the `../../share/pixmaps/bnet128.png` to `/usr/share/pixmaps`

bnet-qt.protocol (KDE)

