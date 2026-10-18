from guard.cost_guard import Action, PaymentBlockedError, assert_allowed, check_action


def test_allows_clean_action():
    result = check_action(Action(provider_id="grok", description="generate clip"))
    assert result.allowed
    assert result.status == "OK"


def test_blocks_on_payment_signal_in_text():
    result = check_action(
        Action(
            provider_id="some_provider",
            description="generate clip",
            observed_text="Please add a credit card to continue.",
        )
    )
    assert not result.allowed
    assert result.status == "PAYMENT_BLOCKED"


def test_blocks_on_explicit_flag_even_with_existing_subscription():
    result = check_action(
        Action(
            provider_id="grok",
            description="generate clip",
            flags={"requires_payment"},
            existing_subscription=True,
        )
    )
    assert not result.allowed, "existing_subscription darf ein Zahlungssignal nie aufheben"


def test_blocks_on_auto_renew_hint():
    result = check_action(
        Action(
            provider_id="elevenlabs",
            description="check quota",
            observed_text="Ihr Abo wird automatisch verlängert am 1.1.",
        )
    )
    assert result.status == "PAYMENT_BLOCKED"


def test_assert_allowed_raises():
    action = Action(provider_id="x", description="y", observed_text="Buy credits now")
    try:
        assert_allowed(action)
        assert False, "sollte PaymentBlockedError werfen"
    except PaymentBlockedError:
        pass
