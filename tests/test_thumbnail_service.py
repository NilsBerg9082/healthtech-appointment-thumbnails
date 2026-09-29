from src.thumbnail_service import choose_notification


def test_large_source_is_ready_for_patient_review() -> None:
    result = choose_notification(1600, 1000)
    assert result.status == "ready"
    assert result.message == "The appointment image is ready for review."


def test_invalid_dimensions_are_rejected_before_processing() -> None:
    assert choose_notification(0, 400).status == "rejected"
