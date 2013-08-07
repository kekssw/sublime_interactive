
import time
import threading

import sublime
import sublime_plugin

# import .webfaction
from .sublime_interactive.formatters import rectangle
from .sublime_interactive.commands import SublimeInteractiveUpdateViewCommand
from .sublime_interactive.event_listeners import SublimeInteractiveEventListener
from .sublime_interactive.iviews import BaseIView
from .sublime_interactive.iregions import BaseIRegion, GenericIRegion, Button,\
                                            Space, LineBreak, HorizontalRule

class GetInputButton(Button):
    def __init__(self):
        super().__init__(label='Get User Input', formatter_kwargs={'min_width': 30})

    def process(self, iregion):
        '''
        Prompts the user for input when clicked.
        '''
        super().process(iregion)
        self.get_input()

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
                    self.iview.add_iregion_index(7, text)
                    self.iview.add_iregion_index(7, line_breaks)
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
        super().__init__(label='Clear User Input', formatter_kwargs={'min_width': 30})

    def process(self, iregion):
        super().process(iregion)
        if hasattr(self.iview, 'temp_example_container'):
            for iregion in self.iview.temp_example_container:
                self.iview.del_iregion(iregion)
            del self.iview.temp_example_container


class ErrorButton(Button):
    def __init__(self):
        super().__init__(label='Create Error Message', formatter_kwargs={'min_width': 30})

    def process(self, iregion):
        '''
        Basic on click handler.
        Only raises an error message in sublime text
        '''
        super().process(iregion)
        sublime.error_message('This is an error message')


class StatusButton(Button):
    '''
    Basic on click handler.
    Only writes a status message in sublime text's status bar
    '''
    def __init__(self):
        super().__init__(label='Create Status Message', formatter_kwargs={'min_width': 30})

    def process(self, iregion):
        super().process(iregion)
        sublime.status_message('This is an status message')


class ProgressBar(BaseIRegion):
    def __init__(self, width=50):
        self.percentage = 0
        self.width = width
        super().__init__()

    def get_data(self):
        content = '-' * (int((self.width / 100) * self.percentage))
        content += ' ' * (self.width - int((self.width / 100) * self.percentage))
        return content


class ProgressPercentage(BaseIRegion):
    def __init__(self):
        self.percentage = 0
        super().__init__()

    def get_data(self):
        return ('%d%%' % (self.percentage)).rjust(4)


class DownloadButton(Button):
    def __init__(self):
        super().__init__(label='Start Download', formatter_kwargs={'min_width': 64})

    def pre_process(self, iregion):
        pass
    post_process = pre_process

    def process(self, iregion):
        super().process(iregion)

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
        self.button.hide()

        done = 0
        while done <= self.total:
            percentage = 100 * (done / self.total)
            self.progress_bar_iregion.percentage = percentage
            self.progress_percentage_iregion.percentage = percentage
            self.progress_bar_iregion.draw()
            self.progress_percentage_iregion.draw()
            done += 1
            time.sleep(.02)

        self.button.show()


class TextWithBorder(GenericIRegion):
    '''
    An IRegion that extends the generic iregion with
    a border when it's drawn
    '''
    def __init__(self, content):
        flags = sublime.DRAW_OUTLINED | sublime.DRAW_NO_FILL
        super().__init__(content, scope='comment', flags=flags)


