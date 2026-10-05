import re


ALLOWED_FILE_EXT = [".pdf",".jpg",".jpeg",".png",".doc",".docx",".eml", ".csv", ".xlsx"]
# Regex for Codice AVEPA: ddd-ddd-ddd-ddd-ddd
RE_AVEPA = re.compile(r'\d{3}-\d{3}-\d{3}-\d{3}-\d{3}')