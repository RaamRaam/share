def step(msg):
    print(f"\n► {msg}")


def click_button_ci(page, texts):
    """Click first visible button matching any text (case-insensitive)."""
    for t in texts:
        el = page.locator(
            f"xpath=//*[translate(normalize-space(text()),"
            f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='{t.lower()}']"
        )
        if el.count():
            el.first.click()
            return True
    return False