class ExampleIView(BaseIView):
    '''
    Example Interactive View.
    Really, the skys the limit.
    This has a title, a horizontal rule and then three buttons.
    '''
    def __init__(self, window=None):
        super().__init__(
            label='Example IView',
            window=window
        )

        # Title text at the top of the view and horizontal line
        self.add_iregion(
            GenericIRegion(
                'This is an Example IView',
                formatter=rectangle,
                formatter_kwargs={'center': True, 'min_width': 64}
            )
        )
        self.add_iregion(LineBreak())
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

        # 3 Bodies of text
        self.add_iregion(
            GenericIRegion(
                '''This is the first line in a body of text.
    This is the second line in the same body of text.
    This is the third line!
    Forth.
    And fifth.''',
                process=lambda x: x.set_region(
                    scope='button.highlight',
                    flags=sublime.DRAW_OUTLINED
                ),
                post_process=lambda x: sublime.set_timeout_async(x.pop_region, 200),
                style_name='button',
                styles={
                    'button': {
                        'scope': 'button',
                        'flags': sublime.DRAW_OUTLINED
                    },
                    'button.highlight': {
                        'scope': 'button.highlight',
                        'flags': sublime.DRAW_OUTLINED
                    }
                },
                formatter=rectangle,
                formatter_kwargs={'min_width': 64, 'left_padding': 0}
            )
        )
        self.add_iregion(LineBreak(2))

        self.add_iregion(
            GenericIRegion(
                '''This is the first line in a body of text.
    This is the second line in the same body of text.
    This is the third line!
    Forth.
    And fifth.''',
                process=lambda x: x.set_region(
                    scope='button.highlight',
                    flags=sublime.DRAW_OUTLINED
                ),
                post_process=lambda x: sublime.set_timeout_async(x.pop_region, 200),
                style_name='button',
                styles={
                    'button': {
                        'scope': 'button',
                        'flags': sublime.DRAW_OUTLINED
                    },
                    'button.highlight': {
                        'scope': 'button.highlight',
                        'flags': sublime.DRAW_OUTLINED
                    }
                },
                formatter=rectangle,
                formatter_kwargs={'min_width': 64, 'left_padding': -1}
            )
        )
        self.add_iregion(LineBreak(2))

        self.add_iregion(
            GenericIRegion(
                '''This is the first line in a body of text.
    This is the second line in the same body of text.
    This is the third line!
    Forth.
    And fifth.''',
                process=lambda x: x.set_region(
                    scope='button.highlight',
                    flags=sublime.DRAW_OUTLINED,
                ),
                post_process=lambda x: sublime.set_timeout_async(x.pop_region, 200),
                style_name='button',
                styles={
                    'button': {
                        'scope': 'button',
                        'flags': sublime.DRAW_OUTLINED
                    },
                    'button.highlight': {
                        'scope': 'button.highlight',
                        'flags': sublime.DRAW_OUTLINED
                    }
                },
                formatter=rectangle,
                formatter_kwargs={'min_width': 64, 'right_padding': 0}
            )
        )
        self.add_iregion(LineBreak(2))

        # DownloadButton ProgressBar ProgressPercentage
        # When you click the download button, it threads off a fake
        # download process and updates the bar and percentage as it goes
        self.add_iregion(DownloadButton())
        self.add_iregion(GenericIRegion('\n\n| '))
        self.add_iregion(ProgressBar(width=55))
        self.add_iregion(GenericIRegion(' | '))
        self.add_iregion(ProgressPercentage())
        self.add_iregion(LineBreak(2))

        # Button Space Text Space Button
        # First button hides the text.
        # Second button shows the text.
        text = TextWithBorder(' TEXT ')
        self.add_iregion(
            Button(
                'Hide Text >',
                process=lambda x: text.hide(),
                formatter_kwargs={'min_width': 28, 'right_padding': 1}
            )
        )
        self.add_iregion(Space())
        self.add_iregion(text)
        self.add_iregion(Space())
        self.add_iregion(
            Button(
                '< Show Text',
                process=lambda x: text.show(),
                formatter_kwargs={'min_width': 28, 'left_padding': 1}
            )
        )
        self.add_iregion(LineBreak())

        # Draw all the iregions in the iview
        self.draw()


class ExampleIViewStartCommand(sublime_plugin.WindowCommand):
    '''
    Sublime Text Command to instantiate the IView
    '''
    def run(self):
        ExampleIView(self.window)
