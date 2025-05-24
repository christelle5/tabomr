import cv2


# Visualizing results after processing by OCR model
def visualize_yolo_results(results_data, original_image, output_path):
    for data in results_data:
        x1, y1, x2, y2 = data["bbox"]
        label = data["class"]
        if label == "fret_number":
            label = f"pr:{data['pred_number']}"
            cv2.rectangle(original_image, (x1, y1), (x2, y2), (255, 255, 0), 2)
            cv2.putText(original_image, label, (x1, y2 + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.imwrite(output_path, original_image)
    print(f"✅ Marked with recognized fret numbers image has been saved as '{output_path}'")


# Visualization of staffs (after recognition of this class)
def visualize_staffs(staff_objects, original_image, output_path):
    for idx, staff in enumerate(staff_objects):
        x1, y1, x2, y2 = staff["bbox"]
        cv2.rectangle(original_image, (x1, y1), (x2, y2), (255, 0, 255), 1)
        cv2.putText(original_image, f"Staff {idx}", (x1 + 5, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1)
    cv2.imwrite(output_path, original_image)
    print(f"✅ Marked with staff image has been saved as '{output_path}'")


# Visualization of bars
def visualize_bars(staff_data, original_image, output_path):
    for staff_idx, staff in staff_data.items():
        for bar in staff["bars"]:
            x1, y1, x2, y2 = bar["bbox"]
            cv2.rectangle(original_image, (x1, y1), (x2, y2), (255, 0, 255), 1)  # Рамка рожевого кольору
            cv2.putText(original_image, f"Bar {bar['bar_index']}", (x1 + 5, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1)

    cv2.imwrite(output_path, original_image)
    print(f"✅ Marked with bars image has been saved as '{output_path}'")


# Visualization of staffs with updated bboxes
def visualize_updated_staffs(staff_objects, original_image, output_path):
    for idx, staff in enumerate(staff_objects):
        x1, y1, x2, y2 = staff["bbox"]
        cv2.rectangle(original_image, (x1, y1), (x2, y2), (255, 0, 255), 1)  # pink frame
        cv2.putText(original_image, f"Staff {idx}", (x1 + 5, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1)
    cv2.imwrite(output_path, original_image)
    print(f"✅ Marked with updated bboxes of staffs image has been saved as '{output_path}'")


