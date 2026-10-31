from data.store import load_data


def _dashboard_counts(records):
    items, inquiries = records["items"], records["inquiries"]                           # Gets the dashboard counts to use for the report
    return {
        "total_items": len(items),                                                      # Counts the total number of found items
        "unclaimed_items": sum(item.get("status") == "Unclaimed" for item in items),   
        "claimed_items": sum(item.get("status") == "Claimed" for item in items),        # Counts all items that have already been claimed
    }
def _report_counts(records):    
    counts = _dashboard_counts(records)                                               
    inquiries, claims = records["inquiries"], records["claims"]                         # Gets all inquiries and claims from the saved records
    counts.update(                                                                      # Adds more information to the existing dashboard counts
        open_inquiries=sum(item.get("status") == "Open" for item in inquiries),         # Counts all inquiries that are still open
        resolved_inquiries=sum(item.get("status") == "Resolved" for item in inquiries), # Counts all inquiries that have been resolved
        total_claims=len(claims),                                                       # Counts the total number of recorded claims
        pending_releases=sum(not claim.get("release_date") for claim in claims),        # Counts claims that have not been released yet
        released_claims=sum(bool(claim.get("release_date")) for claim in claims),       # Counts claims that have already been released
    )   
    return counts                                                                       # Returns all the collected report counts


def _category_summary(items):
    summary = {}                                                                        # Creates an empty dictionary to store the item category summary
    for item in items:                                                                  # Goes through each item in the list
        category = item.get("category", "")                                             # Gets the category of the current item
        if category not in summary:                                                     
            summary[category] = {"category": category, "total": 0, "unclaimed": 0, "claimed": 0}
        summary[category]["total"] += 1                                                 # Adds one to the total number of items in that category
        status = item.get("status", "")                                                 # Gets the current item's status
        if status in ("Unclaimed", "Claimed"):                                          # Checks if the item's status is either Unclaimed or Claimed    
            summary[category][status.lower()] += 1                                      # Adds one to the matching status count             
    return [summary[key] for key in sorted(summary)]                                    # Returns the category summary arranged alphabetically

def get_report_summary():
    records = load_data()                                                               # Loads all saved records from the database
    return _report_counts(records), _category_summary(records["items"])                 # Returns the report counts and item category summary            

def get_dashboard_counts():
    return _dashboard_counts(load_data())                                               # Loads the saved records and gets the dashboard statistics


