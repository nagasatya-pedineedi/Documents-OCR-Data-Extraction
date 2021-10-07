from reader.processing import country_code, passport_no, surname, given_name, nationality, gender, date_of_birth, place_of_birth, place_of_issue, date_of_issue, date_of_expiry
from google.cloud import documentai_v1 as documentai
from google.cloud import vision
from datetime import datetime
import pdf2image as p2i
from PIL import Image
import pandas as pd
import threading
import img2pdf
import string
import pickle
import math
import glob
import cv2
import os
import re


puncs = string.punctuation

# Global variables

PROJECT_ID = ''
LOCATION = ''
PROCESSOR_ID = ''
CREDS_PATH = "reader/creds/"
TEMP_PATH = "reader/tmp"

VISION_CREDS = "reader/creds/"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = VISION_CREDS

def extract_info(field_imgs):
    print(">> Extraction started..")

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDS_PATH

    info = {}
    def read_document(file_path, project_id=PROJECT_ID, location=LOCATION,
                      processor_id=PROCESSOR_ID):
        opts = {}
        if location == "eu":
            opts = {"api_endpoint": "eu-documentai.googleapis.com"}
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
        name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"  # noqa

        with open(file_path, "rb") as pdffile:
            pdf_content = pdffile.read()

        document = {"content": pdf_content, "mime_type": "application/pdf"}

        request = {"name": name, "raw_document": document}
        result = client.process_document(request=request)
        document = result.document
        document_pages = document.pages

        pptext = []
        for page in document_pages:
            paragraphs = page.paragraphs
            for paragraph in paragraphs:
                paragraph_text = get_text(paragraph.layout, document)
                pptext.append(paragraph_text)
        key = os.path.basename(file_path).split(".")[-2]
        info[key] = get_extracted_list(pptext)


    def get_text(doc_element, document):
        response = ""
        for segment in doc_element.text_anchor.text_segments:
            start_index = (
                int(segment.start_index)
                if segment in doc_element.text_anchor.text_segments
                else 0
            )
            end_index = int(segment.end_index)
            response += document.text[start_index:end_index]
        return response


    def get_extracted_list(textx):
        tmptext = []
        for i in textx:
            tmptext += i.split("\n")
        tmptext = [x for x in tmptext if len(x) > 0]
        return " ".join(tmptext)


    def convert_image_to_pdf(imgpath):
        image = Image.open(imgpath)
        target = TEMP_PATH + "/" + os.path.basename(imgpath).split(".")[-2] + ".pdf"
        pdf_bytes = img2pdf.convert(image.filename)
        with open(target, 'wb') as pf:
            pf.write(pdf_bytes)
        image.close()

    files = glob.glob(TEMP_PATH+"/*")
    for f in files:
        os.chmod(f, 0o777)
        os.remove(f)
    for i in field_imgs.keys():
        cv2.imwrite(os.path.join(TEMP_PATH, i+".jpg"), field_imgs[i])
    files = glob.glob(TEMP_PATH+"/*.jpg")
    for f in files:
        convert_image_to_pdf(f)
    files = glob.glob(TEMP_PATH+"/*.pdf")
    thds = []
    for f in files:
        thds.append(threading.Thread(target=read_document,args=(f,)))
    for t in thds:
        t.start()
    for t in thds:
        t.join()
    print(">> Extration finished...")
    return info

def rotate_it(mat, angle):
    height, width = mat.shape[:2]
    image_center = (width/2, height/2)
    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)
    abs_cos = abs(rotation_mat[0,0])
    abs_sin = abs(rotation_mat[0,1])
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)
    rotation_mat[0, 2] += bound_w/2 - image_center[0]
    rotation_mat[1, 2] += bound_h/2 - image_center[1]
    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
    return rotated_mat


def find_angle(coord):
    yd = coord[1][1]-coord[0][1]
    xd = coord[1][0]-coord[0][0]
    ang = 0
    try:
        ang = abs(yd)/abs(xd)
    except:
        ang = 99999999
    if yd!=0:
        return yd/abs(yd) * math.atan(ang)*180/math.pi
    else:
        return 0


