#pylint: disable=too-many-statements
#pylint: disable=too-many-branches
'''
Gscreenshot's CLI
'''
import argparse
import locale
import sys
import gettext
from pkg_resources import resource_filename

from gscreenshot import Gscreenshot
from gscreenshot.screenshooter.exceptions import NoSupportedScreenshooterError

_ = gettext.gettext


def run():

    locale_path = resource_filename('gscreenshot.resources', 'locale')
    locale.setlocale(locale.LC_ALL, '')
    locale.bindtextdomain('gscreenshot', locale_path)
    gettext.bindtextdomain('gscreenshot', locale_path)
    gettext.textdomain('gscreenshot')


    '''Run the CLI frontend'''
    parser = argparse.ArgumentParser()

    #pylint: disable=line-too-long
    parser.add_argument(
            '-d',
            '--delay',
            required=False,
            default=0,
            help=_("How many seconds to wait before taking the screenshot. Defaults to 0.")
            )
    parser.add_argument(
            '-f',
            '--filename',
            required=False,
            default=False,
            help=_("Where to store the screenshot file. Defaults to gscreenshot_<time>.png. This can be paired with -c to save and copy. If you specify a filename without a file extension, it will be treated as a directory (creating the tree if needed) and screenshots will be saved there with the default filename scheme.")
            )
    parser.add_argument(
            '-c',
            '--clip',
            required=False,
            action='store_true',
            help=_("Copy the image to the clipboard. Requires xclip to be installed. This can be paired with -f to save and copy together.")
            )
    parser.add_argument(
            '-o',
            '--open',
            required=False,
            action='store_true',
            help=_("Open the screenshot in your default viewer.")
            )
    parser.add_argument(
            '-s',
            '--selection',
            required=False,
            action='store_true',
            help=_("Choose a window or select a region to screenshot.")
            )
    parser.add_argument(
            '-V',
            '--version',
            required=False,
            action='store_true',
            help=_("Show information about gscreenshot")
            )
    parser.add_argument(
            '-n',
            '--notify',
            required=False,
            action='store_true',
            help=_("Show a notification when the screenshot is taken. Gscreenshot will automatically show a notification if a screenshot is taken from a different session, so some situations may not need this option.")
    )

    args = parser.parse_args()

    #pylint: enable=line-too-long

    try:
        gscreenshot = Gscreenshot()
    except NoSupportedScreenshooterError:
        print(_("No supported screenshot backend is available."))
        print(_("Please install one to use gscreenshot."))
        sys.exit(1)

    if args.version is not False:
        authors = gscreenshot.get_program_authors()
        website = gscreenshot.get_program_website()
        description = gscreenshot.get_program_description()
        license_name = gscreenshot.get_program_license()
        name = gscreenshot.get_program_name()
        version = gscreenshot.get_program_version()

        print(_("Using {0} screenshot backend").format(gscreenshot.get_screenshooter_name()))
        print("{0} {1}; {2}".format(name, version, _(description)))
        print(website)
        print("")
        print(_("Author(s)"))
        print("\n".join(authors))
        print("")
        print(_("Licensed as {0}").format(license_name))
        sys.exit(0)

    if args.selection is not False:
        gscreenshot.screenshot_selected(args.delay)
    else:
        gscreenshot.screenshot_full_display(args.delay)

    if gscreenshot.get_last_image() is None:
        print(_("No screenshot taken."))
        sys.exit(1)
    else:
        if args.notify:
            gscreenshot.show_screenshot_notification()
        shot_saved = False
        should_save_shot = (args.filename is not False or args.clip is False)
        exit_code = 0

        if args.filename is not False:
            shot_saved = gscreenshot.save_last_image(args.filename)
        elif args.clip is False:
            shot_saved = gscreenshot.save_last_image()

        if should_save_shot and not shot_saved:
            exit_code = 1
            print(_("Failed to save screenshot!"))

        if args.open is not False:
            gscreenshot.open_last_screenshot()

        if args.clip is not False:
            successful_clip = gscreenshot.copy_last_screenshot_to_clipboard()

            if not successful_clip:
                tmp_file = gscreenshot.save_and_return_path()
                print(_("Could not clip image! Xclip failed to run."))
                print(_("Your screenshot was saved to " + tmp_file))
                exit_code = 1
        sys.exit(exit_code)
