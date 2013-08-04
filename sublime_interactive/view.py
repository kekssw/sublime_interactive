
import time

import sublime
from .regions import MultiInteractiveRegion


SUBLIME_INTERACTIVE_VIEWS = []


class InteractiveView:
    def __init__(self,
        label='Interactive View',
        view=None,
        window=None,
        interactive_regions=None,
        syntax_file='Packages/Python/Python.tmLanguage'
    ):
        if window is None:
            window = sublime.active_window()
        if view is None:
            view = window.new_file()
        self.view = view

        self.set_syntax_file(syntax_file)
        settings = self.settings()
        settings.set('sublime_interactive_view', len(SUBLIME_INTERACTIVE_VIEWS))
        SUBLIME_INTERACTIVE_VIEWS.append(self)

        self.label = label

        if interactive_regions is None:
            interactive_regions = []
        self.interactive_regions = interactive_regions
        self.reset()

    def reset(self):
        self.keys = []
        self.region_interactive_region_map = {}
        self.last_click_time = 0
        self.last_point = None

        self.set_name(self.label)

    def __getattr__(self, attr):
        if self.view and hasattr(self.view, attr):
            return getattr(self.view, attr)
        raise AttributeError("%s does not exist on %s" % (attr, self.__class__.__name__))

    def add_interactive_regions(self, interactive_region):
        self.interactive_regions.append(interactive_region)

    def get_interactive_region_from_region(self, region):
        region_key = '%d:%d' % (region.begin(), region.end())
        return self.region_interactive_region_map.get(region_key, None)

    def generate(self):
        self.reset()

        contents = ''
        last_end = 0
        keyed_regions = {}
        interactive_regions_with_regions = []
        for interactive_region in self.interactive_regions:
            if isinstance(interactive_region, MultiInteractiveRegion):
                for sub_interactive_region in getattr(interactive_region, getattr(interactive_region, 'container', 'interactive_regions'), []):
                    for i in range(2):
                        if i == 1:
                            # Expand this to allow seperator be a list with arguements
                            sub_interactive_region = interactive_region.seperator()
                        interactive_region_as_string = str(sub_interactive_region)
                        new_end = last_end + len(interactive_region_as_string)
                        region = sublime.Region(last_end, new_end)
                        key = sub_interactive_region.key()
                        if not key in self.keys:
                            self.keys.append(key)
                        sub_interactive_region.region = region
                        sub_interactive_region.view = self
                        interactive_regions_with_regions.append(sub_interactive_region)
                        self.region_interactive_region_map['%d:%d' % (last_end, new_end)] = sub_interactive_region
                        contents += interactive_region_as_string
                        last_end = new_end
            else:
                interactive_region_as_string = str(interactive_region)
                new_end = last_end + len(interactive_region_as_string)
                region = sublime.Region(last_end, new_end)
                key = interactive_region.key()
                if not key in self.keys:
                    self.keys.append(key)
                interactive_region.region = region
                interactive_region.view = self
                interactive_regions_with_regions.append(interactive_region)
                self.region_interactive_region_map['%d:%d' % (last_end, new_end)] = interactive_region
                contents += interactive_region_as_string
                last_end = new_end
        self.run_command('sublime_interactive_set_view_contents', {'contents': contents})
        for interactive_region in interactive_regions_with_regions:
            interactive_region.add_view_region()
        self.set_read_only(True)

    def process_click(self):
        click_time = time.time()
        regions = self.sel()
        if not len(regions) == 1:
            self.sel().clear()
            return
        region = regions[0]
        if not region.empty():
            self.sel().clear()
            return
        point = region.begin()
        if point == self.last_point and click_time - self.last_click_time < 0.5:
            return False
        self.last_click_time = time.time()
        self.last_point = point

        for key in self.keys:
            regions = self.get_regions(key)
            for region in regions:
                if region.contains(point) and not point == region.end():
                    interactive_region = self.get_interactive_region_from_region(region)
                    getattr(interactive_region, 'on_click', lambda x: x)(interactive_region)
                    return
