from scripts import build_report as br


def test_missing_sections_become_todo(tmp_path):
    (tmp_path / "01_data.md").write_text("# Section 1: Data\n\nHello.\n")
    texts, missing = br.collect_sections(tmp_path)

    assert len(texts) == len(br.SECTIONS)
    assert texts[0].startswith("# Section 1: Data")
    assert "01_data.md" not in missing
    assert "02_mandate_portfolio.md" in missing
    assert "TODO" in texts[1]


def test_empty_file_counts_as_missing(tmp_path):
    (tmp_path / "01_data.md").write_text("  \n")
    _, missing = br.collect_sections(tmp_path)
    assert "01_data.md" in missing


def test_table_rules_are_not_words():
    assert br.count_words("| a | b |\n|---|---|\n| 1 | 2 |") == 4


def test_page_limits():
    assert br.check_pages(7)
    assert br.check_pages(15)
    assert not br.check_pages(6.9)
    assert not br.check_pages(16)


def test_title_page_lists_team():
    page = br.title_page(br.date(2026, 10, 31))
    assert "Team Nexora" in page
    assert all(name in page for name in br.MEMBERS)
    assert "31 October 2026" in page
