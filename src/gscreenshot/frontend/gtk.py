#pylint: disable=unused-argument
#pylint: disable=wrong-import-order
#pylint: disable=wrong-import-position
#pylint: disable=ungrouped-imports
'''
Classes for the GTK gscreenshot frontend
'''
import gettext
import io
import sys
import threading
from time import sleep
from pkg_resources import resource_string, resource_filename
from gi import pygtkcompat
from gscreenshot import Gscreenshot
from gscreenshot.screenshooter.exceptions import NoSupportedScreenshooterError

pygtkcompat.enable()
pygtkcompat.enable_gtk(version='3.0')
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GObject

i18n = gettext.gettext


class Presenter(object):
    '''Presenter class for the GTK frontend'''

    __slots__ = ('_delay', '_app', '_hide', '_can_resize',
            '_pixbuf', '_view', '_keymappings')

    def __init__(self, application, view):
        self._app = application
        self._view = view
        self._can_resize = True
        self._delay = 0
        self._hide = True
        self._set_image(self._app.get_last_image())
        self._show_preview()
        self._keymappings = {}

    def _begin_take_screenshot(self, app_method):
        screenshot = app_method(self._delay)

        # Re-enable UI on the UI thread.
        GObject.idle_add(self._end_take_screenshot, screenshot)

    def _end_take_screenshot(self, screenshot):
        self._set_image(screenshot)
        self._show_preview()

        self._view.unhide()

    def set_keymappings(self, keymappings):
        '''Set the keymappings'''
        self._keymappings = keymappings

    def window_state_event_handler(self, widget, event, *_):
        '''Handle window state events'''
        self._view.handle_state_event(widget, event)

    def take_screenshot(self, app_method):
        '''Take a screenshot using the passed app method'''
        if self._hide:
            self._view.hide()

        # Do work in background thread.
        # Taken from here: https://wiki.gnome.org/Projects/PyGObject/Threading
        _thread = threading.Thread(target=self._begin_take_screenshot(app_method))
        _thread.daemon = True
        _thread.start()

    def handle_keypress(self, widget, event, *args):
        """
        This method handles individual keypresses. These are
        handled separately from accelerators (which include
        modifiers).
        """
        if event.keyval in self._keymappings:
            self._keymappings[event.keyval]()

    def hide_window_toggled(self, widget):
        '''Toggle the window to hidden'''
        self._hide = widget.get_active()

    def delay_value_changed(self, widget):
        '''Handle a change with the screenshot delay input'''
        self._delay = widget.get_value()

    def on_button_all_clicked(self, *_):
        '''Take a screenshot of the full screen'''
        self.take_screenshot(
            self._app.screenshot_full_display
            )

    def on_button_window_clicked(self, *args):
        '''Take a screenshot of a window'''
        self._button_select_area_or_window_clicked(args)

    def on_button_selectarea_clicked(self, *args):
        '''Take a screenshot of an area'''
        self._button_select_area_or_window_clicked(args)

    def _button_select_area_or_window_clicked(self, *_):

        self.take_screenshot(
            self._app.screenshot_selected
            )

    def on_button_saveas_clicked(self, *_):
        '''Handle the saveas button'''
        saved = False
        cancelled = False
        save_dialog = FileSaveDialog(
                self._app.get_time_filename(),
                self._app.get_last_save_directory(),
                self._view.get_window()
                )

        while not (saved or cancelled):
            fname = self._view.run_dialog(save_dialog)
            if fname is not None:
                saved = self._app.save_last_image(fname)
            else:
                cancelled = True

    def on_button_openwith_clicked(self, *_):
        '''Handle the "open with" button'''
        fname = self._app.save_and_return_path()
        appchooser = OpenWithDialog()

        self._view.run_dialog(appchooser)

        appinfo = appchooser.appinfo

        if appinfo is not None:
            if appinfo.launch_uris(["file://"+fname], None):
                self.quit(None)

    def on_button_copy_clicked(self, *_):
        """
        Copy the current screenshot to the clipboard
        """
        img = self._app.get_last_image()
        pixbuf = self._image_to_pixbuf(img)

        if not self._view.copy_to_clipboard(pixbuf):
            if not self._app.copy_last_screenshot_to_clipboard():
                warning_dialog = WarningDialog(
                    i18n("Your clipboard doesn't support persistence and xclip isn't available."),
                    self._view.get_window())
                self._view.run_dialog(warning_dialog)

    def on_button_open_clicked(self, *_):
        '''Handle the open button'''
        success = self._app.open_last_screenshot()
        if success:
            dialog = WarningDialog(
                i18n("Please install xdg-open to open files."),
                self._view.get_window())
            self._view.run_dialog(dialog)
        else:
            self.quit(None)

    def on_button_about_clicked(self, *_):
        '''Handle the about button'''
        about = Gtk.AboutDialog(transient_for=self._view.get_window())

        authors = self._app.get_program_authors()
        about.set_authors(authors)

        description = i18n(self._app.get_program_description())
        description += "\n" + i18n("Using {0} screenshot backend").format(
            self._app.get_screenshooter_name()
        )
        about.set_comments(i18n(description))

        website = self._app.get_program_website()
        about.set_website(website)
        about.set_website_label(website)

        name = self._app.get_program_name()
        about.set_program_name(name)
        about.set_title(i18n("About"))

        license_text = self._app.get_program_license_text()
        about.set_license(license_text)

        version = self._app.get_program_version()
        about.set_version(version)

        about.set_logo(
                Gtk.gdk.pixbuf_new_from_file(
                    resource_filename(
                        'gscreenshot.resources.pixmaps', 'gscreenshot.png'
                        )
                    )
                )

        self._view.run_dialog(about)

    def on_fullscreen_toggle(self):
        '''Handle the window getting toggled to fullscreen'''
        self._view.toggle_fullscreen()

    def on_button_quit_clicked(self, widget=None):
        '''Handle the quit button'''
        self.quit(widget)

    def on_window_main_destroy(self, widget=None):
        '''Handle the titlebar close button'''
        self.quit(widget)

    def on_window_resize(self, *_):
        '''Handle window resizes'''
        if self._can_resize:
            self._view.resize()
            self._show_preview()

    def quit(self, *_):
        '''Exit the app'''
        self._app.quit()

    def _image_to_pixbuf(self, image):
        descriptor = io.BytesIO()
        image = image.convert("RGB")
        image.save(descriptor, "ppm")
        contents = descriptor.getvalue()
        descriptor.close()
        loader = Gtk.gdk.PixbufLoader("pnm")
        loader.write(contents)
        pixbuf = loader.get_pixbuf()
        loader.close()
        return pixbuf

    def _set_image(self, image):
        # create an image buffer (pixbuf) and insert the grabbed image
        if image is None:
            image = self._app.get_app_icon()
        self._pixbuf = self._image_to_pixbuf(image)

    def _show_preview(self):
        height, width = self._view.get_preview_dimensions()

        preview_img = self._app.get_thumbnail(width, height)

        self._view.update_preview(self._image_to_pixbuf(preview_img))


