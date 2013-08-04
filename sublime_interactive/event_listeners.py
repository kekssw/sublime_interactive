
import sublime_plugin

from .view import SUBLIME_INTERACTIVE_VIEWS

class SublimeInteractiveEventListener(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        settings = view.settings()
        if settings.has('sublime_interactive_view'):
            SUBLIME_INTERACTIVE_VIEWS[
                            settings.get('sublime_interactive_view')].process_click()
