# gscreenshot

[![Code Climate](https://codeclimate.com/github/thenaterhood/gscreenshot/badges/gpa.svg)](https://codeclimate.com/github/thenaterhood/gscreenshot)


gscreenshot is a gtk frontend for scrot, an application for taking screenshots,
written in python and pygtk. This is a fork of the original project (last
updated in 2006) that updates it to use modern technologies and to provide
updated functionality.

This application was originally written by matej.horvath. The original project
can be found at https://code.google.com/p/gscreenshot/ while Google Code is
still up and running.

gscreenshot is licensed under the GPLv2.

## Installation

ArchLinux and derivatives:
[Available in the AUR](https://aur.archlinux.org/packages/gscreenshot/)

Fedora/Mageia/OpenSUSE:
[Available in COPR](https://copr.fedorainfracloud.org/coprs/thenaterhood/gscreenshot/)

SparkyLinux:
Available in your distro's repositories. Run `sudo apt-get install gscreenshot`

Manual installation:

1. Download the latest version from [here](https://github.com/thenaterhood/gscreenshot/releases/latest)
2. Unzip or untar the file (depending which you downloaded)
3. From the command line, navigate to the unzipped files and run
   - `sudo python setup.py install --single-version-externally-managed` (may fail on some Python versions)
   - OR `sudo python setup.py install --old-and-unmanageable`
   - OR you can also install with `sudo pip install -e .` but this won't install pixmaps or menu entries

Building a package:

Generally, running one of the setup.py calls above with the --root parameter
should work fine for building a packageable version.

gscreenshot automatically retrieves its version number from specs/gscreenshot.spec
and setup.py should generate appropriate menu entries and binaries.

## Usage
gscreenshot takes screenshots! Run it manually or bind it to a keystroke.
Both a graphical (gscreenshot) and CLI (gscreenshot-cli) interface are available.

### Command Line
Run `gscreenshot --help` for instructions. The shell interface is
non-interactive so it is suitable for use in scripts and pre-built
calls.

### Graphical

Buttons

* "Selection" allows you to drag-select an area to screenshot
* "Window" allows you to click a window to screenshot
* "Everything" takes a screenshot of the entire screen.
* "Save" brings up the file save dialog to save your screenshot

Keyboard shortcuts

* Control+S opens the save dialog
* Control+C copies the screenshot to the clipboard
* Control+O opens your screenshot in your default image application
* Escape quits the application

## Contributing
Find a problem? Have something to add? Just think gscreenshot is super
cool? gscreenshot accepts contributions!

### Localization
gscreenshot uses the standard gettext tools. Locale files can be found in
src/gscreenshot/resources/locale.

If you contribute a localization, do not add the compiled .mo files. They
are generated on demand as part of the installation.

Current supported languages are:
* English
* Español

### Contributing Code
Please base pull requests off of and open pull requests against the
'dev' branch. 'master' is reserved for stable code. You may be asked to
rebase your code against the latest version of the 'dev' branch if
there's been a flurry of activity before your contribution.

Pull requests may not be merged right away! Don't take offense,
sometimes it just takes a little while to get to them.

### Opening Issues
Don't worry about categorizing your issue properly, it'll get taken
care of on this end.

## Requirements
_automatically installed by the setup script or your package manager_

_Your preference for taking screenshots. You need at least one of these._
* Scrot
* ImageMagick
* Imlib2_grab (the library Scrot uses)

_These requirements_
* Python 2.7 or Python 3
* python-pillow
* python-gobject (may be called "python-gi" or "python3-gi")
* Setuptools

_Optional, but recommended_
* Slop (used for improved region and window selection)
  * There are some issues with the builtin selection functionality in scrot and some others
* Xclip (for command line clipboard functionality)
* xdg-open (for opening screenshots in your image viewer)

## Development Requirements
The above, plus:
* Glade

