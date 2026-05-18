from app.core.config import Settings


def test_development_cors_allows_all_origins() -> None:
    settings = Settings(
        app_env="development",
        cors_origins="http://localhost:5173,http://localhost:8080",
        cors_allow_credentials=True,
    )

    assert settings.cors_origin_list == ["*"]
    assert settings.cors_allow_credentials_effective is False


def test_develop_alias_cors_allows_all_origins() -> None:
    settings = Settings(app_env="develop")

    assert settings.is_development is True
    assert settings.cors_origin_list == ["*"]


def test_publish_cors_uses_only_configured_origins() -> None:
    settings = Settings(
        app_env="publish",
        cors_origins="http://localhost:8080,https://example.com",
        cors_allow_credentials=True,
    )

    assert settings.is_publish is True
    assert settings.cors_origin_list == [
        "http://localhost:8080",
        "https://example.com",
    ]
    assert settings.cors_allow_credentials_effective is True


def test_publish_cors_ignores_empty_origins() -> None:
    settings = Settings(
        app_env="publish",
        cors_origins="http://localhost:8080, , https://example.com,",
    )

    assert settings.cors_origin_list == [
        "http://localhost:8080",
        "https://example.com",
    ]
