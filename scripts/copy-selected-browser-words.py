browser = aqt.dialogs.open("Browser", _mw=mw)
nids = browser.selected_notes()
words = []
for nid in nids:
    note = mw.col.get_note(nid)
    words.append(note["Word"])
print(repr(words))
