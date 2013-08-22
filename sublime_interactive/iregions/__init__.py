
import sublime

from ..errors import SublimeInteractiveError
from ..formatters import rectangle


class BaseIRegion:
    def __init__(
        self,
        data='',
        process=None,
        pre_process=None,
        post_process=None,
        iview=None,
        styles=None,
        style_name='__default__',
        scope='',
        icon='',
        flags=sublime.DRAW_NO_OUTLINE | sublime.DRAW_NO_FILL,
        formatter=None,
        formatter_kwargs=None
    ):
        self.iview = iview
        self.key = 'IRegion-%s-%s' % (self.__class__.__name__, id(self))

        self.data = data

        if pre_process is not None:
            self.pre_process = pre_process
        if process is not None:
            self.process = process
        if post_process is not None:
            self.post_process = post_process

        self.formatter = formatter
        self.formatter_kwargs = {} if formatter_kwargs is None else formatter_kwargs

        if styles is None:
            styles = {}
        if not style_name in styles:
            styles[style_name] = {}
        styles[style_name]['scope'] = styles[style_name].get('scope', scope)
        styles[style_name]['icon'] = styles[style_name].get('icon', icon)
        styles[style_name]['flags'] = styles[style_name].get('flags', flags)

        self.styles = styles
        self.style_name = style_name
        self.style_history = []

        self.drawn = False
        self.disabled = False
        self.hidden = False

    def __len__(self):
        length = len(str(self))
        return length

    def __str__(self):
        return self.get_formatted_data()

    def get_formatted_data(self, formatter=None, formatter_kwargs=None):
        data = self.get_data()
        if formatter is None:
            formatter = self.formatter
        if not formatter is None:
            if formatter_kwargs is None:
                formatter_kwargs = self.formatter_kwargs
            data = formatter(data, **formatter_kwargs)
        return data

    def get_data(self):
        return self.data

    def last_end_point(self):
        index = self.iview.iregions.index(self)
        # We can't just get the preceeding because of emply regions
        for i in range(index - 1, -1, -1):
            iregion = self.iview.iregions[i]
            region = iregion.get_region()
            if region is not None:
                return region.end()
        return 0

    def has_region(self):
        return self.get_region() is not None

    def get_region(self):
        if not self.drawn:
            return
        regions = self.iview.view.get_regions(self.key)
        if regions:
            return regions[0]

    def set_region(self, style_name=None, scope=None, icon=None, flags=None):
        if not self.drawn:
            return

        if self.key in self.iview.keys:
            self.del_region()

        last_end_point = self.last_end_point()
        end = last_end_point + len(self)

        region = sublime.Region(last_end_point, end)

        style_name = self.style_name if style_name is None else style_name
        style = self.styles.get(style_name, {})
        scope = style.get('scope',
                        self.styles.get(self.style_name, {}).get('scope', '')) if scope is None else scope
        icon = style.get('icon',
                        self.styles.get(self.style_name, {}).get('icon', '')) if icon is None else icon
        flags = style.get('flags',
                        self.styles.get(self.style_name, {}).get('flags', sublime.DRAW_NO_OUTLINE | sublime.DRAW_NO_FILL)) if flags is None else flags

        self.iview.view.add_regions(self.key, [region], scope, icon, flags)
        self.style_history.append(
            {
                'style_name': style_name,
                'scope': scope,
                'icon': icon,
                'flags': flags
            }
        )

        if not self.key in self.iview.keys:
            self.iview.keys.append(self.key)

        return region

    def del_region(self, forget=False):
        if not self.drawn:
            return
        del self.iview.keys[self.iview.keys.index(self.key)]
        if forget:
            del self.style_history[-1]
        self.iview.view.erase_regions(self.key)

    def pop_region(self, **kwargs):
        if not self.drawn:
            return
        self.del_region(forget=True)
        last_style = self.style_history[-1] if self.style_history else {}
        kwargs.update(last_style)
        self.set_region(**kwargs)

    def hide(self):
        self.hidden = True
        if self.drawn:
            self.undraw()

    def show(self):
        self.hidden = False
        if self.iview.drawn:
            self.draw()

    def enable(self):
        self.disabled = False

    def disable(self):
        self.disabled = True

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
        self.del_region(forget=True)
        self.drawn = False

    def draw(self):
        if self.hidden:
            return
        data = self.get_formatted_data()
        last_style = self.style_history[-1] if self.style_history else {}
        if self.drawn:
            region = self.get_region()
            begin = region.begin()
            end = region.end()
            self.del_region(forget=True)
        else:
            begin = end = self.last_end_point()
        self.iview.view.run_command(
            'sublime_interactive_update_view',
            {
                'data': data,
                'start': begin,
                'end': end
            }
        )
        self.drawn = True
        # When you draw something that is already drawn, we reset it's style to the style when you clicked draw.
        # To force a restyleing, you must also do an undraw first.
        self.set_region(**last_style)

    def process(self, iregion):
        region = self.get_region()
        print('Clicked: %s - %d - %d:%d %d\n\'\'\'%s\'\'\'' % (
            self.key,
            self.iview.view.sel()[0].begin(),
            region.begin(),
            region.end(),
            region.size(),
            self.get_formatted_data()
            )
        )

    def pre_process(self, iregion):
        pass

    def post_process(self, iregion):
        pass


class GenericIRegion(BaseIRegion):
    def get_data(self):
        return str(self.data)


class Space(GenericIRegion):
    def __init__(self, width=1, **kwargs):
        super().__init__(data=' ' * width, **kwargs)


class LineBreak(GenericIRegion):
    def __init__(self, amount=1, **kwargs):
        super().__init__(data='\n' * amount, **kwargs)


class HorizontalRule(GenericIRegion):
    def __init__(self, width=100, **kwargs):
        super().__init__(data='-' * width, **kwargs)


class Button(BaseIRegion):
    def __init__(
        self,
        highlight_style_name='button.highlight',
        **kwargs
    ):
        self.highlight_style_name = highlight_style_name

        kwargs['formatter'] = kwargs.get('formatter', rectangle)
        formatter_kwargs = {
            'min_width': -1,
            'center': True,
            'left_padding': -1,
            'right_padding': -1
        }
        formatter_kwargs.update(kwargs.get('formatter_kwargs', {}))
        kwargs['formatter_kwargs'] = formatter_kwargs

        kwargs['style_name'] = kwargs.get('style_name', 'button')
        kwargs['styles'] = kwargs.get('styles', {})

        if not kwargs['style_name'] in kwargs['styles']:
            kwargs['styles'][kwargs['style_name']] = {
                'scope': 'button',
                'flags': sublime.DRAW_NO_OUTLINE
            }
        if not highlight_style_name in kwargs['styles']:
            kwargs['styles'][highlight_style_name] = {
                'scope': 'button.highlight',
                'flags': sublime.DRAW_NO_OUTLINE
            }
        super().__init__(**kwargs)

    def pre_process(self, iregion):
        self.disable()
        self.set_region(self.highlight_style_name)

    def post_process(self, iregion):
        def call():
            self.pop_region()
            self.enable()
        sublime.set_timeout_async(call, 200)
