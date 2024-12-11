import os
from ultralytics import YOLO
from pathlib import Path
import xml.etree.ElementTree as ET
import json
import shutil

def convert_yolo_to_xml(yolo_file, image_name, image_width, image_height, names):
    """
    Convert YOLO segmentation output to XML format.
    
    :param yolo_file: Path to YOLO segmentation output file.
    :param image_name: Name of the image file.
    :param image_width: Width of the image.
    :param image_height: Height of the image.
    """
    # Create the root element <image>
    root = ET.Element("image", id="0", name=image_name, width=str(image_width), height=str(image_height))
    
    # Read the YOLO file
    with open(yolo_file, "r") as file:
        lines = file.readlines()
    
    for line in lines:
        # Parse each line into class and points
        data = line.strip().split()
        label = names[int(data[0])]
        points = data[1:]
        if len(points)==0:
            continue
        # Convert points into "x1,y1;x2,y2;..." format
        points_str = ";".join(f"{int(float(points[i])*image_width)}.00,{int(float(points[i+1])*image_height)}.00" for i in range(0, len(points), 2))
        
        # Create a <polygon> element
        polygon = ET.SubElement(root, "polygon", {
            "label": label,
            "source": "semi-auto",
            "occluded": "0",
            "points": points_str,
            "z_order": "0"
        })
    return root

with open('keyword.txt', 'r') as f:
    search_query = f.read()
image_path = Path(f"data/{search_query}/images")
if not image_path.exists: exit()
# Load a model
model = YOLO("yolo11x-seg.pt")
yolo_label_dir = Path(f"data/{search_query}/label")
shutil.rmtree(yolo_label_dir)

sample = ET.parse("coco_categories.xml")
root = sample.getroot()
names = [label.find('name').text for label in root.findall('.//label')]
for img in image_path.iterdir():
    results = model(img)
    file_name = yolo_label_dir / f"{img.stem}.txt"
    results[0].save_txt(str(file_name))
    file_name.touch() # prevent no result, yolo won't save file
    image_name = results[0].path.split("\\")[-1]             # Replace with the actual image name
    image_width = results[0].orig_shape[1]                   # Replace with the actual image width
    image_height = results[0].orig_shape[0]                  # Replace with the actual image height
    image_tag = convert_yolo_to_xml(str(file_name), image_name, image_width, image_height, names)
    root.append(image_tag)
# Write the XML tree to the output file
output_file = f"data/{search_query}/annotations.xml"
output_class = f"data/{search_query}/cvat_labels.txt"
tree = ET.ElementTree(root)
ET.indent(tree, space="  ", level=0)  # Beautify the XML output
tree.write(output_file, encoding="utf-8", xml_declaration=True)
temp = {
    "name": "A",
    "type": "any",
    "attributes": []
}
labels = []
for n in names:
    temp['name'] = n
    labels.append(temp.copy())
with open(output_class, 'w') as f:
    f.write(json.dumps(labels, indent=2))
print(labels)