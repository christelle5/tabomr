import cv2
# import numpy as np
from ultralytics import YOLO
import tensorflow as tf
import os
from processing import preprocess_yolo_results, process_staff_bars, find_nearest_staff, \
    process_fret_numbers, find_chords_in_bar, get_duration_value
from visualization import visualize_yolo_results, visualize_staffs, visualize_updated_staffs, \
    visualize_bars
from processing_musicxml import convert_to_musicxml
# import xml.etree.ElementTree as ET


# Downloading the models
# yolo_model = YOLO("models/tab-yolo-v1/old-best.pt")  # YOLO
# ocr_model = tf.keras.models.load_model("models/ocr-cnn/old-cnn-1_norm.keras")  # OCR
yolo_model = YOLO("models/tab-yolo-v1/best.pt")  # YOLO
ocr_model = tf.keras.models.load_model("models/ocr-cnn/cnn2_N2.keras")  # OCR

# Importing input image (!!!)
image_path = "test210.png"
image = cv2.imread(image_path)
original_image = image.copy()

# Creating a folder for intermediate results if it does not exist
stages_dir = "outputs_working"
os.makedirs(stages_dir, exist_ok=True)

output_ocr_numbers = os.path.join(stages_dir, f"output_ocr_numbers_{image_path}")
output_staff = os.path.join(stages_dir, f"output_staff_{image_path}")
output_staff_updated = os.path.join(stages_dir, f"output_staff_updated_{image_path}")
output_bars = os.path.join(stages_dir, f"output_bars_{image_path}")
output_time_vals = os.path.join(stages_dir, f"output_time_vals_{image_path}")

# Creating a folder for final results (.MusicXML files) if it does not exist
final_dir = "outputs_final"
os.makedirs(final_dir, exist_ok=True)

res_file = os.path.join(final_dir, f"musicxml_{image_path}.xml")

# Recognizing & classifying with YOLO
yolo_results = yolo_model(image)

# Results preprocessing
results_data = preprocess_yolo_results(yolo_results, image, ocr_model)
# Visualizing results after being processed by OCR model
visualize_yolo_results(results_data, original_image, output_ocr_numbers)

# Staff indexation
staff_objects = [obj for obj in results_data if obj["class"] == "staff"]
staff_objects.sort(key=lambda s: s["bbox"][1])  # sorting staffs up to down

# Adding staff_index to all objects, except staff
for obj in results_data:
    if obj["class"] != "staff":
        y_center = (obj["bbox"][1] + obj["bbox"][3]) // 2
        obj["staff_index"] = find_nearest_staff(y_center, staff_objects)

# Visualization of the staffs
image = cv2.imread(image_path)
original_image = image.copy()
visualize_staffs(staff_objects, original_image, output_staff)

# Grouping objects by staff_index
staff_data = {i: {"time_values": [], "fret_numbers": [], "barlines": []} for i in range(len(staff_objects))}

for obj in results_data:
    if "staff_index" in obj:
        staff = staff_data[obj["staff_index"]]
        if obj["class"] == "fret_number":
            staff["fret_numbers"].append(obj)
        elif obj["class"] in ["half_note", "quarter_note", "eighth_note",
                              "half_note_dot", "quarter_note_dot", "eighth_note_two"]:
            staff["time_values"].append(obj)
        elif obj["class"] in ["barline", "barline_end"]:
            staff["barlines"].append(obj)  # separate for barlines

# Bar indexation (with missing barline handling)
staff_data = process_staff_bars(staff_data, staff_objects)

# Visualization of bars
image = cv2.imread(image_path)
original_image = image.copy()
visualize_bars(staff_data, original_image, output_bars)

# Visualization of updated staffs (bboxes have been updated during barlines processing)
image = cv2.imread(image_path)
original_image = image.copy()
visualize_updated_staffs(staff_objects, original_image, output_staff_updated)

# For visualization of frets & time values
image = cv2.imread(image_path)
original_image = image.copy()

# Going through each staff
for staff_idx, data in staff_data.items():
    st_bbox = staff_objects[staff_idx]["bbox"]
    processed_frets = process_fret_numbers(data["fret_numbers"], data["time_values"], st_bbox, data["bars"])

    # Visualization
    for fret in processed_frets:
        x1, y1, x2, y2 = fret["bbox"]
        # pred_number = fret["pred_number"]  # fret
        time_value = fret["time_value"]
        string_number = fret["string"]
        bar_number = fret["bar_index"]

        # Blue rectangle for fret_number bbox
        cv2.rectangle(original_image, (x1, y1), (x2, y2), (255, 255, 0), 2)

        # # Green label for predicted number by CNN
        # cv2.putText(original_image, f"{pred_number}", (x1, y1 - 30),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 1)

        # Red label for class of corresponding time value object
        cv2.putText(original_image, f"{time_value}", (x1, y2 + 23),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Blue label for calculated string
        cv2.putText(original_image, f"str:{string_number+1}", (x1, y2 + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 1)

        # And a label for calculated bar
        cv2.putText(original_image, f"bar: {bar_number+1}", (x1, y2 + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (144, 200, 0), 1)

    print(f">< Staff {staff_idx}:")
    for fret in processed_frets:
        print(f"    Fret: {fret['pred_number']}, Time value: {fret['time_value']}, String: {fret['string']}, "
              f"Bar: {fret['bar_index']}")

cv2.imwrite(output_time_vals, original_image)
print(f"✅ Marked with string indexes and time values image has been saved as 'output_time_vals_{image_path}'.")
print()

# Searching for chords in each bar
for staff_idx, staff in staff_data.items():
    print(f">< Staff {staff_idx}:")

    for bar in staff["bars"]:
        bar_idx = bar["bar_index"]
        bar_frets = [fret for fret in staff["fret_numbers"] if fret["bar_index"] == bar_idx]

        chords = find_chords_in_bar(bar_frets)

        if "chords" not in staff:
            staff["chords"] = {}
        staff["chords"][bar_idx] = chords

        print(f"  |-- Bar {bar_idx}:")
        for chord in chords:
            note_repr = ", ".join([f"{f['pred_number']} (str {f['string']})" for f in chord])
            print(f"        Chord: {note_repr}")

# Searching for time signatures of each bar
for staff in staff_data.values():
    staff["time_signatures"] = {}

# Going through each staff to find Time Signatures of each bar
for staff_idx, staff in staff_data.items():
    for bar in staff["bars"]:
        bar_index = bar["bar_index"]

        # Taking all chords of this bar
        chords_in_bar = staff["chords"].get(bar_index, [])

        total_duration = 0

        for chord in chords_in_bar:
            if chord:
                first_note = chord[0]  # taking time value of the first note of the chord
                duration = get_duration_value(first_note["time_value"])
                total_duration += duration

        staff["time_signatures"][bar_index] = total_duration

print("\n>< Time Signatures for Each Staff and Bar:")
for staff_idx, staff in staff_data.items():
    print(f"Staff {staff_idx}:")
    for bar in staff["bars"]:
        bar_index = bar["bar_index"]
        time_signature = staff["time_signatures"].get(bar_index, "?")  # getting time signature
        print(f"   Bar {bar_index}, Time Signature: {time_signature}/8")
print("✅ Done!")

'''Converting into MUSICXML'''

# Converting into MusicXML format
convert_to_musicxml(staff_data, res_file)
