'''
Interface class for integrating a screenshot utility
'''
import os
import subprocess
import tempfile
import PIL.Image

from pkg_resources import resource_filename
from gscreenshot.selector import SelectionExecError, SelectionParseError
from gscreenshot.selector import SelectionCancelled, NoSupportedSelectorError
from gscreenshot.selector.factory import SelectorFactory

try:
    from Xlib import display
    XLIB_AVAILABLE = True
except ImportError:
    XLIB_AVAILABLE = False


class Screenshooter(object):
    """
    Python interface for a screenshooter
    """

    __slots__ = ('_image', 'tempfile', 'selector')

    def __init__(self):
        """
        constructor
        """
        try:
            self.selector = SelectorFactory().create()
        except NoSupportedSelectorError:
            self.selector = None

        self._image = None
        self.tempfile = os.path.join(
                tempfile.gettempdir(),
                str(os.getpid()) + ".png"
                )

    @property
    def image(self):
        """
        Returns the last screenshot taken

        Returns:
            PIL.Image or None
        """
        return self._image

    def _grab_fullscreen(self, delay=0, capture_cursor=False, use_cursor=None):
        '''
        Internal API method for grabbing the full screen
        '''
        if use_cursor is None:
            self.grab_fullscreen(delay, capture_cursor)
        else:
            self.grab_fullscreen(delay, capture_cursor=False)
            self.add_fake_cursor(use_cursor)

    def grab_fullscreen(self, delay=0, capture_cursor=False):
        """
        Takes a screenshot of the full screen with a given delay

        Parameters:
            int delay, in seconds
        """
        raise Exception("Not implemented. Fullscreen grab called with delay " + str(delay))

    def _grab_selection(self, delay=0, capture_cursor=False, use_cursor=None):
        '''
        Internal API method for grabbing a selection
        '''
        if use_cursor is None:
            self.grab_selection(delay, capture_cursor)
        else:
            self.grab_selection(delay, capture_cursor=False)
            self.add_fake_cursor(use_cursor)

    def grab_selection(self, delay=0, capture_cursor=False):
        """
        Takes an interactive screenshot of a selected area with a
        given delay. This has some safety around the interactive selection:
        if it fails to run, it will call a fallback method (which defaults to
        taking a full screen screenshot). if it gives unexpected output it will
        fall back to a full screen screenshot.

        Parameters:
            int delay: seconds
        """
        if self.selector is None:
            self._grab_selection_fallback(delay, capture_cursor)
            return

        try:
            crop_box = self.selector.region_select()
        except SelectionCancelled:
            print("Selection was cancelled")
            return
        except (OSError, SelectionExecError):
            print("Failed to call region selector -- Using fallback region selection")
            self._grab_selection_fallback(delay, capture_cursor)
            return
        except SelectionParseError:
            print("Invalid selection data -- falling back to full screen")
            self.grab_fullscreen(delay, capture_cursor)
            return

        self.grab_fullscreen(delay, capture_cursor)

        if self._image is not None:
            self._image = self._image.crop(crop_box)

    def _grab_window(self, delay=0, capture_cursor=False, use_cursor=None):
        '''
        Internal API method for grabbing a window
        '''
        if use_cursor is None:
            self.grab_window(delay, capture_cursor)
        else:
            self.grab_window(delay, capture_cursor=False)
            self.add_fake_cursor(use_cursor)

    def grab_window(self, delay=0, capture_cursor=False):
        """
        Takes an interactive screenshot of a selected window with a
        given delay

        Parameters:
            int delay: seconds
        """
        self.grab_selection(delay, capture_cursor)

    @staticmethod
    def can_run():
        """
        Whether this utility can run
        """
        return False

    def get_cursor_position(self):
        """
        Gets the current position of the mouse cursor, if able.
        Returns (x, y) or None.
        """
        if not XLIB_AVAILABLE:
            return None

        try:
            # This is a ctype
            # pylint: disable=protected-access
            mouse_data = display.Display().screen().root.query_pointer()._data
        # pylint: disable=bare-except
        except:
            # We don't really care about the specific error here. If we can't
            # get the pointer, then just move on.
            return None

        return (mouse_data["root_x"], mouse_data["root_y"])

    def add_fake_cursor(self, cursor_img=None):
        """
        Stamps a fake cursor onto the screenshot.
        This is intended for use with screenshot backends that don't
        capture the cursor (or don't capture the cursor in some scenarios)
        """
        if self._image is None:
            return

        cursor_pos = self.get_cursor_position()
        if cursor_pos is None:
            print("Unable to get cursor position - is xlib available?")
            return

        fname = resource_filename(
                  'gscreenshot.resources.pixmaps', 'cursor-adwaita.png'
                )

        if cursor_img is None:
            cursor_img = PIL.Image.open(fname)

        screenshot_img = self._image.copy()

        screenshot_width, screenshot_height = screenshot_img.size

        # scale the cursor stamp to a reasonable size
        cursor_size_ratio = min(max(screenshot_width / 2000, .3), max(screenshot_height / 2000, .3))
        cursor_height = cursor_img.size[0] * cursor_size_ratio
        cursor_width = cursor_img.size[1] * cursor_size_ratio
        cursor_img.thumbnail((cursor_width, cursor_height))

        # Passing cursor_img twice is intentional. The second time it's used
        # as a mask (PIL uses the alpha channel) so the cursor doesn't have
        # a black box.
        screenshot_img.paste(cursor_img, cursor_pos, cursor_img)
        self._image = screenshot_img

    def _grab_selection_fallback(self, delay=0, capture_cursor=False):
        """
        Fallback for grabbing the selection, in case the selection tool fails to
        run entirely. Defaults to giving up and just taking a full screen shot.

        Parameters:
            int delay: seconds
        """
        self.grab_fullscreen(delay, capture_cursor)

    def _call_screenshooter(self, screenshooter, params = None):

        # This is safer than defaulting to []
        if params is None:
            params = []

        params = [screenshooter] + params
        try:
            subprocess.check_output(params)
            self._image = PIL.Image.open(self.tempfile)
            os.unlink(self.tempfile)
        except (subprocess.CalledProcessError, IOError, OSError):
            self._image = None
            return False

        return True
