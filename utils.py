import re
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
    pass


class Walls(MlEngTest):
    pass


class Tables(MlEngTest):
    pass


tasks_types = {"walls": Walls,
               "rooms": Rooms,
               "tables": Tables,
               "page_info": PageInfo}
