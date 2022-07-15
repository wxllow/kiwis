# Props

## What are props in kiwis?

In kiwis, props are simply data that is passed to Jinja templates.

Kiwis has data which it will pass to all of your templates by default. These are `site` and `page`

Markdown files will also pass a `_md` prop, which contains the metadata and the contents as HTML of the file.

Props you pass from Python scripts are in a dictionary named `props` that you can access from your templates.

## Passing props

To get started passing your own props to kiwis, simply make a `.py` file with the name of your template file (minus the extension it has).

From here, you can run code and define a `props` variable which will be passed to your template.
