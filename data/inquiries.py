from datetime import date
from data.store import load_data, save_data, next_id, find_record, format_record_id


# Saves a new lost item inquiry.
def add_inquiry(data):
    records = load_data()
    inquiry = dict(data)
    inquiry.update(inquiry_id=next_id(records["inquiries"], "inquiry_id"),
                   date_reported=date.today().isoformat(), status="Open")
    records["inquiries"].append(inquiry)
    save_data(records)


# Handles filter inquiries.
def _filter_inquiries(records, search, status="All", date_filter=""):
    if status != "All":
        records = [item for item in records if item.get("status") == status]
    if date_filter:
        records = [item for item in records
                   if date_filter in (item.get("date_lost", ""), item.get("date_reported", ""))]
    if search:
        term = search.casefold()
        fields = ("student_name", "tip_email", "item_name", "item_description", "category", "color", "brand",
                  "location_last_seen", "additional_details")
        records = [item for item in records if term in format_record_id("INQ", item.get("date_reported"), item["inquiry_id"]).casefold() or any(term in str(item.get(field, "")).casefold() for field in fields)]
    return records


# Returns inquiries matching the selected filters.
def get_inquiries(search="", status="All", date_filter=""):
    records = load_data()["inquiries"]
    records = _filter_inquiries(records, search, status, date_filter)
    return sorted(records, key=lambda item: item["inquiry_id"], reverse=True)


# Finds an inquiry by its ID.
def get_inquiry_by_id(inquiry_id):
    return find_record(load_data()["inquiries"], "inquiry_id", inquiry_id)


# Saves changes to an inquiry.
def update_inquiry(inquiry_id, data):
    records = load_data()
    inquiry = find_record(records["inquiries"], "inquiry_id", inquiry_id)
    if inquiry is None:
        raise ValueError("That inquiry could not be found.")
    inquiry.update(data)
    save_data(records)


# Updates an inquiry status.
def update_inquiry_status(inquiry_id, new_status):
    records = load_data()
    inquiry = find_record(records["inquiries"], "inquiry_id", inquiry_id)
    if inquiry is None:
        raise ValueError("That inquiry could not be found.")
    inquiry["status"] = new_status
    save_data(records)
