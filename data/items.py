from .store import load_data, save_data, next_id, find_record, format_record_id


def add_item(data):
    records = load_data()
    item = dict(data)
    item.update(item_id=next_id(records["items"], "item_id"), status="Unclaimed")
    records["items"].append(item)
    save_data(records)


def update_item(item_id, data):
    records = load_data()
    item = find_record(records["items"], "item_id", item_id)
    if item is None:
        raise ValueError("That item could not be found.")
    status = item["status"]
    item.update(data)
    item["status"] = status
    save_data(records)


def _filter_items(items, search, category="All"):
    if category != "All":
        items = [item for item in items if item.get("category") == category]
    if search:
        term = search.casefold()
        fields = ("item_name", "subcategory", "description", "color", "brand", "location_found", "finder_name")
        items = [item for item in items if term in format_record_id("ITM", item.get("date_found"), item["item_id"]).casefold() or any(term in str(item.get(field, "")).casefold() for field in fields)]
    return items


def get_items(search="", category="All"):
    records = load_data()["items"]
    records = _filter_items(records, search, category)
    return sorted(records, key=lambda item: item["item_id"], reverse=True)


def get_item_by_id(item_id):
    return find_record(load_data()["items"], "item_id", item_id)


def get_unclaimed_items():
    items = [item for item in load_data()["items"] if item.get("status") == "Unclaimed"]
    return sorted(({key: item.get(key, "") for key in ("item_id", "item_name", "category", "date_found")} for item in items),
                  key=lambda item: item["item_name"].casefold())
