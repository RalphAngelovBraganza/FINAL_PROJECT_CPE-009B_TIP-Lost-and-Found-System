import json
import os
import shutil
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "lost_and_found.json")
IMAGES_DIR = os.path.join(BASE_DIR, "images")

CATEGORIES = [
    "Electronics", "Bags", "Clothing", "Accessories", "Wallets and Cards",
    "IDs", "Study Materials", "Tumblers/Containers", "Keys", "Others",
]
ITEM_STATUSES = ["Unclaimed", "Claimed"]
INQUIRY_STATUSES = ["Open", "Resolved"]


def create_database():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        save_data({"items": [], "inquiries": [], "claims": [], "settings": {}})


def load_data():
    create_database()
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)
    for key in ("items", "inquiries", "claims", "settings"):
        data.setdefault(key, [] if key != "settings" else {})
    return data


def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def next_id(records, id_key):
    return max((record[id_key] for record in records), default=0) + 1


def format_record_id(prefix, record_date, record_id):
    month = str(record_date or date.today().isoformat())[:7].replace("-", "")[2:]
    return f"{prefix}-{month}-{int(record_id):03d}"


def find_record(records, key, value):
    return next((record for record in records if record.get(key) == value), None)


def copy_image_to_images(source_path):
    os.makedirs(IMAGES_DIR, exist_ok=True)
    if not source_path:
        return ""
    source_path = os.path.abspath(source_path)
    if not os.path.isfile(source_path):
        raise OSError("The photo file could not be found.")
    ext = os.path.splitext(source_path)[1].lower() or ".jpg"
    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ext
    dest_path = os.path.join(IMAGES_DIR, filename)
    base, extension = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest_path):
        filename = f"{base}_{counter}{extension}"
        dest_path = os.path.join(IMAGES_DIR, filename)
        counter += 1
    shutil.copy2(source_path, dest_path)
    return os.path.join("images", filename)


def backup_database(destination):
    shutil.copy2(DATA_PATH, destination)