def pdf_to_image(file):
    print(">> Converting pdf to image started..")
    imgs = p2i.convert_from_path(file, poppler_path=PDF_BIN_FILE)
    for img in imgs:
        img.save(FILENAME)
    print(">> Converting pdf to image finished..")


def get_text_from_image(filepath):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = VISION_CREDS
    print(">> OCR started..")
    img = cv2.imread(filepath)
    byte_img = cv2.imencode('.png', img)[1].tobytes()
    client = vision.ImageAnnotatorClient()
    res = []
    image = vision.Image(content=byte_img)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    print(">> OCR finished..")
    return texts[1:]


def strip_lines(annotations):
    print(">> Indicator identification started..")
    indicators = [
                'Sex',
                'Surname',
                'Nationality',
                'Given',
                'Birth',
                'Issue',
                'Country',
                'Passport',
                'Date'
    ]

    coord_dict = {}
    for i in indicators:
        c = 0
        for a in annotations:
#             print(a.description)
#             print(a.bounding_poly)
            if i in a.description or i in a.description.lower():
                box = []
                xbox = []
                for n in range(0,4):
                    box.append(a.bounding_poly.vertices[n].y)
                    xbox.append(a.bounding_poly.vertices[n].x)
                coord = [
                    [a.bounding_poly.vertices[0].x, a.bounding_poly.vertices[0].y],
                    [a.bounding_poly.vertices[1].x, a.bounding_poly.vertices[1].y],
                ]
                ang = find_angle(coord)
                font_sz = max(box)-min(box)
                coord_dict[i+str(c)] = [min(box)-(font_sz//2), max(box)+(font_sz*4)]
                tan_theta = math.tan(ang*math.pi/180)
                coord_dict[i+str(c)].append(tan_theta)
                coord_dict[i+str(c)].append(ang)
                center = [(max(xbox)+min(xbox))//2,(max(box)-min(box))//2+(75//2)]
                coord_dict[i+str(c)].append(center)
                c+=1
#     for i in coord_dict.keys():
#         if i not in list(coord_dict.keys()):
#             coord_dict[i] = [-1, -1]
    print(">> Indicator identification finished..")
    return coord_dict

def crop_fields(coord_dict, filepath):
    print(">> Indicator cropping started..")
    img = cv2.imread(filepath)
    field_imgs = {}
    for i in coord_dict.keys():
        if coord_dict[i][0]!=-1 and coord_dict[i][1]!=-1:
            delta = int(coord_dict[i][2] * img.shape[1])
            if delta < 0:
                tim = img[coord_dict[i][0]+delta:coord_dict[i][1],0:img.shape[1]]
                coord_dict[i][4][1] -= delta
            else:
                tim = img[coord_dict[i][0]:coord_dict[i][1]+delta,0:img.shape[1]]
            tim = rotate_it(tim, coord_dict[i][3])
            field_imgs[i] = tim
    print(">> Indicator cropping finished..")
    return field_imgs

def extract_all(FILE):
    annotations = get_text_from_image(FILE)
    coords = strip_lines(annotations)
    cropped = crop_fields(coords, FILE)
    info = extract_info(cropped)
    data = {}
    fields = ['Country Code', 'Passport No.', 'Surname', 'Given Names(s)', 'Nationality',
            'Sex', 'Date of Birth', 'Place of Birth', 'Place of Issue', 'Date of Issue', 'Date of Expiry']
    for field in fields:
        if field == "Country Code":
            data[field] = country_code(info)
        elif field == "Passport No.":
            data[field] = passport_no(info)
        elif field == "Surname":
            data[field] = surname(info)
        elif field == "Given Names(s)":
            data[field] = given_name(info)
        elif field == "Nationality":
            data[field] = nationality(info)
        elif field == "Sex":
            data[field] = gender(info)
        elif field == "Date of Birth":
            data[field] = date_of_birth(info)
        elif field == "Place of Birth":
            data[field] = place_of_birth(info)
        elif field == "Place of Issue":
            print("calling the place_of_issue")
            data[field] = place_of_issue(info)
        elif field == "Date of Issue":
            data[field] = date_of_issue(info)
        elif field == "Date of Expiry":
            data[field] = date_of_expiry(info)
    return data
