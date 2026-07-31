---
name: Sheet Layout
about: Add a new sheet layout that is still missing from the currently supported collection
title: 'New Sheet layout: [layout name]'
labels: sheet layout
assignees: suheyldroid

---

**Product information**
Just in case something needs to be verified or anyone wants to get any:
- Brand(s) and/or supplier(s) if available: '...'
- Online product link and/or supplier/manufacturer item number: ...
- Image of the physical label sheet if possible (online information is not always clear)

**Page size configuration**

See [here](https://github.com/suheyldroid/better-inventree-label-sheet/blob/main/better_label_sheet/layouts.py) which paper sizes are already defined. If your paper size is not defined yet, please define it as follows:

```python
# change the dimensions and names to your paper size
PAPER_SIZES = {
    "A4": PaperSize("A4", 210, 297) # width, height
}
```

Otherwise, you can remove this section from the issue.

**Layout configuration**

Fill out the following sheet layout definition with the values of your layout:

```python
# replace the below values with your values
{
    "4737": SheetLayout(                # The internal identification string. This MUST be unique.
        display_name="4737",            # The name show in the UI dropdown. Should be unique. This should not include additional label data, that is added automatically.
        page_size=PAPER_SIZES["A4"],    # The size of the entire page 
        label_width=63.5,               # widh of an individual label on the page in mm
        label_height=29.6,              # height of an individual label on the page in mm
        columns=3,                      # number of label columns on one page
        rows=9,                         # number of label rows on one page
        column_spacing=2.54,            # the space between two columns (not the left/right page margin). Might be 0.
        row_spacing=0,                  # the space between two rows (not teh top/bottom page margin). Might be 0.
        corner_radius=3,                # corner radius of an individual label. 0 if the corners are sharp
        spacing_top=None                # top margin of teh first label. None means automatic centering of the labels and is the default
        spacing_left=None               # left margin of the first label. None means automatic centering of the labels and is the default
    )
}
```

**Additional information**
Anything else you want to say.
