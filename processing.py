import cv2
import numpy as np


'''YOLO results processing'''


def preprocess_yolo_results(yolo_results, image, ocr_model):  # OCR model is used here
    results_data = []

    for result in yolo_results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id = int(box.cls)
            class_name = result.names[class_id]
            # confidence = float(box.conf)

            data_entry = {"bbox": (x1, y1, x2, y2), "class": class_name}

            if class_name == "fret_number":
                digit_crop = image[y1:y2, x1:x2]  # cropping fret_number
                digit_crop = cv2.resize(digit_crop, (224, 224))  # rescaling
                digit_crop = np.expand_dims(digit_crop, axis=0)  # adding batch dimension

                pred = ocr_model.predict(digit_crop)  # predicting number using OCR model
                pred_number = np.argmax(pred)

                data_entry["pred_number"] = pred_number  # filling corresponding field

            results_data.append(data_entry)

    return results_data


'''Staff indexation'''


def find_nearest_staff(y, staff_objects):  # nearest staff for each object
    min_dist = float("inf")
    nearest_staff_idx = None
    for i, staff in enumerate(staff_objects):
        y_min, y_max = staff["bbox"][1], staff["bbox"][3]
        dist = min(abs(y - y_min), abs(y - y_max))  # distance to the top/bottom of the staff
        if dist < min_dist:
            min_dist = dist
            nearest_staff_idx = i
    return nearest_staff_idx  # returns index of the nearest staff


''' Functions for bar indexation'''


def check_notes_before_first_barline(fret_numbers, time_values, first_barline_x):
    for note in fret_numbers + time_values:
        note_x = (note["bbox"][0] + note["bbox"][2]) / 2  # center of X
        if note_x < first_barline_x:  # if there is a note before the first barline
            return True
    return False


def check_notes_after_last_barline(fret_numbers, time_values, last_barline_x):
    for note in fret_numbers + time_values:
        note_x = (note["bbox"][0] + note["bbox"][2]) / 2  # center of X
        if note_x > last_barline_x:  # if there is a note after the last barline
            return True
    return False


def process_staff_bars(staff_data, staff_objects):  # Bar processing
    for staff_idx, staff in staff_data.items():

        barlines = sorted(staff["barlines"], key=lambda b: b["bbox"][0])  # Sorting barlines by X
        st_x1, st_y1, st_x2, st_y2 = staff_objects[staff_idx]["bbox"]
        if not barlines:  # if there is no barlines, make single bar, as big as the staff
            bars = [{"bar_index": 0, "bbox": [st_x1, st_y1, st_x2, st_y2]}]

        else:
            bars = []
            y1_values = []
            y2_values = []

            # If the first bar is missing
            first_barline_x = barlines[0]["bbox"][0]
            if check_notes_before_first_barline(staff["fret_numbers"], staff["time_values"], first_barline_x):
                fake_first_barline = {"bbox": [st_x1, st_y1, st_x1 + 5, st_y2]}
                barlines.insert(0, fake_first_barline)

            # Bars & corresponding y1, y2 values
            for i in range(len(barlines) - 1):
                left_bar = barlines[i]
                right_bar = barlines[i + 1]

                y1_values.append(left_bar["bbox"][1])
                y2_values.append(left_bar["bbox"][3])

                bars.append({
                    "bar_index": i,
                    "bbox": [
                        left_bar["bbox"][0],  # x1
                        left_bar["bbox"][1],  # y1
                        right_bar["bbox"][2],  # x2
                        right_bar["bbox"][3]  # y2
                    ]
                })

            # If the last bar is missing
            last_barline_x = barlines[-1]["bbox"][2]
            if check_notes_after_last_barline(staff["fret_numbers"], staff["time_values"], last_barline_x):
                fake_last_barline = {"bbox": [st_x2 - 5, st_y1, st_x2, st_y2]}
                barlines.append(fake_last_barline)

            # Adding last y1, y2
            y1_values.append(barlines[-1]["bbox"][1])
            y2_values.append(barlines[-1]["bbox"][3])

            # Updating staff bboxes using avg barlines' y1 & y2 values to make them more certain for string search
            new_y1 = int(sum(y1_values) / len(y1_values))
            new_y2 = int(sum(y2_values) / len(y2_values))
            staff_objects[staff_idx]["bbox"] = [st_x1, new_y1, st_x2, new_y2]

        staff["bars"] = bars  # saving bars in the staff

    return staff_data


'''Functions for fret numbers processing (nearest time value / string / bar)'''


def find_nearest_time_value(fret_x, time_values):  # nearest time value for each fret number (using x)
    min_dist = float('inf')
    nearest_time_val = None

    for time_val in time_values:
        time_x = (time_val['bbox'][0] + time_val['bbox'][2]) / 2  # center of bbox
        dist = abs(fret_x - time_x)

        if dist < min_dist:
            min_dist = dist
            nearest_time_val = time_val

    if nearest_time_val is None:
        nearest_time_val = 'whole_note'

    return nearest_time_val  # returns (bbox + class) of the nearest time value


def find_nearest_string(fret_y, staff_bbox):  # nearest to fret_number string
    y_min, y_max = staff_bbox[1], staff_bbox[3]
    gap = (y_max - y_min) / 5  # spaces between strings

    string_centers = [y_min + i * gap for i in range(6)]  # centers of 6 strings

    # The nearest string's center
    nearest_string = min(range(6), key=lambda i: abs(fret_y - string_centers[i]))

    return nearest_string


def find_nearest_bar(fret_x, st_bars):
    for b in st_bars:
        bar_x1, _, bar_x2, _ = b["bbox"]
        if bar_x1 <= fret_x <= bar_x2:
            return b["bar_index"]
    return None  # if note is out the bars (under normal circumstances, this is not possible)


def process_fret_numbers(fret_numbers, time_values, staff_bbox, st_bars):  # calling three above functions
    for fret in fret_numbers:
        fret_x = (fret['bbox'][0] + fret['bbox'][2]) / 2  # X center
        fret_y = (fret['bbox'][1] + fret['bbox'][3]) / 2  # Y center

        nearest_time = find_nearest_time_value(fret_x, time_values)  # corresponding time value
        nearest_string = find_nearest_string(fret_y, staff_bbox)  # corr. string
        bar_index = find_nearest_bar(fret_x, st_bars)  # corr. bar

        fret['time_value'] = nearest_time['class'] if nearest_time else 'unknown'
        fret['string'] = nearest_string
        fret['bar_index'] = bar_index

    return fret_numbers


'''Search for chords'''


def find_chords_in_bar(frets):  # For chords processing
    if not frets:
        return []
    frets.sort(key=lambda f: f["bbox"][0])  # sorting frets by X
    res_chords = []
    while frets:
        first_fret = frets.pop(0)
        ch = [first_fret]
        # a half of width of the first note
        chord_threshold = (first_fret["bbox"][2] - first_fret["bbox"][0]) / 2
        for other_fret in frets[:]:  # going through next frets
            if abs(first_fret["bbox"][0] - other_fret["bbox"][0]) < chord_threshold:
                ch.append(other_fret)
                frets.remove(other_fret)  # removing as proceeded
        res_chords.append(ch)

    return res_chords


'''Time Signatures of each bar processing'''


def get_duration_value(time_val):  # one beat = one 8th note
    duration_map = {
        "whole_note": 8,
        "half_note": 4,
        "quarter_note": 2,
        "eighth_note": 1,
        "eighth_note_two": 1,
        "half_note_dot": 6,
        "quarter_note_dot": 3
    }
    return duration_map.get(time_val, 0)