class View(object):
    '''View class for the GTK frontend'''

    def __init__(self, window, builder):
        self._window = window
        self._window_is_fullscreen = False
        self._was_maximized = False
        self._last_window_dimensions = self._window.get_size()
        self._header_bar = builder.get_object('header_bar')
        self._preview = builder.get_object('image1')
        self._control_grid = builder.get_object('control_box')

    def run(self):
        '''Run the view'''
        self._window.set_position(Gtk.WIN_POS_CENTER)
        # Set the initial size of the window
        active_window = Gdk.get_default_root_window().get_screen().get_active_window()
        while active_window is None:
            # There appears to be a race condition with getting the active window,
            # so we'll keep trying until we have it
            active_window = Gdk.get_default_root_window().get_screen().get_active_window()

        initial_screen = self._window.get_screen().get_monitor_at_window(active_window)
        geometry = self._window.get_screen().get_monitor_geometry(initial_screen)

        if self._header_bar is not None:
            height_x = .6
        else:
            height_x = .48

        gscreenshot_height = geometry.height * height_x
        gscreenshot_width = gscreenshot_height * .9

        if geometry.height > geometry.width:
            gscreenshot_width = geometry.width * height_x
            gscreenshot_height = gscreenshot_width * .9

        self._window.set_size_request(gscreenshot_width, gscreenshot_height)

        self._window.show_all()

    def get_window(self):
        '''Returns the associated window'''
        return self._window

    def toggle_fullscreen(self):
        '''Toggle the window to full screen'''
        if self._window_is_fullscreen:
            self._window.unfullscreen()
        else:
            self._window.fullscreen()

        self._window_is_fullscreen = not self._window_is_fullscreen

    def handle_state_event(self, widget, event):
        '''Handles a window state event'''
        widget = None
        self._was_maximized = bool(event.new_window_state & Gtk.gdk.WINDOW_STATE_MAXIMIZED)
        self._window_is_fullscreen = bool(
                            Gtk.gdk.WINDOW_STATE_FULLSCREEN & event.new_window_state)

    def hide(self):
        '''Hide the view'''
        self._window.set_geometry_hints(None, min_width=-1, min_height=-1)
        # We set the opacity to 0 because hiding the window is
        # subject to window closing effects, which can take long
        # enough that the window will still appear in the screenshot
        self._window.set_opacity(0)

        # This extra step allows the window to be unmaximized after it
        # reappears. Otherwise, the hide() call clears the previous
        # state and the window is stuck maximized. We restore the
        # maximization when we unhide the window.
        if self._was_maximized:
            self._window.unmaximize()

        self._window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        sleep(0.2)

    def unhide(self):
        '''Unhide the view'''
        self._window.set_sensitive(True)
        self._window.set_opacity(1)

        original_window_size = self._window.get_size()
        self._window.set_geometry_hints(
            None,
            min_width=original_window_size.width,
            min_height=original_window_size.height
        )

        if self._was_maximized:
            self._window.maximize()

        self._window.show_all()

    def resize(self):
        '''Resize the display'''
        current_window_size = self._window.get_size()
        if self._last_window_dimensions is None:
            self._last_window_dimensions = current_window_size

        if (self._last_window_dimensions.width != current_window_size.width
                or self._last_window_dimensions.height != current_window_size.height):

            self._last_window_dimensions = current_window_size

    def get_preview_dimensions(self):
        '''Get the current dimensions of the preview widget'''
        window_size = self._window.get_size()
        control_size = self._control_grid.get_allocation()

        header_height = 0
        if self._header_bar is not None:
            header_height = self._header_bar.get_allocation().height

        width_x = .8 if self._header_bar is not None else .98

        preview_size = (
            (window_size.height-control_size.height-(.6*header_height))*.98,
            window_size.width*width_x
        )

        height = preview_size[0]
        width = preview_size[1]

        return height, width

    def update_preview(self, pixbuf):
        '''
        Update the preview widget with a new image.

        This assumes the pixbuf has already been resized appropriately.
        '''
        # view the previewPixbuf in the image_preview widget
        self._preview.set_from_pixbuf(pixbuf)

    def copy_to_clipboard(self, pixbuf):
        """
        Copy the provided image to the screen's clipboard,
        if it supports persistence
        """
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        display = Gdk.Display.get_default()

        if display.supports_clipboard_persistence():
            clipboard.set_image(pixbuf)
            clipboard.store()
            return True

        return False

    def run_dialog(self, dialog):
        '''Run a dialog window and return the outcome'''
        self._window.set_sensitive(False)
        result = dialog.run()
        self._window.set_sensitive(True)

        try:
            dialog.destroy()
        except AttributeError:
            # This process is wonky, and due to incorrect polymorphism
            pass

        return result


