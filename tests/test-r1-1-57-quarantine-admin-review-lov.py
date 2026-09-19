from pathlib import Path
from app import quarantine


def _rows(admin_decision="all"):
    original = quarantine.cache
    try:
        quarantine.cache = {
            "data": [
                {"pdp_id":"required","from":"a@example","to":"u@example","subject":"p","date":"2026-09-16","category":"Spam","from_domain":"example","is_released":False,"is_manual_spam":False,"learning":""},
                {"pdp_id":"completed","from":"b@example","to":"u@example","subject":"c","date":"2026-09-16","category":"Spam","from_domain":"example","is_released":False,"is_manual_spam":True,"learning":"spam"},
            ],
            "last_updated":"now","error":"","scan_stats":{},
        }
        result = quarantine.query_items(admin_decision=admin_decision, decided_pdp_ids={"completed"}, page_size=20)
        return [x["pdp_id"] for x in result["items"]]
    finally:
        quarantine.cache = original


def test_admin_review_filter_semantics():
    assert _rows("all") == ["required", "completed"]
    assert _rows("required") == ["required"]
    assert _rows("completed") == ["completed"]


def test_ui_realignment_and_removed_duplicate_controls():
    main = (Path(__file__).resolve().parents[1] / "app" / "main.py").read_text(encoding="utf-8")
    assert '<label>Learning Mark</label>' in main
    assert '<label>Admin Review Queue</label>' in main
    assert main.index('<label>Learning Mark</label>') < main.index('<label>Admin Review Queue</label>')
    assert 'qreview-metric' not in main
    assert 'qReviewRequired' not in main
    assert 'Review Pending Messages' not in main
    assert 'openRequiredReviewQueue' not in main
    assert 'Admin Decision Required / Review Now' not in main
    assert 'R1.1.57 Admin Review Queue Filter' in main
