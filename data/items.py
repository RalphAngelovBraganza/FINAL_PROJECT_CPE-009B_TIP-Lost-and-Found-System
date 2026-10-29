from data.store import load_data, save_data, next_id, find_record, format_record_id  # Imports functions for loading, saving, finding, and formatting records.


def add_item(data):  # Defines the function for adding a new item.
    records = load_data()  # Loads the existing records.
    item = dict(data)  # Copies the new item's information into a dictionary.
    item.update(item_id=next_id(records["items"], "item_id"), status="Unclaimed")  # Assigns a new ID and sets the status to Unclaimed.
    records["items"].append(item)  # Adds the new item to the list of items.
    save_data(records)  # Saves the updated records.


def update_item(item_id, data):  # Defines the function for updating an existing item.
    records = load_data()  # Loads the existing records.
    item = find_record(records["items"], "item_id", item_id)  # Finds the item using its ID.
    if item is None:  # Checks if the item does not exist.
        raise ValueError("That item could not be found.")  # Shows an error if the item is missing.
    status = item["status"]  # Keeps the item's current status.
    item.update(data)  # Updates the item's information.
    item["status"] = status  # Restores the original status so it does not change.
    save_data(records)  # Saves the updated records.


def _filter_items(items, search, category="All"):  # Defines the function for filtering items.
    if category != "All":  # Checks if a specific category was selected.
        items = [item for item in items if item.get("category") == category]  # Keeps only items in that category.
    if search:  # Checks if the user entered a search keyword.
        term = search.casefold()  # Converts the keyword to lowercase for easier matching.
        fields = ("item_name", "subcategory", "description", "color", "brand", "location_found", "finder_name")  # Lists the item details to search.
        items = [item for item in items  # Keeps items that match the search keyword.
                 if term in format_record_id("ITM", item.get("date_found"), item["item_id"]).casefold()  # Checks if the keyword matches the formatted item ID.
                 or any(term in str(item.get(field, "")).casefold() for field in fields)]  # Checks if the keyword matches any listed item detail.
    return items  # Returns the filtered list of items.


def get_items(search="", category="All"):  # Defines the function for retrieving items.
    records = load_data()["items"]  # Loads the records and gets the list of items.
    records = _filter_items(records, search, category)  # Filters the items using the search and category.
    return sorted(records, key=lambda item: item["item_id"], reverse=True)  # Returns the items sorted by ID from newest to oldest.