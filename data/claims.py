from data.store import load_data, save_data, next_id, find_record, format_record_id


def add_claim(item_id, claimant_name, contact_info, date_claimed, verification_notes):
    records = load_data()                                                  # Loads all saved items, inquiries and claims from the database.
    item = find_record(records["items"], "item_id", item_id)               # Searches for the item using its item ID
    if item is None or item.get("status") != "Unclaimed":                  # Checks the item if it exist and if it's still available for claiming
        raise ValueError("This item is not available for claiming (it may already be claimed).")
    claim = {                                                              #Creates new claim record that contains the claimant's information                                  
        "claim_id": next_id(records["claims"], "claim_id"), "item_id": item_id,
        "claimant_name": claimant_name, "contact_info": contact_info,
        "date_claimed": date_claimed, "verification_notes": verification_notes,
        "release_date": "", "released_by": "",
    }
    item["status"] = "Claimed"                                             # Changes the item's status to Claimed
    records["claims"].append(claim)                                        # Adds the new claim to the claims list
    save_data(records)                                                     # Saves the updated records to the database


def _filter_claims(claims, search):
    if not search:                                                         # Returns all claims if the search field is empty
        return claims                                                       
    term = search.casefold()                                               # Converts the search text to lowercase for easier comparison
    fields = ("claimant_name", "contact_info", "item_name", "released_by") # Specifies the claim information that can be searched
    return [claim for claim in claims if term in format_record_id("CLM", claim.get("date_claimed"), claim["claim_id"]).casefold() or any(term in str(claim.get(field, "")).casefold() for field in fields)]     # Returns to the claims that matches the search text


def get_claims(search=""):
    records = load_data()                                                  
    claims = []                                                            # Creates an empty list to store the retrieved claims
    for claim in records["claims"]:                                        # Goes through each claim record in the database
        item = records["items"].get(claim["item_id"])                      # Finds the item connected to the current claim
        if item is None:                                                   # Skips the claim if its associated item cannot be found.
            continue
        result = dict(                                                     # Copies the claim information and adds the item's name and the date when it wasfound
            claim,
            item_name=item.get("item_name", ""),
            item_date_found=item.get("date_found", ""),
        )
        claims.append(result)                                              # Adds the claim to the list of retrieved claims    
    claims = _filter_claims(claims, search)                                # Filters the claims based on the search text
    return sorted(claims, key=lambda claim: claim["claim_id"], reverse=True) # Sorts claims by ID in descending order, showing newer records first

def cancel_claim(claim_id):
    records = load_data()
    claim = find_record(records["claims"], "claim_id", claim_id)           # Checks if the claim record exists
    if claim is None:                                                           
        raise ValueError("That claim record could not be found.")
    if claim.get("release_date"):                                          # Prevents cancellation if the item has already been released
        raise ValueError("This item was already released, so the claim cannot be cancelled.")
    item = find_record(records["items"], "item_id", claim["item_id"])      # Finds the item that is associated with the claim
    if item:                                                               # Changes the item's status back to Unclaimed if the item exists
        item["status"] = "Unclaimed"
    records["claims"].remove(claim)                                        # Removes the cancelled claim from the claims list
    save_data(records)                                                     # Saves the updated records to the database

def release_claim(claim_id, release_date, released_by):
    records = load_data()                                                  
    claim = find_record(records["claims"], "claim_id", claim_id)           # Searches for the claim using its claim ID
    if claim is None or claim.get("release_date"):                         # Checks if the claim exists or has already been released
        return 0
    claim.update(release_date=release_date, released_by=released_by)       # Updates the claim with its release date and the name of the person who released it
    save_data(records)                                                     # Saves the updated claim information
    return 1                                                               # Returns 1 to indicate that the claim was successfully released


