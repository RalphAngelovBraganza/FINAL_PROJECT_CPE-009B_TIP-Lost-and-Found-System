import json
import os
import shutil
import tempfile
from datetime import date, datetime


# Stores the application folder path.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Stores the database file path.
DATA_PATH = os.path.join(BASE_DIR, "lost_and_found.json")

# Stores the image folder path.
IMAGES_DIR = os.path.join(BASE_DIR, "images")


# Lists the available record categories.
CATEGORIES = [
    "Electronics", "Bags", "Clothing", "Accessories", "Wallets and Cards",
    "IDs", "Study Materials", "Tumblers/Containers", "Keys", "Others",
]

# Lists the possible item statuses.
ITEM_STATUSES = ["Unclaimed", "Claimed"]

# Lists the possible inquiry statuses.
INQUIRY_STATUSES = ["Open", "Resolved"]


# Creates the database and required folders.
def create_database():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        save_data({"items": [], "inquiries": [], "claims": [], "settings": {}})


# Loads saved records from the database.
def load_data():
    create_database()
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)
    for key in ("items", "inquiries", "claims", "settings"):
        data.setdefault(key, [] if key != "settings" else {})
    return data


# Writes records to the database.
def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# Returns the next record ID.
def next_id(records, id_key):
    return max((record[id_key] for record in records), default=0) + 1


# Formats a record ID for display.
def format_record_id(prefix, record_date, record_id):
    month = str(record_date or date.today().isoformat())[:7].replace("-", "")[2:]
    return f"{prefix}-{month}-{int(record_id):03d}"


# Finds a record by its field value.
def find_record(records, key, value):
    return next((record for record in records if record.get(key) == value), None)


# Copies the selected photo into the app images folder.
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


# Copies the database to the selected location.
def backup_database(destination):
    shutil.copy2(DATA_PATH, destination)


# Loads and validates a JSON database before replacing the current data.
def import_database(source_path):
    try:
        with open(source_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError("The selected file is not valid JSON.") from error

    if not isinstance(data, dict):
        raise ValueError("The selected file must contain a JSON object.")

    id_keys = {"items": "item_id", "inquiries": "inquiry_id", "claims": "claim_id"}
    for collection, id_key in id_keys.items():
        records = data.get(collection)
        if not isinstance(records, list):
            raise ValueError(f"The JSON file must contain an '{collection}' list.")
        for record in records:
            if not isinstance(record, dict):
                raise ValueError(f"Every entry in '{collection}' must be an object.")
            if not isinstance(record.get(id_key), int) or isinstance(record.get(id_key), bool):
                raise ValueError(f"Every entry in '{collection}' must have a numeric '{id_key}'.")

    settings = data.get("settings", {})
    if not isinstance(settings, dict):
        raise ValueError("The 'settings' value must be an object.")

    imported_data = {
        "items": data["items"],
        "inquiries": data["inquiries"],
        "claims": data["claims"],
        "settings": settings,
    }

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=os.path.dirname(DATA_PATH),
            suffix=".json.tmp", delete=False
        ) as file:
            temp_path = file.name
            json.dump(imported_data, file, indent=4, ensure_ascii=False)
        os.replace(temp_path, DATA_PATH)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

    return {collection: len(imported_data[collection]) for collection in id_keys}
