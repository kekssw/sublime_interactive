sublime_interactive
===================

A sublime text 3 interactive view framework. Create views with clickable areas that map to functionality. Buttons, lists, sentences...

## Note:

This is a work in progress.

Anything can change at this stage.

## Usuage:

To test out the example.

You'll need Sublime Text 3 (I'm sure I can alter it to work in both but I aimed for 3 while developing.)

Clone this repository into your Sublime Text *Packages* directory.

    git clone https://github.com/sligodave/sublime_interactive.git SublimeInteractive

Open Sublime Text 3

Open Sublime Text 3's Python Prompt:

	CTRL + `
	Type: window.run_command('example_iView_start')

This should open a new Read Only view, with the content of the example view present.

You can click on the items present, they'll either print to the Python Console or do a few other things.

Most of what you see is configurable and more will be added.

Remember, it's still very much a work in pregress.

## Do it yourself:

It's not very well commented yet.

You basically need a class that extends IView.

You will need a WindowCommand that will instantiate it when it is run.

You then populate the IView with IRegions.

Like Buttons, Text, LineBreaks, Horizontal Rules etc.

You can give each IRegion an "on_click" action.

Have fun, I'll document it better as I get further along. I just wanted to get it uploaded so I didn't lose any work.

## Why did I do this?

I don't know really :) I've been writing a lot of plugins for Sublime Text lately and I started thinking about
interaction with API's etc through plugins and thought a handy interative view framework would be a good
place to start. It may seem like I'm forcing too much into the editor but people can use it as much or as
little as they like.

For me, I was thinking about a view that interacts with my managed web hosting.
It might list out all domains, sites and applications registered.
It might also give me buttons to create new ones, edit old or delete etc.

Sky's the limit really. Ultimately they are just events that trigger python!
What they do is up to you.

## Todo:

- Comment the code completely
- Documentation
- Better examples

## Troubleshooting:

- I've noticed that when you click "Ok" on a popup error message, it'll register as a click again, when the prompt goes away and the cursor is returned to the view. I'm not sure there is much I can do about that. It will probably be up to the implementor to
record flags to catch such events. It doesn't appear to happen all the time. Presumably it's down to click speed and cursor position or something like that.
- If more than one iregion is getting drawn at the same time. Things can get out of line. I may investigate a queue for the draw command. To see this in action. Use the "Get User Input" button while the progress bar is running.

## Issues / Suggestions:

Fire them on! I'll make fixes as they are pointed out and will consider any request for updates.

## Copyright and license
Copyright 2013 David Higgins

[MIT License](LICENSE)
