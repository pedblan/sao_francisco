from sao_francisco import credentials


def test_status_never_returns_secret(monkeypatch) -> None:
    monkeypatch.setattr(credentials, "_read_native", lambda _account: "super-secret")
    monkeypatch.setattr(credentials, "secure_store_available", lambda: True)

    status = credentials.credential_status("openai")

    assert status["configured"] is True
    assert "super-secret" not in repr(status)
    assert set(status) == {
        "provider",
        "name",
        "configured",
        "source",
        "storeAvailable",
        "storeLabel",
    }
