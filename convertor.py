import os
import xml.etree.ElementTree as ET

def rearrange_xml(root, polygon):    
    # 找到 <meta> 標籤並將其移動到結尾
    meta = root.find("meta")
    if meta is not None:
        root.remove(meta)
        root.append(meta)
    
    # 將更新後的 XML 寫入新文件
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

def convert_yolo_to_xml(yolo_file, output_file, image_name, image_width, image_height):
    """
    Convert YOLO segmentation output to XML format.
    
    :param yolo_file: Path to YOLO segmentation output file.
    :param output_file: Path to save the converted XML file.
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
        label = data[0]
        points = data[1:]
        
        # Convert points into "x1,y1;x2,y2;..." format
        points_str = ";".join(f"{points[i]*image_width},{points[i+1]*image_height}" for i in range(0, len(points), 2))
        
        # Create a <polygon> element
        polygon = ET.SubElement(root, "polygon", {
            "label": label,
            "source": "semi-auto",
            "occluded": "0",
            "points": points_str,
            "z_order": "0"
        })
    return polygon
    # Write the XML tree to the output file
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)  # Beautify the XML output
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

# Example usage
file_path = "label/annotations.xml"
tree = ET.parse(file_path)
root = tree.getroot()
yolo_file_path = "save.txt"  # Replace with the actual YOLO file path
output_xml_path = "output.xml"             # Replace with the desired XML file path
image_name = "49538624068.jpg"             # Replace with the actual image name
image_width = 2048                         # Replace with the actual image width
image_height = 1365                        # Replace with the actual image height

polygon = convert_yolo_to_xml(yolo_file_path, output_xml_path, image_name, image_width, image_height)
root.append(polygon)
