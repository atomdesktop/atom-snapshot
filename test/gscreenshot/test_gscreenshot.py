import unittest
from unittest.mock import Mock

from src.gscreenshot import Gscreenshot

class GscreenshotTest(unittest.TestCase):

    def setUp(self):
        self.fake_screenshooter = Mock()
        self.fake_image = Mock()

        self.fake_screenshooter.image = self.fake_image
        self.gscreenshot = Gscreenshot(self.fake_screenshooter)

    def test_screenshot_full_display_defaults(self):

        actual = self.gscreenshot.screenshot_full_display()

        self.fake_screenshooter.grab_fullscreen_.assert_called_once_with(
            0,
            False,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_full_display_delay(self):
        actual = self.gscreenshot.screenshot_full_display(5)

        self.fake_screenshooter.grab_fullscreen_.assert_called_once_with(
            5,
            False,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_full_display_cursor(self):
        actual = self.gscreenshot.screenshot_full_display(capture_cursor=True)

        self.fake_screenshooter.grab_fullscreen_.assert_called_once_with(
            0,
            True,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_selected_defaults(self):

        actual = self.gscreenshot.screenshot_selected()

        self.fake_screenshooter.grab_selection_.assert_called_once_with(
            0,
            False,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_selected_delay(self):
        actual = self.gscreenshot.screenshot_selected(5)

        self.fake_screenshooter.grab_selection_.assert_called_once_with(
            5,
            False,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_selection_cursor(self):
        actual = self.gscreenshot.screenshot_selected(capture_cursor=True)

        self.fake_screenshooter.grab_selection_.assert_called_once_with(
            0,
            True,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_window_defaults(self):

        actual = self.gscreenshot.screenshot_window()

        self.fake_screenshooter.grab_window_.assert_called_once_with(
            0,
            False,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_window_delay(self):
        actual = self.gscreenshot.screenshot_window(5)

        self.fake_screenshooter.grab_window_.assert_called_once_with(
            5,
            False,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_window_cursor(self):
        actual = self.gscreenshot.screenshot_window(capture_cursor=True)

        self.fake_screenshooter.grab_window_.assert_called_once_with(
            0,
            True,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_get_thumbnail(self):

        fake_thumbnail = Mock()
        fake_thumbnail.thumbnail.return_falue = fake_thumbnail
        self.fake_image.copy.return_value = fake_thumbnail

        actual = self.gscreenshot.get_thumbnail(50, 50)
        self.assertEqual(fake_thumbnail, actual)

    def test_get_program_authors(self):
        self.assertIsInstance(self.gscreenshot.get_program_authors(), list)

    def test_get_program_description(self):
        self.assertIsInstance(self.gscreenshot.get_program_description(), str)

    def test_get_program_name(self):
        self.assertIsInstance(self.gscreenshot.get_program_name(), str)

    def test_get_program_license(self):
        self.assertIsInstance(self.gscreenshot.get_program_license(), str)

    def test_get_program_license_text(self):
        self.assertIsInstance(self.gscreenshot.get_program_license_text(), str)

    def test_get_program_website(self):
        self.assertIsInstance(self.gscreenshot.get_program_website(), str)

    def test_get_program_version(self):
        self.assertIsInstance(self.gscreenshot.get_program_version(), str)

    def test_get_supported_formats(self):
        self.assertIsInstance(self.gscreenshot.get_supported_formats(), list)

    def test_get_last_image(self):
        self.assertEqual(self.fake_image, self.gscreenshot.get_last_image())

    def test_get_screenshooter_name(self):
        self.assertEqual(self.fake_screenshooter.__class__.__name__, self.gscreenshot.get_screenshooter_name())

        self.fake_screenshooter.__utilityname__ = "fake"
        self.assertEqual("fake", self.gscreenshot.get_screenshooter_name())


