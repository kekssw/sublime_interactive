
import time

import sublime

from .errors import SublimeInteractiveError


class InteractiveRegion:
    scope = ''
    icon = ''
    flags = sublime.DRAW_NO_OUTLINE | sublime.DRAW_NO_FILL
    highlight_flags = None

    def __init__(self):
        # All set by the interactive view when it
        # "renders" the interactive region in the view
        self.region = None
        self.view = None

    def __getattr__(self, attr):
        if self.region and hasattr(self.region, attr):
            return getattr(self.region, attr)
        raise AttributeError("%s does not exist on %s" % (attr, self.__class__.__name__))

    def __len__(self):
        return len(self.__str__())

    def __str__(self):
        raise SublimeInteractiveError('Function "__str__" not implemented')

    def key(self):
        return 'InteractiveRegion-%s' % self.__class__.__name__

    def add_view_region(self):
        key = self.key()
        regions = self.view.get_regions(key)
        if not self.region in regions:
            regions.append(self.region)
            self.view.add_regions(key, regions, self.scope, self.icon, self.flags)

    def del_view_region(self):
        key = self.key()
        regions = self.view.get_regions(key)
        if self.region in regions:
            del regions[regions.index(self.region)]
            self.view.add_regions(key, regions, self.scope, self.icon, self.flags)

    def add_view_highlight(self):
        if self.highlight_flags:
            self.del_view_region()
            key = 'Highlighted-%s' % self.key()
            regions = self.view.get_regions(key)
            if not self.region in regions:
                regions.append(self.region)
                self.view.add_regions(key, regions, self.scope, self.icon,
                                                                        self.highlight_flags)

    def del_view_highlight(self, timeout=200):
        if self.highlight_flags:
            key = 'Highlighted-%s' % self.key()
            regions = self.view.get_regions(key)
            if self.region in regions:
                del regions[regions.index(self.region)]
                delayed_call = lambda: self.view.add_regions(key, regions, self.scope,
                                            self.icon, self.highlight_flags); self.add_view_region()
                sublime.set_timeout_async(delayed_call, timeout)

    def on_click(self, interactive_region):
        if hasattr(self, 'add_view_highlight'):
            self.add_view_highlight()
        print('Clicked: %s - %d - %d:%d\n"""%s"""' % (
            self.key(),
            self.view.sel()[0].begin(),
            self.region.begin(),
            self.region.end(),
            str(self)
            )
        )
        if hasattr(self, 'del_view_highlight'):
            self.del_view_highlight()


class AnyString(InteractiveRegion):
    def __init__(self, content=''):
        self.content = content
        super().__init__()

    def __str__(self):
        return str(self.content)


class Space(AnyString):
    def __init__(self, width=1):
        super().__init__(' ' * width)


class LineBreak(AnyString):
    def __init__(self, amount=1):
        super().__init__('\n' * amount)


class HorizontalRule(AnyString):
    def __init__(self, width=100):
        super().__init__('-' * width)


class Button(InteractiveRegion):
    scope = 'comment'
    flags = sublime.DRAW_OUTLINED | sublime.DRAW_NO_FILL
    highlight_flags = sublime.DRAW_NO_OUTLINE

    def __init__(self, label, on_click=None, min_width=0, left_padding=-1, right_padding=-1):
        self.label = label
        self.min_width = min_width
        self.left_padding = left_padding
        self.right_padding = right_padding
        if on_click is not None:
            self.on_click = on_click
        super().__init__()

    def __str__(self):
        as_str = ' ' * self.left_padding
        as_str += self.label
        as_str += ' ' * self.right_padding
        button_length = len(as_str)
        if button_length < self.min_width:
            left = self.min_width - button_length
            if self.left_padding == self.right_padding == -1:
                left_padding = ' ' * (left // 2)
                right_padding = (' ' * ((left // 2) + (left % 2)))
            elif self.right_padding == -1:
                left_padding = ''
                right_padding = ' ' * left
            else:
                left_padding = ' ' * left
                right_padding = ''
            as_str = left_padding + as_str + right_padding
        return as_str


class ListSubInteractiveRegion(AnyString):
    def __init__(self, bullet, text, left_padding='', right_padding=' '):
        self.bullet = bullet
        self.text = text
        super().__init__(left_padding + str(bullet) + right_padding + text)


class MultiInteractiveRegion:
    pass

class OrderedList(MultiInteractiveRegion):
    seperator = LineBreak
    container = 'interactive_regions'
    def __init__(self, interactive_regions=None, left_padding='', right_padding=' '):
        self.left_padding = left_padding
        self.right_padding = right_padding
        if interactive_regions is None:
            interactive_regions = []
        self.interactive_regions = []
        for text in interactive_regions:
            self.add(text)

    def add(self, text):
        sub_interactive_region = ListSubInteractiveRegion(len(self.interactive_regions) + 1, text, self.left_padding, self.right_padding)
        self.interactive_regions.append(sub_interactive_region)

    def insert(self, index, text):
        sub_interactive_region = ListSubInteractiveRegion(index + 1, text, self.left_padding, self.right_padding)
        self.interactive_regions.insert(index, sub_interactive_region)
        for sub_interactive_region in self.interactive_regions[index + 1:]:
            sub_interactive_region.__init__(sub_interactive_region.index + 1, sub_interactive_region.text, self.left_padding, self.right_padding)

    def remove(self, index):
        del self.interactive_regions[index]
        for sub_interactive_region in self.interactive_regions[index:]:
            sub_interactive_region.__init__(sub_interactive_region.index - 1, sub_interactive_region.text, self.left_padding, self.right_padding)


class UnOrderedList(MultiInteractiveRegion):
    seperator = LineBreak
    container = 'interactive_regions'
    def __init__(self, interactive_regions=None, left_padding='', right_padding=' ', bullet='*'):
        self.left_padding = left_padding
        self.right_padding = right_padding
        self.bullet = bullet
        if interactive_regions is None:
            interactive_regions = []
        self.interactive_regions = []
        for text in interactive_regions:
            self.add(text)

    def add(self, text):
        sub_interactive_region = ListSubInteractiveRegion(self.bullet, text, self.left_padding, self.right_padding)
        self.interactive_regions.append(sub_interactive_region)

    def insert(self, index, text):
        sub_interactive_region = ListSubInteractiveRegion(self.bullet, text, self.left_padding, self.right_padding)
        self.interactive_regions.insert(index, sub_interactive_region)

    def remove(self, index):
        del self.interactive_regions[index]
