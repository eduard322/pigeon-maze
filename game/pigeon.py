def slice_sheet(sheet, frame_w, frame_h):
    """Cut a horizontal strip sheet into a list of frame Surfaces."""
    width = sheet.get_width()
    cols = width // frame_w
    return [
        sheet.subsurface((i * frame_w, 0, frame_w, frame_h)).copy()
        for i in range(cols)
    ]
