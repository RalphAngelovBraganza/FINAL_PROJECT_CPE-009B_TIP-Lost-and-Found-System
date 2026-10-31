from data.store import load_data, save_data, next_id, find_record, format_record_id


def add_claim(item_id, claimant_name, contact_info, date_claimed, verification_notes):
    records = load_data()
    item = find_record(records["items"], "item_id", item_id)
    if item is None or item.get("status") != "Unclaimed":
        raise ValueError("This item is not available for claiming (it may already be claimed).")
    claim = {
        "claim_id": next_id(records["claims"], "claim_id"), "item_id": item_id,
        "claimant_name": claimant_name, "contact_info": contact_info,
        "date_claimed": date_claimed, "verification_notes": verification_notes,
        "release_date": "", "released_by": "",
    }
    item["status"] = "Claimed"
    records["claims"].append(claim)
    save_data(records)


def _filter_claims(claims, search):
    if not search:
        return claims
    term = search.casefold()
    fields = ("claimant_name", "contact_info", "item_name", "released_by")
    return [claim for claim in claims if term in format_record_id("CLM", claim.get("date_claimed"), claim["claim_id"]).casefold() or any(term in str(claim.get(field, "")).casefold() for field in fields)]


def get_claims(search=""):
    records = load_data()
    items = {item["item_id"]: item for item in records["items"]}
    claims = []
    for claim in records["claims"]:
        item = items.get(claim["item_id"])
        if item is None:
            continue
        result = dict(
            claim,
            item_name=item.get("item_name", ""),
            item_date_found=item.get("date_found", ""),
        )
        claims.append(result)
    claims = _filter_claims(claims, search)
    return sorted(claims, key=lambda claim: claim["claim_id"], reverse=True)


def release_claim(claim_id, release_date, released_by):
    records = load_data()
    claim = find_record(records["claims"], "claim_id", claim_id)
    if claim is None or claim.get("release_date"):
        return 0
    claim.update(release_date=release_date, released_by=released_by)
    save_data(records)
    return 1


def cancel_claim(claim_id):
    records = load_data()
    claim = find_record(records["claims"], "claim_id", claim_id)
    if claim is None:
        raise ValueError("That claim record could not be found.")
    if claim.get("release_date"):
        raise ValueError("This item was already released, so the claim cannot be cancelled.")
    item = find_record(records["items"], "item_id", claim["item_id"])
    if item:
        item["status"] = "Unclaimed"
    records["claims"].remove(claim)
    save_data(records)
