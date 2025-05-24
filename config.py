# For MusicXML
DIVISIONS = 24  # 1 quarter note = 24 divisions
DURATION_MAP = {
    "whole_note": 96,
    "half_note": 48,
    "half_note_dot": 72,
    "quarter_note": 24,
    "quarter_note_dot": 36,
    "eighth_note": 12,
    "eighth_note_two": 12,
    "eighth_note_dot": 18
}

FRETS_TO_PITCHES_MAP = {
    "1": [("E", 4, False), ("F", 4, False), ("F", 4, True), ("G", 4, False), ("G", 4, True),
          ("A", 4, False), ("A", 4, True), ("B", 4, False), ("C", 5, False), ("C", 5, True),
          ("D", 5, False), ("D", 5, True), ("E", 5, False), ("F", 5, False), ("F", 5, True), ("G", 5, False)],
    "2": [("B", 3, False), ("C", 4, False), ("C", 4, True), ("D", 4, False), ("D", 4, True),
          ("E", 4, False), ("F", 4, False), ("F", 4, True), ("G", 4, False), ("G", 4, True),
          ("A", 4, False), ("A", 4, True), ("B", 4, False), ("C", 5, False), ("C", 5, True), ("D", 5, False)],
    "3": [("G", 3, False), ("G", 3, True), ("A", 3, False), ("A", 3, True), ("B", 3, False),
          ("C", 4, False), ("C", 4, True), ("D", 4, False), ("D", 4, True), ("E", 4, False),
          ("F", 4, False), ("F", 4, True), ("G", 4, False), ("G", 4, True), ("A", 4, False), ("A", 4, True)],
    "4": [("D", 3, False), ("D", 3, True), ("E", 3, False), ("F", 3, False), ("F", 3, True),
          ("G", 3, False), ("G", 3, True), ("A", 3, False), ("A", 3, True), ("B", 3, False),
          ("C", 4, False), ("C", 4, True), ("D", 4, False), ("D", 4, True), ("E", 4, False), ("F", 4, False)],
    "5": [("A", 2, False), ("A", 2, True), ("B", 2, False), ("C", 3, False), ("C", 3, True),
          ("D", 3, False), ("D", 3, True), ("E", 3, False), ("F", 3, False), ("F", 3, True),
          ("G", 3, False), ("G", 3, True), ("A", 3, False), ("A", 3, True), ("B", 3, False), ("C", 4, False)],
    "6": [("E", 2, False), ("F", 2, False), ("F", 2, True), ("G", 2, False), ("G", 2, True),
          ("A", 2, False), ("A", 2, True), ("B", 2, False), ("C", 3, False), ("C", 3, True),
          ("D", 3, False), ("D", 3, True), ("E", 3, False), ("F", 3, False), ("F", 3, True), ("G", 3, False)]
}

FORMAL_DURATION_MAP = {
    "whole_note": ("whole", False),
    "half_note": ("half", False),
    "half_note_dot": ("half", True),
    "quarter_note": ("quarter", False),
    "quarter_note_dot": ("quarter", True),
    "eighth_note": ("eighth", False),
    "eighth_note_two": ("eighth", False),
    "eighth_note_dot": ("eighth", True)
}
