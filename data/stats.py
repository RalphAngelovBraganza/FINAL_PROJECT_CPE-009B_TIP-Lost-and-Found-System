from data.store import load_data


def _dashboard_counts(records):
    items, inquiries = records["items"], records["inquiries"]
    return {
        "total_items": len(items),
        "unclaimed_items": sum(item.get("status") == "Unclaimed" for item in items),
        "claimed_items": sum(item.get("status") == "Claimed" for item in items),
        "total_inquiries": len(inquiries),
    }


def _report_counts(records):
    counts = _dashboard_counts(records)
    inquiries, claims = records["inquiries"], records["claims"]
    counts.update(
        open_inquiries=sum(item.get("status") == "Open" for item in inquiries),
        resolved_inquiries=sum(item.get("status") == "Resolved" for item in inquiries),
        total_claims=len(claims),
        pending_releases=sum(not claim.get("release_date") for claim in claims),
        released_claims=sum(bool(claim.get("release_date")) for claim in claims),
    )
    return counts


def _category_summary(items):
    summary = {}
    for item in items:
        category = item.get("category", "")
        if category not in summary:
            summary[category] = {"category": category, "total": 0, "unclaimed": 0, "claimed": 0}
        summary[category]["total"] += 1
        status = item.get("status", "")
        if status in ("Unclaimed", "Claimed"):
            summary[category][status.lower()] += 1
    return [summary[key] for key in sorted(summary)]


def get_dashboard_counts():
    return _dashboard_counts(load_data())


def get_report_summary():
    records = load_data()
    return _report_counts(records), _category_summary(records["items"])