class OpenWithDialog(Gtk.AppChooserDialog):
    '''The "Open With" dialog'''

    def __init__(self, parent=None):

        Gtk.AppChooserDialog.__init__(self, content_type="image/png", parent=parent)
        self.set_title(i18n("Choose an Application"))
        self.connect("response", self._on_response)
        self.appinfo = None

    def _on_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            self.appinfo = self.get_app_info()
        else:
            self.appinfo = None


class FileSaveDialog(object):
    '''The 'save as' dialog'''
    def __init__(self, default_filename=None, default_folder=None, parent=None):
        self.default_filename = default_filename
        self.default_folder = default_folder
        self.parent = parent

    def run(self):
        ''' Run the dialog'''
        filename = self.request_file()

        return filename

    def request_file(self):
        '''Run the file selection dialog'''
        chooser = Gtk.FileChooserDialog(
                transient_for=self.parent,
                title=None,
                action=Gtk.FILE_CHOOSER_ACTION_SAVE,
                buttons=(
                    Gtk.STOCK_CANCEL,
                    Gtk.RESPONSE_CANCEL,
                    Gtk.STOCK_SAVE,
                    Gtk.RESPONSE_OK
                    )
                )

        if self.default_filename is not None:
            chooser.set_current_name(self.default_filename)

        if self.default_folder is not None:
            chooser.set_current_folder(self.default_folder)

        chooser.set_do_overwrite_confirmation(True)

        response = chooser.run()

        if response == Gtk.RESPONSE_OK:
            return_value = chooser.get_filename()
        else:
            return_value = None

        chooser.destroy()
        return return_value


