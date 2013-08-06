
import sublime_plugin

from .iviews import SUBLIME_INTERACTIVE_IVIEWS

class SublimeInteractiveEventListener(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        settings = view.settings()
        if settings.has('sublime_interactive_iview'):
            SUBLIME_INTERACTIVE_IVIEWS[
                            settings.get('sublime_interactive_iview')].process_click()
