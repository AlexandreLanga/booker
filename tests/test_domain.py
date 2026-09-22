from domain.entities import ReadingProgress


def test_progress_percentage_rounds_to_one_decimal():
    progress = ReadingProgress(book_id=1, current_page=4)

    assert progress.percentage(total_pages=10) == 50.0


def test_progress_percentage_with_zero_total_pages_is_zero():
    progress = ReadingProgress(book_id=1, current_page=0)

    assert progress.percentage(total_pages=0) == 0.0
