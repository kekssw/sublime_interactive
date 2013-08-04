
import sublime
import sublime_plugin


class SublimeInteractiveSetViewContentsCommand(sublime_plugin.TextCommand):
    def run(self, edit, contents):
        self.view.set_read_only(False)
        self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.insert(edit, 0, contents)
        self.view.set_read_only(False)
