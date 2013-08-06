
import sublime

from ..errors import SublimeInteractiveError


class BaseIRegion:
    scope = ''
    icon = ''
    flags = sublime.DRAW_NO_OUTLINE | sublime.DRAW_NO_FILL
    highlight_flags = None

    def __init__(self, on_click=None, region=None, iview=None):
        if on_click is not None:
            self.on_click = on_click
        self.iview = iview
        self.key = 'IRegion-%s-%s' % (self.__class__.__name__, id(self))
        self.highlighted = False
        self.drawn = False
        self.disabled = False
        self.hidden = False

    def __len__(self):
        return len(self.__str__())

    def __str__(self):
        raise SublimeInteractiveError('Function "__str__" not implemented')

    def last_end_point(self):
        index = self.iview.iregions.index(self)
        return 0 if index == 0 else self.iview.iregions[index - 1].get_region().end()

    def has_region(self):
        return self.get_region() is not None

    def get_region(self):
        if not self.drawn:
            return
        regions = self.iview.view.get_regions(self.key)
        if regions:
            return regions[0]

    def set_region(self, scope=None, icon=None, flags=None):
        if not self.drawn:
            return
        if scope is None:
            scope = self.scope
        if icon is None:
            icon = self.icon
        if flags is None:
            flags = self.flags
        if self.key in self.iview.keys:
            self.del_region()
        last_end_point = self.last_end_point()
        if self.hidden:
            end = last_end_point
        else:
            end = last_end_point + len(self)
        region = sublime.Region(last_end_point, end)
        self.iview.view.add_regions(self.key, [region], scope, icon, flags)
        if not self.key in self.iview.keys:
            self.iview.keys.append(self.key)
        return region

    def del_region(self):
        if not self.drawn:
            return
        del self.iview.keys[self.iview.keys.index(self.key)]
        self.iview.view.erase_regions(self.key)

    def set_highlighted_region(self):
        if self.drawn and getattr(self, 'highlight_flags', False):
            self.highlighted = True
            self.set_region(flags=self.highlight_flags)

    def del_highlighted_region(self, timeout=200):
        if self.drawn:
            self.highlighted = False
            sublime.set_timeout_async(self.set_region, timeout)

    def hide(self):
        self.hidden = True
        if self.drawn:
            self.draw()

    def show(self):
        self.hidden = False
        if self.drawn:
            self.draw()

    def undraw(self):
        if not self.drawn:
            return
        region = self.get_region()
        self.iview.view.run_command(
            'sublime_interactive_update_view',
            {
                'data': '',
                'start': region.begin(),
                'end': region.end()
            }
        )
        self.del_region()
        self.drawn = False

    def draw(self):
        data = str(self)
        if self.drawn:
            region = self.get_region()
            begin = region.begin()
            end = region.end()
            self.del_region()
        else:
            begin = end = self.last_end_point()
        if self.hidden:
            data = ''
        self.iview.view.run_command(
            'sublime_interactive_update_view',
            {
                'data': data,
                'start': begin,
                'end': end
            }
        )
        self.drawn = True
        if hasattr(self,  'highlighted') and self.highlighted:
            self.set_highlighted_region()
        else:
            self.set_region()

    def on_click(self, iregion):
        if hasattr(self, 'set_highlighted_region'):
            self.set_highlighted_region()
        region = self.get_region()
        print('Clicked: %s - %d - %d:%d %d\n"""%s"""' % (
            self.key,
            self.iview.view.sel()[0].begin(),
            region.begin(),
            region.end(),
            region.size(),
            str(self)
            )
        )
        if hasattr(self, 'del_highlighted_region'):
            self.del_highlighted_region()


class GenericIRegion(BaseIRegion):
    def __init__(self, content='', on_click=None, region=None, iview=None):
        self.content = content
        super().__init__(on_click=on_click, region=region, iview=iview)

    def __str__(self):
        return str(self.content)


class Space(GenericIRegion):
    def __init__(self, width=1, on_click=None, region=None, iview=None):
        super().__init__(content=' ' * width, on_click=on_click, region=region, iview=iview)


class LineBreak(GenericIRegion):
    def __init__(self, amount=1, on_click=None, region=None, iview=None):
        super().__init__(content='\n' * amount, on_click=on_click, region=region, iview=iview)


class HorizontalRule(GenericIRegion):
    def __init__(self, width=100, on_click=None, region=None, iview=None):
        super().__init__(content='-' * width, on_click=on_click, region=region, iview=iview)


class Button(BaseIRegion):
    scope = 'comment'
    flags = sublime.DRAW_OUTLINED | sublime.DRAW_NO_FILL
    highlight_flags = sublime.DRAW_NO_OUTLINE

    def __init__(
        self,
        label,
        min_width=0,
        left_padding=-1,
        right_padding=-1,
        on_click=None,
        region=None,
        iview=None
    ):
        self.label = label
        self.min_width = min_width
        self.left_padding = left_padding
        self.right_padding = right_padding
        super().__init__(on_click=on_click, region=region, iview=iview)

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
