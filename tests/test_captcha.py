from sbt_bot.utils.captcha import CAPTCHA_ITEMS, generate_captcha


def test_generate_captcha_returns_known_item() -> None:
    codes = {item.code for item in CAPTCHA_ITEMS}
    labels = {item.label for item in CAPTCHA_ITEMS}
    for _ in range(20):
        challenge = generate_captcha()
        assert challenge.expected_code in codes
        assert challenge.prompt_label in labels
