
import sublime
import sublime_plugin

# import .webfaction
from .sublime_interactive.commands import SublimeInteractiveSetViewContentsCommand
from .sublime_interactive.event_listeners import SublimeInteractiveEventListener
from .sublime_interactive.view import InteractiveView
from .sublime_interactive.regions import Button, Space, AnyString, LineBreak, HorizontalRule, OrderedList, UnOrderedList

class GetInputButton(Button):
    def __init__(self):
        super().__init__('Get User Input', min_width=50)

    def on_click(self, interactive_region):
        """
        Prompts the user for input when clicked.
        """
        self.add_view_highlight()
        self.get_input()
        self.del_view_highlight()

    def get_input(self, user_input=None):
        # it is str, then not the first run, test the input
        if isinstance(user_input, str):
            # Was input provided?
            if user_input:
                print('Adding User Input Region from View')
                # Test to see if this is the first time this button was run.
                # If it was then we have to add our AnyString Region to the end of the view.
                if isinstance(self.view.interactive_regions[-1], LineBreak):
                    self.view.add_interactive_regions(AnyString())
                # Set the text in the AnyString region at the end of the view
                self.view.interactive_regions[-1].content = 'You entered "%s"' % user_input
                # Regenerate the view and it's regions
                self.view.generate()
                # End
                return
            # No input, write error
            sublime.error_message('Please enter input')
        # Prompt the user for input
        self.view.window().show_input_panel(
            'Input',
            '',
            self.get_input,
            None,
            None
        )


class ClearInputButton(Button):
    def __init__(self):
        super().__init__('Clear User Input', min_width=50)

    def on_click(self, interactive_region):
        print('Clearing User Input Region from View')
        self.add_view_highlight()
        if getattr(self.view.interactive_regions[-1], 'content', '').startswith('You entered '):
            del self.view.interactive_regions[-1]
            self.view.generate()
        self.del_view_highlight()



class ErrorButton(Button):
    def __init__(self):
        super().__init__('Create Error Message', min_width=50)

    def on_click(self, interactive_region):
        """
        Basic on click handler.
        Only raises an error message in sublime text
        """
        print('Creating error message prompt')
        self.add_view_highlight()
        sublime.error_message('This is an error message')
        self.del_view_highlight()


class StatusButton(Button):
    """
    Basic on click handler.
    Only writes a status message in sublime text's status bar
    """
    def __init__(self):
        super().__init__('Create Status Message', min_width=50)

    def on_click(self, interactive_region):
        print('Creating status message in status bar')
        self.add_view_highlight()
        sublime.status_message('This is an status message')
        self.del_view_highlight()


class MyInteractiveView(InteractiveView):
    """
    Example Interactive View.
    Really, the skys the limit.
    This has a title, a horizontal rule and then three buttons.
    """
    def __init__(self, window=None):
        super().__init__(label='My Interactive View', window=window)
        self.add_interactive_regions(AnyString('This is my interactive view\n'))
        self.add_interactive_regions(HorizontalRule())
        self.add_interactive_regions(LineBreak())
        self.add_interactive_regions(LineBreak())
        self.add_interactive_regions(GetInputButton())
        self.add_interactive_regions(Space(4))
        self.add_interactive_regions(ClearInputButton())
        self.add_interactive_regions(LineBreak(2))
        self.add_interactive_regions(ErrorButton())
        self.add_interactive_regions(Space(4))
        self.add_interactive_regions(StatusButton())
        self.add_interactive_regions(LineBreak(2))

        self.add_interactive_regions(OrderedList(['Item One', 'Item Two', 'Item Three'], right_padding=': '))
        self.add_interactive_regions(LineBreak(2))
        self.add_interactive_regions(UnOrderedList(['Item One', 'Item Two', 'Item Three']))
        self.add_interactive_regions(LineBreak(2))

        self.generate()


class MyInteractiveViewStartCommand(sublime_plugin.WindowCommand):
    """
    Sublime Text Command to instantiate the Interactive View
    """
    def run(self):
        MyInteractiveView(self.window)
