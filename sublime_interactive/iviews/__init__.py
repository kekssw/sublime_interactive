
import time
import os.path

import sublime


SUBLIME_INTERACTIVE_IVIEWS = []


class BaseIView:
    def __init__(self,
        label=None,
        view=None,
        window=None,
        iregions=None,
        settings=None,
        syntax_file=None
    ):
        if window is None:
            window = sublime.active_window()
        if view is None:
            view = window.new_file()
        self.view = view

        if syntax_file is not None:
            self.view.set_syntax_file(syntax_file)


        default_theme_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..',
            'sublime_interactive.tmTheme'
        )
        packages_path = sublime.packages_path()
        default_theme_path = default_theme_path[len(packages_path) - 8:]

        default_settings = {
            'rulers': [],
            'highlight_line': False,
            'fade_fold_buttons': True,
            'caret_style': 'solid',
            'line_numbers': False,
            'draw_white_space': 'none',
            'gutter': False,
            'indent_guide_options': [],
            'color_scheme': default_theme_path
        }
        if settings is None:
            settings = {}
        default_settings.update(settings)
        view_settings = self.view.settings()
        for name, value in default_settings.items():
            view_settings.set(name, value)

        view_settings.set('sublime_interactive_iview', len(SUBLIME_INTERACTIVE_IVIEWS))
        SUBLIME_INTERACTIVE_IVIEWS.append(self)

        if label is None:
            label = self.__class__.__name__
        self.label = label
        self.view.set_name(self.label)

        self.iregions = []
        if iregions is None:
            iregions = []
        for iregion in iregions:
            self.add_iregion(iregion)

        self.last_event_time = 0
        self.last_point = None
        self.keys = []
        self.drawn = False

    def add_iregion(self, iregion):
        if iregion.iview is not None:
            raise SublimeInteractiveError('IRegion already associated with an IView')
        iregion.iview = self
        self.iregions.append(iregion)
        if self.drawn:
            iregion.draw()

    def add_iregion_index(self, index, iregion):
        if iregion.iview is not None:
            raise SublimeInteractiveError('IRegion already associated with an IView')
        iregion.iview = self
        self.iregions.insert(index, iregion)
        if self.drawn:
            iregion.draw()

    def del_iregion(self, iregion):
        iregion.undraw()
        index = self.iregions.index(iregion)
        del self.iregions[index]
        iregion.iview = None

    def del_iregion_index(self, index):
        iregion = self.iregions[index]
        iregion.undraw()
        del self.iregions[index]
        iregion.iview = None

    def get_iregion(self, index):
        return self.iregions[index]

    def get_iregion_index(self, iregion):
        return self.iregions.index(iregion)

    def get_iregion_count(self):
        return len(self.iregions)

    def has_iregion(self, iregion):
        return iregion in self.iregions

    def draw(self):
        self.drawn = True
        self.view.set_name(self.label)
        for iregion in self.iregions:
            iregion.draw()

    def process(self):
        event_time = time.time()
        regions = self.view.sel()
        if not len(regions) == 1:
            self.view.sel().clear()
            return
        region = regions[0]
        if not region.empty():
            self.view.sel().clear()
            return
        point = region.begin()
        if point == self.last_point and event_time - self.last_event_time < 0.5:
            self.view.sel().clear()
            return
        self.last_event_time = event_time
        self.last_point = point

        for key in self.keys:
            regions = self.view.get_regions(key)
            if regions:
                region = regions[0]
                if region.contains(point) and not point == region.end():
                    iregion = [x for x in self.iregions if x.get_region() == region][0]
                    if not getattr(iregion, 'disabled', False):
                        if hasattr(iregion, 'pre_process'):
                            iregion.pre_process(iregion)
                        if hasattr(iregion, 'process'):
                            iregion.process(iregion)
                        if hasattr(iregion, 'post_process'):
                            iregion.post_process(iregion)
                    return
