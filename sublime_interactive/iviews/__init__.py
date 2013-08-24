
import time
import os.path

import sublime

from ..errors import SublimeInteractiveError
from ..iregions import BaseIRegion, GenericIRegion


SUBLIME_INTERACTIVE_IVIEWS = []


class BaseIView:
    def __init__(
        self,
        label=None,
        view=None,
        window=None,
        iregions=None,
        igroups=None,
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
            'word_wrap': False,
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

        if igroups is None:
            igroups = []
        self.igroups = igroups

        self.last_event_time = 0
        self.keys = []
        self.drawn = False
        self.disabled = False

    def add_iregion(self, iregion):
        if not isinstance(iregion, BaseIRegion):
            iregion = GenericIRegion(data=iregion)
        if iregion.iview is not None:
            raise SublimeInteractiveError('IRegion already associated with an IView')
        iregion.iview = self
        if hasattr(iregion, 'igroup') and not iregion.igroup in self.igroups:
            self.igroups.append(iregion.igroup)
        self.iregions.append(iregion)
        if self.drawn:
            iregion.draw()
        return iregion

    def add_iregions(self, iregions):
        for i, iregion in enumerate(iregions):
            iregion = self.add_iregion(iregion)
            iregions[i] = iregion
        return iregions

    def add_iregion_index(self, index, iregion):
        if isinstance(index, BaseIRegion):
            index = self.iregions.index(index)
        if not isinstance(iregion, BaseIRegion):
            iregion = GenericIRegion(data=iregion)
        if iregion.iview is not None:
            raise SublimeInteractiveError('IRegion already associated with an IView')
        iregion.iview = self
        self.iregions.insert(index, iregion)
        if self.drawn:
            iregion.draw()
        return iregion

    def add_iregions_index(self, index, iregions):
        if isinstance(index, BaseIRegion):
            index = self.iregions.index(index)
        iregions.reverse()
        for i, iregion in enumerate(iregions):
            iregion = self.add_iregion_index(index, iregion)
            iregions[i] = iregion
        iregions.reverse()
        return iregions

    def del_iregion(self, iregion):
        iregion.undraw()
        index = self.iregions.index(iregion)
        del self.iregions[index]
        iregion.iview = None
        if iregion.igroup and not [x for x in self.iregions if x.igroup == iregion.igroup]:
            del self.igroups[self.igroups.index(iregion.igroup)]

    def del_iregions(self, iregions=None):
        if iregions is None:
            iregions = self.iregions[::]
        while iregions:
            iregion = iregions.pop()
            self.del_iregion(iregion)

    def del_iregion_index(self, index):
        iregion = self.iregions[index]
        iregion.undraw()
        del self.iregions[index]
        iregion.iview = None
        if iregion.igroup and not [x for x in self.iregions if x.igroup == iregion.igroup]:
            del self.igroups[self.igroups.index(iregion.igroup)]

    def get_iregion(self, index):
        return self.iregions[index]

    def get_iregion_index(self, iregion):
        return self.iregions.index(iregion)

    def get_iregion_count(self):
        return len(self.iregions)

    def has_iregion(self, iregion):
        return iregion in self.iregions

    def draw(self):
        if self.drawn:
            self.undraw()
        self.drawn = True
        self.view.set_name(self.label)
        for iregion in self.iregions:
            iregion.draw()

    def undraw(self):
        for iregion in self.iregions:
            iregion.undraw()
        self.drawn = False

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

    def process(self):
        if self.disabled:
            return
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
        if event_time - self.last_event_time < 0.1:
            self.view.sel().clear()
            return
        self.last_event_time = event_time

        for key in self.keys:
            regions = self.view.get_regions(key)
            if regions:
                region = regions[0]
                if region.contains(point) and not point == region.end():
                    iregion = [x for x in self.iregions if x.get_region() == region][0]
                    if not iregion.disabled:
                        handler = iregion.igroup if iregion.igroup else iregion
                        if hasattr(handler, 'pre_process'):
                            handler.pre_process(iregion)
                        if hasattr(handler, 'process'):
                            handler.process(iregion)
                        if hasattr(handler, 'post_process'):
                            handler.post_process(iregion)
                    return
