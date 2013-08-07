
import sublime_plugin

from .iviews import SUBLIME_INTERACTIVE_IVIEWS

class SublimeInteractiveEventListener(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        settings = view.settings()
        if settings.has('sublime_interactive_iview'):
            sublime_interactive_iview_index = settings.get('sublime_interactive_iview')
            if sublime_interactive_iview_index < len(SUBLIME_INTERACTIVE_IVIEWS):
                SUBLIME_INTERACTIVE_IVIEWS[sublime_interactive_iview_index].process()
