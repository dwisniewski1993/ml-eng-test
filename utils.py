import re
import cv2
import numpy as np
import pytesseract
from werkzeug.utils import secure_filename
from pdf2image import convert_from_bytes


class MlEngTest:
    def __init__(self, image):
        self.image = image

    def execute_task(self):
        pass


class PageInfo(MlEngTest):
    def __init__(self, image):
        super().__init__(image)
        self.image = image
        self.text_pages = []
        self.numbers = []
        self.revisions = []

    def extract_text_from_pdf(self):
        filename = secure_filename(self.image.filename)
        pdf_content = self.image.read()
        images = convert_from_bytes(pdf_content)

        for idx, image in enumerate(images, start=1):
            gray_image = image.convert('L')
            page_text = pytesseract.image_to_string(gray_image)

            id_text = {"page_number": idx, "filename": filename, "text": page_text}
            self.text_pages.append(id_text)

            width, height = gray_image.size

            # Extracting numbers from left bottom region
            left_bottom_region = gray_image.crop((int(0.90 * width), int(0.90 * height), width, height))
            num_text = pytesseract.image_to_string(left_bottom_region)
            numbers = re.findall(r'[A-Za-z\d]+\.[-\w\d]+', num_text)
            self.numbers.append(numbers)

            # Extracting revision number and date from right bottom region
            right_bottom_region = image.crop((int(0.90 * width), 0, width, height))
            rev_text = pytesseract.image_to_string(right_bottom_region)
            revision_date_pairs = self.extract_revision_info(rev_text)
            self.revisions.extend(revision_date_pairs)

    @staticmethod
    def extract_revision_info(rev_text):
        date_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
        revision_pattern = r'\b\d+\b'

        revision_date_pairs = []

        lines = rev_text.split('\n')

        for line in lines:
            match_date = re.search(date_pattern, line)
            if match_date:
                match_revision = re.search(revision_pattern, line)
                if match_revision:
                    revision_date_pairs.append({"number": match_revision.group(), "date": match_date.group()})
                    break

        return revision_date_pairs

    def execute_task(self):
        self.extract_text_from_pdf()
        idx = self.text_pages[0]["page_number"] if self.text_pages else None
        detection_result = []

        for page, nums in zip(self.text_pages, self.numbers):
            page_number, filename, text = page["page_number"], page["filename"], page["text"]
            sheet_number = nums[0] if nums else "unknown"
            revisions = self.revisions if self.revisions else None
            result = {"sheet_number": sheet_number, "sheet_name": filename, "revisions": revisions}
            detection_result.append(result)

        response = {"type": "page_info", "imageId": idx, "detectionResult": detection_result}
        return response


class Rooms(MlEngTest):
    def __init__(self, image):
        super().__init__(image)
        self.image = image

    def execute_task(self):
        rooms = self.find_rooms_from_pdf()

        response = {"type": "rooms",
                    "imageId": "some_image_id",
                    "detectionResults": {
                        "rooms": rooms
                    }}
        return response

    def find_rooms_from_pdf(self, noise_removal_threshold=1, corners_threshold=0.1):
        pdf_content = self.image.read()
        images = convert_from_bytes(pdf_content)

        detected_rooms = []

        for idx, image in enumerate(images, start=1):
            img = np.array(image.convert("L"))

            height, width = img.shape
            new_width = int(width * 0.75)
            new_height = int(height * 0.85)

            left_offset = int(width * 0.075)
            top_offset = int(height * 0.075)

            img = img[top_offset:top_offset + new_height, left_offset:left_offset + new_width]

            blurred_img = cv2.GaussianBlur(img, (5, 5), 0)
            contours, _ = cv2.findContours(blurred_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            mask = np.zeros_like(blurred_img)

            selected_contours = []

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > noise_removal_threshold:
                    cv2.fillPoly(mask, [contour], 255)

            cv2.fillPoly(mask, selected_contours, 255)

            img = ~mask

            dst = cv2.cornerHarris(img, 2, 3, 0.04)
            dst = cv2.dilate(dst, None)
            corners = dst > corners_threshold * dst.max()
            # TODO

        return detected_rooms


class Walls(MlEngTest):
    pass


class Tables(MlEngTest):
    pass


tasks_types = {"walls": Walls,
               "rooms": Rooms,
               "tables": Tables,
               "page_info": PageInfo}