class WarningDialog():
    '''A warning dialog'''

    def __init__(self, message, parent=None):
        self.parent = parent
        self.message_dialog = Gtk.MessageDialog(
                parent,
                None,
                Gtk.MESSAGE_WARNING,
                Gtk.BUTTONS_OK,
                message
                )

    def run(self):
        '''Run the warning dialog'''
        if self.parent is not None:
            self.parent.set_sensitive(False)

        self.message_dialog.run()
        self.message_dialog.destroy()

        if self.parent is not None:
            self.parent.set_sensitive(True)


def main():
    '''The main function for the GTK frontend'''

    try:
        application = Gscreenshot()
    except NoSupportedScreenshooterError:
        warning = WarningDialog(
            i18n("No supported screenshot backend is available."),
            None
            )
        warning.run()
        sys.exit(1)

    # Improves startup performance by kicking off a screenshot
    # as early as we can in the background.
    screenshot_thread = threading.Thread(
        target=application.screenshot_full_display
    )
    screenshot_thread.daemon = True
    screenshot_thread.start()

    builder = Gtk.Builder()
    builder.set_translation_domain('gscreenshot')
    builder.add_from_string(resource_string(
        'gscreenshot.resources.gui.glade', 'main.glade').decode('UTF-8'))

    window = builder.get_object('window_main')

    waited = 0
    while application.get_last_image() is None and waited < 4:
        sleep(.01)
        waited += .01

    view = View(builder.get_object('window_main'), builder)

    presenter = Presenter(
            application,
            view
            )

    accel = Gtk.AccelGroup()
    accel.connect(Gdk.keyval_from_name('S'), Gdk.ModifierType.CONTROL_MASK,
            0, presenter.on_button_saveas_clicked)
    accel.connect(Gdk.keyval_from_name('C'), Gdk.ModifierType.CONTROL_MASK,
            0, presenter.on_button_copy_clicked)
    accel.connect(Gdk.keyval_from_name('O'), Gdk.ModifierType.CONTROL_MASK,
            0, presenter.on_button_open_clicked)
    window.add_accel_group(accel)

    window.connect("key-press-event", presenter.handle_keypress)

    keymappings = {
        Gtk.gdk.keyval_to_lower(Gtk.gdk.keyval_from_name('Escape')):
            presenter.on_button_quit_clicked,
        Gtk.gdk.keyval_to_lower(Gtk.gdk.keyval_from_name('F11')):
            presenter.on_fullscreen_toggle
    }
    presenter.set_keymappings(keymappings)

    builder.connect_signals(presenter)

    window.connect("check-resize", presenter.on_window_resize)
    window.connect("window-state-event", presenter.window_state_event_handler)
    window.set_icon_from_file(
        resource_filename('gscreenshot.resources.pixmaps', 'gscreenshot.png')
    )

    view.run()

    GObject.threads_init() # Start background threads.
    Gtk.main()

if __name__ == "__main__":
    main()
