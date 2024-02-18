import re
import numpy as np
from PIL import Image
import cv2
from tesserocr import PyTessBaseAPI
from module.utils import resource_path


def crop_image(img, box_lines):
    if isinstance(img, np.ndarray):
        img = Image.fromarray(img)
    roi = img.crop(
        (box_lines["left"], box_lines["top"], box_lines["right"], box_lines["bottom"])
    )
    return roi


def ocr_image(img, scale=3):
    im_gray = img.convert("L")

    # Resize the image (300% by default)
    new_size = (int(im_gray.width * scale), int(im_gray.height * scale))
    resized_im_gray = im_gray.resize(new_size, Image.LANCZOS)

    kernel = np.ones((3, 3), np.uint8)
    conv_img = np.array(resized_im_gray)
    new_img = cv2.erode(conv_img, kernel, iterations=1)

    with PyTessBaseAPI(path=resource_path(r"app/model/tesseract-ocr/"), lang="eng") as api:
        temp = Image.fromarray(new_img)
        api.SetVariable("preserve_interword_spaces", "1")
        api.SetImage(temp)

        return api.GetUTF8Text()


def clean_text(input_text):
    pattern = r"(?:Lith|Meso|Neo|Axi)\s[A-Z][1-9][0-9]?\s(?:Intact|Exceptional|Flawless|Radiant)"
    match = re.search(pattern, input_text)
    if match:
        return match.group(0)
    else:
        return None


def get_recommended_relic(screenshot, relic):
    text_from_image = ocr_image(img=crop_image(img=screenshot, box_lines=relic))
    cleaned_text = clean_text(text_from_image)
    if cleaned_text is None and text_from_image != "":
        for scale in [2.75, 2.5, 2]:
            text_from_image = ocr_image(
                img=crop_image(img=screenshot, box_lines=relic), scale=scale
            )
            cleaned_text = clean_text(text_from_image)
            if cleaned_text:
                break
        if cleaned_text is None:
            raise ValueError("Unable to get recommended relic from overlay (RegEX).")
    return cleaned_text


def recommended_relic_box_lines():
    crop_box = {"V": [1427, 1655, 1660, 1888], "H": [80, 102, 148, 170]}
    relic_1 = {
        "left": crop_box["V"][0],
        "top": crop_box["H"][0],
        "right": crop_box["V"][1],
        "bottom": crop_box["H"][1],
    }
    relic_2 = {
        "left": crop_box["V"][2],
        "top": crop_box["H"][0],
        "right": crop_box["V"][3],
        "bottom": crop_box["H"][1],
    }
    relic_3 = {
        "left": crop_box["V"][0],
        "top": crop_box["H"][2],
        "right": crop_box["V"][1],
        "bottom": crop_box["H"][3],
    }
    relic_4 = {
        "left": crop_box["V"][2],
        "top": crop_box["H"][2],
        "right": crop_box["V"][3],
        "bottom": crop_box["H"][3],
    }
    return relic_1, relic_2, relic_3, relic_4
