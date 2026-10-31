from datetime import date
from data.store import load_data, save_data, next_id, find_record, format_record_id


# Adds a new inquiry to the JSON file with a unique ID, today's date, and an Open status.
# This keeps each new inquiry properly recorded and ready for staff to review.
def add_inquiry(data):
    records = load_data()
    inquiry = dict(data)
    inquiry.update(inquiry_id=next_id(records["inquiries"], "inquiry_id"),
                   date_reported=date.today().isoformat(), status="Open")
    records["inquiries"].append(inquiry)
    save_data(records)


# Filters inquiries according to the selected status and search keyword.
# The search checks the formatted inquiry ID and the details listed in SEARCH_FIELDS, making records easier to find.
def _filter_inquiries(records, search, status="All"):
    if status != "All":
        records = [item for item in records if item.get("status") == status]
    if search:
        term = search.casefold()
        fields = ("student_name", "tip_email", "item_name", "item_description", "category", "color", "brand",
                  "location_last_seen", "additional_details")
        records = [item for item in records if term in format_record_id("INQ", item.get("date_reported"), item["inquiry_id"]).casefold() or any(term in str(item.get(field, "")).casefold() for field in fields)]
    return records


# Retrieves inquiries for display in the table and applies the requested filters.
# The results are sorted by inquiry ID in descending order so newer inquiries appear first.
def get_inquiries(search="", status="All"):
    records = load_data()["inquiries"]
    records = _filter_inquiries(records, search, status)
    return sorted(records, key=lambda item: item["inquiry_id"], reverse=True)


# Finds a specific inquiry using its numeric ID.
# It returns the matching record if it exists, or None if no inquiry matches the ID.
def get_inquiry_by_id(inquiry_id):
    return find_record(load_data()["inquiries"], "inquiry_id", inquiry_id)


# Updates the details of an existing inquiry using its ID.
# If the inquiry cannot be found, the function raises an error instead of updating the wrong record.
def update_inquiry(inquiry_id, data):
    records = load_data()
    inquiry = find_record(records["inquiries"], "inquiry_id", inquiry_id)
    if inquiry is None:
        raise ValueError("That inquiry could not be found.")
    inquiry.update(data)
    save_data(records)


# Changes an inquiry's status, such as from Open to Resolved or back again.
# The function checks that the inquiry exists before saving the updated status.
def update_inquiry_status(inquiry_id, new_status):
    records = load_data()
    inquiry = find_record(records["inquiries"], "inquiry_id", inquiry_id)
    if inquiry is None:
        raise ValueError("That inquiry could not be found.")
    inquiry["status"] = new_status
    save_data(records)