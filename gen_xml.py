import os
import os.path

import lxml.etree

choosen = [9, 18, 22, 23, 27, 33, 35, 37, 40, 43, 46, 49, 52, 55, 58]

data_dir = ''
save_xml = 'train_landmark_15.xml'


def get_coords_and_pts(ptsf):
    pts = []
    with open(ptsf) as f:
        for i, line in enumerate(f):
            if i in [0, 1, 2]:
                continue
            line = line.rstrip()
            if line == '}':
                continue
            x, y = line.split()
            x = int(float(x))
            y = int(float(y))
            pts.append((x, y))
    xmin = min(p[0] for p in pts)
    xmax = max(p[0] for p in pts)
    ymin = min(p[1] for p in pts)
    ymax = max(p[1] for p in pts)
    pts = [e for i, e in enumerate(pts) if i + 1 in choosen]
    return (xmin, ymin, xmax, ymax), pts


def gen_data():
    for entry in os.scandir(os.path.join(data_dir, '300W/01_Indoor')):
        if not entry.name.endswith('.png'):
            continue
        img_path = entry.path
        img_data = entry.path[:-4] + '.pts'
        coords, pts = get_coords_and_pts(img_data)
        yield (img_path, coords, pts)

    for entry in os.scandir(os.path.join(data_dir, '300W/02_Outdoor')):
        if not entry.name.endswith('.png'):
            continue
        img_path = entry.path
        img_data = entry.path[:-4] + '.pts'
        coords, pts = get_coords_and_pts(img_data)
        yield (img_path, coords, pts)


dataset = lxml.etree.Element('dataset')
images = lxml.etree.SubElement(dataset, 'images')

for entry in gen_data():
    path = entry[0]
    coords = entry[1]
    pts = entry[2]
    image = lxml.etree.SubElement(images, 'image', attrib={'file': path})
    xmin = coords[0]
    ymin = coords[1]
    w = coords[2] - xmin
    h = coords[3] - ymin
    box = lxml.etree.SubElement(image, 'box', attrib={
        'top': str(ymin),
        'left': str(xmin),
        'width': str(w),
        'height': str(h)
    })

    for i, pt in enumerate(pts):
        lxml.etree.SubElement(box, 'part', attrib={
            'name': '%02d' % i,
            'x': str(pt[0]),
            'y': str(pt[1]),
        })

tree = lxml.etree.ElementTree(dataset)
tree.write(save_xml, pretty_print=True, xml_declaration=True, encoding='utf-8')
