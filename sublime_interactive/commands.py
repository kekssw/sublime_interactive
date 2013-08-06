
import sublime
import sublime_plugin


class SublimeInteractiveUpdateViewCommand(sublime_plugin.TextCommand):
    def run(self, edit, data, start=0, end=None, read_only=True):
        self.view.set_read_only(False)
        if end is not None:
            self.view.erase(edit, sublime.Region(start, end))
        self.view.insert(edit, start, data)
        self.view.set_read_only(read_only)
