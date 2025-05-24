import xml.etree.ElementTree as ET
from config import DIVISIONS, DURATION_MAP, FRETS_TO_PITCHES_MAP, FORMAL_DURATION_MAP


def get_duration_value(t_val):  # converter from dictionary value to count of divisions
    return int(DURATION_MAP.get(t_val, 12))  # eighth note, 12 (because all time signatures in 8ths)


def get_pitch(str_num="1", fret_num=0):  # gets corresponding pitch using fret and string number
    str_num = str(str_num)
    if str_num not in FRETS_TO_PITCHES_MAP:
        raise ValueError("Invalid string number. Must be 1-6.")
    if not (0 <= fret_num < len(FRETS_TO_PITCHES_MAP[str_num])):
        raise ValueError("Invalid fret number. Must be between 0 and 15.")
    return FRETS_TO_PITCHES_MAP[str_num][fret_num]


def get_formal_duration(yolo_duration):  # returns formal duration name and True/False for dot's present
    if yolo_duration not in FORMAL_DURATION_MAP:
        raise ValueError("Invalid YOLO duration value. Check in documentation.")
    return FORMAL_DURATION_MAP[yolo_duration]


def convert_to_musicxml(staff_dict, output_file="output.xml"):
    root = ET.Element("score-partwise", version="4.0")

    # Info about score
    ET.SubElement(root, "work-title").text = str(output_file)  # name
    part_list = ET.SubElement(root, "part-list")
    score_part = ET.SubElement(part_list, "score-part", id="P1")  # single part for all the tabs
    ET.SubElement(score_part, "part-name").text = "Guitar Tab"
    ET.SubElement(score_part, "part-abbreviation").text = "Guit."

    score_instrument = ET.SubElement(score_part, "score-instrument", id="P1-I1")
    ET.SubElement(score_instrument, "instrument-name").text = "Classical Guitar (Tablature)"

    ET.SubElement(score_part, "midi-device", id="P1-I1", port="1")
    midi_instrument = ET.SubElement(score_part, "midi-instrument", id="P1-I1")
    ET.SubElement(midi_instrument, "midi-channel").text = "1"
    ET.SubElement(midi_instrument, "midi-program").text = "25"  # guitar
    ET.SubElement(midi_instrument, "volume").text = "78.7402"
    ET.SubElement(midi_instrument, "pan").text = "0"

    # Single part for all of staffs
    part = ET.SubElement(root, "part", id="P1")

    previous_time_sig = None  # time signature in previous bar
    count_of_measures = 0
    measures_prev = 0

    for staff_idx, staff in staff_dict.items():
        count_of_measures += measures_prev
        measures_prev = 0

        for bar in staff["bars"]:
            measure_number = count_of_measures + bar["bar_index"] + 1
            measure = ET.SubElement(part, "measure", number=str(measure_number))
            measures_prev += 1

            time_sig = staff["time_signatures"].get(bar["bar_index"], 0)
            bar_check = bar["bar_index"] + count_of_measures

            if bar_check == 0:  # adding 6-string notation to the first measure
                attributes_elem = ET.SubElement(measure, "attributes")
                ET.SubElement(attributes_elem, "divisions").text = str(DIVISIONS)
                time_tag = ET.SubElement(attributes_elem, "time")
                ET.SubElement(time_tag, "beats").text = str(time_sig)
                ET.SubElement(time_tag, "beat-type").text = "8"

                clef_elem = ET.SubElement(attributes_elem, "clef")
                ET.SubElement(clef_elem, "sign").text = "TAB"
                ET.SubElement(clef_elem, "line").text = "5"

                staff_details = ET.SubElement(attributes_elem, "staff-details")
                ET.SubElement(staff_details, "staff-lines").text = "6"
                # ET.SubElement(staff_details, "capo").text = "0"

                # Adding strings
                str1 = ET.SubElement(staff_details, "staff-tuning", line="1")
                ET.SubElement(str1, "tuning-step").text = "E"
                ET.SubElement(str1, "tuning-octave").text = "2"

                str2 = ET.SubElement(staff_details, "staff-tuning", line="2")
                ET.SubElement(str2, "tuning-step").text = "A"
                ET.SubElement(str2, "tuning-octave").text = "2"

                str3 = ET.SubElement(staff_details, "staff-tuning", line="3")
                ET.SubElement(str3, "tuning-step").text = "D"
                ET.SubElement(str3, "tuning-octave").text = "3"

                str4 = ET.SubElement(staff_details, "staff-tuning", line="4")
                ET.SubElement(str4, "tuning-step").text = "G"
                ET.SubElement(str4, "tuning-octave").text = "3"

                str5 = ET.SubElement(staff_details, "staff-tuning", line="5")
                ET.SubElement(str5, "tuning-step").text = "B"
                ET.SubElement(str5, "tuning-octave").text = "3"

                str6 = ET.SubElement(staff_details, "staff-tuning", line="6")
                ET.SubElement(str6, "tuning-step").text = "E"
                ET.SubElement(str6, "tuning-octave").text = "4"

            # Adding <attributes> if time signature is changed
            if time_sig != previous_time_sig:
                attributes_elem = ET.SubElement(measure, "attributes")
                ET.SubElement(attributes_elem, "divisions").text = str(DIVISIONS)

                time_tag = ET.SubElement(attributes_elem, "time")
                ET.SubElement(time_tag, "beats").text = str(time_sig)
                ET.SubElement(time_tag, "beat-type").text = "8"

                previous_time_sig = time_sig

            # Adding notes & chords
            chords_of_the_bar = staff["chords"].get(bar["bar_index"], [])
            tot_duration = 0

            for bar_chord in chords_of_the_bar:
                first_chord_note = True

                for note in bar_chord:
                    note_elem = ET.SubElement(measure, "note")

                    # if it's the second+ chord's note – adding <chord/> tag
                    if not first_chord_note:
                        ET.SubElement(note_elem, "chord")

                    # Additionally, adding corresponding pitch (MuseScore will appreciate)
                    pitch_step, pitch_oct, pitch_sharp = get_pitch(note["string"]+1, note["pred_number"])
                    pitch = ET.SubElement(note_elem, "pitch")
                    ET.SubElement(pitch, "step").text = str(pitch_step)
                    if pitch_sharp:
                        ET.SubElement(pitch, "alter").text = "1"
                    ET.SubElement(pitch, "octave").text = str(pitch_oct)

                    # Adding duration (in divisions)
                    duration = get_duration_value(note["time_value"])
                    ET.SubElement(note_elem, "duration").text = str(duration)
                    if first_chord_note is True:
                        tot_duration += duration
                    first_chord_note = False

                    # Adding voice (always the 1st; might be improved in future)
                    ET.SubElement(note_elem, "voice").text = "1"

                    # Adding formal type of note + <dot/> tag if required
                    form_duration, has_dot = get_formal_duration(note["time_value"])
                    ET.SubElement(note_elem, "type").text = str(form_duration)
                    if has_dot:
                        ET.SubElement(note_elem, "dot")

                    # Adding tablature data (fret, string)
                    notations = ET.SubElement(note_elem, "notations")
                    technical = ET.SubElement(notations, "technical")
                    ET.SubElement(technical, "string").text = str(note["string"] + 1)
                    ET.SubElement(technical, "fret").text = str(note["pred_number"])

            # Time signature check
            expected_duration = time_sig * 12
            if tot_duration != expected_duration:
                print(
                    f"⚠️ Attention! Bar {bar['bar_index'] + 1} (Staff {staff_idx + 1}) has: {tot_duration}, expected: {expected_duration}!"
                )

    # Adding end barline
    barl_end = ET.SubElement(measure, "barline", location="right")
    ET.SubElement(barl_end, "bar-style").text = "light-heavy"

    # Writing result into file
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"✅ MusicXML file has been saved as '{output_file}' in /outputs_final.")
