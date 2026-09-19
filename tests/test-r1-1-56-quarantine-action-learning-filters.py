from pathlib import Path

from app import quarantine


def _rows(action_state="all", learning_mark="all"):
    original = quarantine.cache
    try:
        quarantine.cache = {
            "data": [
                {"pdp_id":"pending","from":"a@example","to":"u@example","subject":"p","date":"2026-09-12","category":"Spam","from_domain":"example","is_released":False,"is_manual_spam":False,"learning":""},
                {"pdp_id":"releaseham","from":"a@example","to":"u@example","subject":"h","date":"2026-09-12","category":"Spam","from_domain":"example","is_released":True,"is_manual_spam":False,"learning":"ham"},
                {"pdp_id":"markspam","from":"a@example","to":"u@example","subject":"s","date":"2026-09-12","category":"Spam","from_domain":"example","is_released":False,"is_manual_spam":True,"learning":"spam"},
                {"pdp_id":"learnhamonly","from":"a@example","to":"u@example","subject":"lh","date":"2026-09-12","category":"Spam","from_domain":"example","is_released":False,"is_manual_spam":False,"learning":"ham"},
            ],
            "last_updated":"now","error":"","scan_stats":{},
        }
        result = quarantine.query_items(action_state=action_state, learning_mark=learning_mark, page_size=20)
        return [x["pdp_id"] for x in result["items"]]
    finally:
        quarantine.cache = original


def test_action_filter_semantics():
    assert _rows(action_state="pending") == ["pending", "learnhamonly"]
    assert _rows(action_state="release_ham") == ["releaseham"]
    assert _rows(action_state="mark_spam") == ["markspam"]


def test_learning_filter_semantics():
    assert _rows(learning_mark="unmarked") == ["pending"]
    assert _rows(learning_mark="ham") == ["releaseham", "learnhamonly"]
    assert _rows(learning_mark="spam") == ["markspam"]


def test_combined_untouched_backlog():
    assert _rows(action_state="pending", learning_mark="unmarked") == ["pending"]


def test_ui_and_help_present():
    main = (Path(__file__).resolve().parents[1] / "app" / "main.py").read_text(encoding="utf-8")
    assert 'id="qActionState"' in main
    assert 'Pending Action' in main
    assert 'id="qLearningMark"' in main
    assert 'Unmarked HAM/SPAM' in main
    assert 'R1.1.56 Quarantine Action & Learning LOV Filters' in main
    assert '<label>Admin Review Queue</label>' in main
