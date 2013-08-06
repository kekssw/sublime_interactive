
import time
import threading

import sublime
import sublime_plugin

# import .webfaction
from .sublime_interactive.commands import SublimeInteractiveUpdateViewCommand
from .sublime_interactive.event_listeners import SublimeInteractiveEventListener
from .sublime_interactive.iviews import BaseIView
from .sublime_interactive.iregions import BaseIRegion, GenericIRegion, Button,\
                                            Space, LineBreak, HorizontalRule

class GetInputButton(Button):
    def __init__(self):
        super().__init__(label='Get User Input', min_width=30)

    def on_click(self, iregion):
        """
        Prompts the user for input when clicked.
        """
        print('Clicked - Get User Input')
        self.set_highlighted_region()
        self.get_input()
        self.del_highlighted_region()

    def get_input(self, user_input=None):
        # it is str, then not the first run, test the input
        if isinstance(user_input, str):
            # Was input provided?
            if user_input:
                print('Adding User Input Region from View')
                # Test to see if this is the first time this button was run.
                # If it was then we have to add our GenericIRegion Region to the end of the view.
                if not hasattr(self.iview, 'temp_example_container'):
                    line_breaks = LineBreak(2)
                    text = GenericIRegion('You entered "%s"' % user_input)
                    self.iview.add_iregion_index(7, line_breaks)
                    self.iview.add_iregion_index(8, text)
                    self.iview.temp_example_container = [line_breaks, text]
                else:
                    self.iview.temp_example_container[1].content = 'You entered "%s"' % user_input
                    self.iview.temp_example_container[1].draw()
                # End
                return
            # No input, write error
            sublime.error_message('Please enter input')
        # Prompt the user for input
        self.iview.view.window().show_input_panel(
            'Input',
            '',
            self.get_input,
            None,
            None
        )


class ClearInputButton(Button):
    def __init__(self):
        super().__init__(label='Clear User Input', min_width=30)

    def on_click(self, iregion):
        print('Clearing User Input Region from View')
        self.set_highlighted_region()
        if hasattr(self.iview, 'temp_example_container'):
            for iregion in self.iview.temp_example_container:
                self.iview.del_iregion(iregion)
            del self.iview.temp_example_container
        self.del_highlighted_region()


class ErrorButton(Button):
    def __init__(self):
        super().__init__(label='Create Error Message', min_width=30)

    def on_click(self, interactive_region):
        """
        Basic on click handler.
        Only raises an error message in sublime text
        """
        print('Creating error message prompt')
        self.set_highlighted_region()
        sublime.error_message('This is an error message')
        self.del_highlighted_region()


class StatusButton(Button):
    """
    Basic on click handler.
    Only writes a status message in sublime text's status bar
    """
    def __init__(self):
        super().__init__(label='Create Status Message', min_width=30)

    def on_click(self, iregion):
        print('Creating status message in status bar')
        self.set_highlighted_region()
        sublime.status_message('This is an status message')
        self.del_highlighted_region()


class ProgressBar(BaseIRegion):
    def __init__(self):
        self.percentage = 0
        self.width = 50
        super().__init__()

    def __str__(self):
        content = '\u25A0' * (int((self.width / 100) * self.percentage))
        content += ' ' * (self.width - int((self.width / 100) * self.percentage))
        return content


class ProgressPercentage(BaseIRegion):
    def __init__(self):
        self.percentage = 0
        super().__init__()

    def __str__(self):
        return '%d%%' % (self.percentage)


class DownloadButton(Button):
    def __init__(self):
        super().__init__(label='Start Download')

    def on_click(self, iregion):
        print('Starting dummy download')
        self.set_highlighted_region()
        self.disabled = True
        # We know the bar is two iregions after the download button
        progress_bar_iregion_index = self.iview.get_iregion_index(self) + 2
        progress_bar_iregion = self.iview.get_iregion(progress_bar_iregion_index)
        progress_percentage_iregion_index = progress_bar_iregion_index + 2
        progress_percentage_iregion = self.iview.get_iregion(progress_percentage_iregion_index)

        downloader = Downloader(100, self, progress_bar_iregion, progress_percentage_iregion)
        downloader.start()


class Downloader(threading.Thread):
    def __init__(self, total, button, progress_bar_iregion, progress_percentage_iregion):
        self.total = total
        self.button = button
        self.progress_bar_iregion = progress_bar_iregion
        self.progress_percentage_iregion = progress_percentage_iregion
        super().__init__()

    def run(self):
        done = 0
        while done <= self.total:
            percentage = 100 * (done / self.total)
            self.progress_bar_iregion.percentage = percentage
            self.progress_percentage_iregion.percentage = percentage
            self.progress_bar_iregion.draw()
            self.progress_percentage_iregion.draw()
            done += 1
            time.sleep(.02)
        self.button.del_highlighted_region()
        self.button.disabled = False


class TextWithBorder(GenericIRegion):
    """
    An IRegion that extends the generic iregion with
    a border when it's drawn
    """
    scope = 'comment'
    flags = sublime.DRAW_OUTLINED | sublime.DRAW_NO_FILL
    def __init__(self, content):
        super().__init__(content)


class ExampleIView(BaseIView):
    """
    Example Interactive View.
    Really, the skys the limit.
    This has a title, a horizontal rule and then three buttons.
    """
    def __init__(self, window=None):
        super().__init__(
            label='Example IView',
            window=window,
            settings={
                "rulers": [],
                "highlight_line": False,
                "always_show_minimap_viewport": False,
                "fade_fold_buttons": True,
                "caret_style": 'solid'
            }
        )

        # Title text at the top of the view and horizontal line
        self.add_iregion(GenericIRegion('This is an Example IView\n'))
        self.add_iregion(HorizontalRule(64))
        self.add_iregion(LineBreak(2))

        # Input and Clear button
        # The Input button prompts the user for input and creates a new
        # region to display the input
        # The clear button, removes the newly displayed input if present
        self.add_iregion(GetInputButton())
        self.add_iregion(Space(4))
        self.add_iregion(ClearInputButton())
        self.add_iregion(LineBreak(2))

        # ErrorButton Status Button
        # The error button triggers a sublime text error message
        # The status button triggers a sublime text status message
        self.add_iregion(ErrorButton())
        self.add_iregion(Space(4))
        self.add_iregion(StatusButton())
        self.add_iregion(LineBreak(2))

        # DownloadButton ProgressBar ProgressPercentage
        # When you click the download button, it threads off a fake
        # download process and updates the bar and percentage as it goes
        self.add_iregion(DownloadButton())
        self.add_iregion(GenericIRegion('\n\n| '))
        self.add_iregion(ProgressBar())
        self.add_iregion(GenericIRegion(' | '))
        self.add_iregion(ProgressPercentage())
        self.add_iregion(LineBreak(2))

        # Button Space Text Space Button
        # First button hides the text.
        # Second button shows the text.
        text = TextWithBorder('TEXT')
        self.add_iregion(
            Button(
                'Hide Text >',
                on_click=lambda x: text.hide(),
                min_width=20,
                right_padding=1
            )
        )
        self.add_iregion(Space())
        self.add_iregion(text)
        self.add_iregion(Space())
        self.add_iregion(
            Button(
                '< Show Text',
                on_click=lambda x: text.show(),
                min_width=20,
                left_padding=1
            )
        )
        self.add_iregion(LineBreak())

        # Draw all the iregions in the iview
        self.draw()


class ExampleIViewStartCommand(sublime_plugin.WindowCommand):
    """
    Sublime Text Command to instantiate the IView
    """
    def run(self):
        ExampleIView(self.window)
