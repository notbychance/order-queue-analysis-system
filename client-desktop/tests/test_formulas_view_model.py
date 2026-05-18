from __future__ import annotations

import pytest

from app.api.errors import QueueApiConnectionError
from app.schemas.queue import QueueFormulasResponse
from app.viewmodels.formulas_view_model import FormulasViewModel


def make_formulas_response() -> QueueFormulasResponse:
    return QueueFormulasResponse(
        model_name="M/M/1",
        description="Одноканальная система массового обслуживания.",
        stability_condition="λ < μ",
        formulas={
            "utilization": "ρ = λ / μ",
            "average_orders_in_system": "L = λ / (μ - λ)",
            "average_waiting_time": "Wq = λ / (μ × (μ - λ))",
            "average_time_in_system": "W = 1 / (μ - λ)",
        },
    )


class FakeApiClient:
    def __init__(self, response: QueueFormulasResponse | None = None) -> None:
        self.response = response or make_formulas_response()
        self.called = False
        self.raise_connection_error = False

    def get_formulas(self) -> QueueFormulasResponse:
        self.called = True

        if self.raise_connection_error:
            raise QueueApiConnectionError("connection failed")

        return self.response


@pytest.mark.unit
@pytest.mark.ui
def test_formulas_view_model_has_default_values():
    view_model = FormulasViewModel(FakeApiClient())

    assert view_model.modelName == "M/M/1"
    assert view_model.stabilityCondition == "λ < μ"
    assert len(view_model.formulaItems) == 4


@pytest.mark.unit
@pytest.mark.ui
def test_load_formulas_updates_properties():
    api_client = FakeApiClient(
        QueueFormulasResponse(
            model_name="M/M/1",
            description="Описание с сервера.",
            stability_condition="lambda < mu",
            formulas={
                "utilization": "rho = lambda / mu",
                "custom": "custom formula",
            },
        )
    )
    view_model = FormulasViewModel(api_client)

    view_model.loadFormulas()

    assert api_client.called is True
    assert view_model.errorMessage == ""
    assert view_model.modelName == "M/M/1"
    assert view_model.description == "Описание с сервера."
    assert view_model.stabilityCondition == "lambda < mu"

    formulas = view_model.formulaItems
    assert formulas[0]["key"] == "utilization"
    assert formulas[0]["formula"] == "rho = lambda / mu"
    assert formulas[1]["key"] == "custom"
    assert formulas[1]["formula"] == "custom formula"


@pytest.mark.unit
@pytest.mark.ui
def test_load_formulas_handles_connection_error():
    api_client = FakeApiClient()
    api_client.raise_connection_error = True
    view_model = FormulasViewModel(api_client)

    view_model.loadFormulas()

    assert "Не удалось подключиться" in view_model.errorMessage


@pytest.mark.unit
@pytest.mark.ui
def test_formula_items_are_returned_in_preferred_order():
    view_model = FormulasViewModel(
        FakeApiClient(
            QueueFormulasResponse(
                model_name="M/M/1",
                description="Описание.",
                stability_condition="λ < μ",
                formulas={
                    "average_time_in_system": "W = 1 / (μ - λ)",
                    "utilization": "ρ = λ / μ",
                    "average_waiting_time": "Wq = λ / (μ × (μ - λ))",
                    "average_orders_in_system": "L = λ / (μ - λ)",
                },
            )
        )
    )

    view_model.loadFormulas()

    keys = [item["key"] for item in view_model.formulaItems]

    assert keys == [
        "utilization",
        "average_orders_in_system",
        "average_waiting_time",
        "average_time_in_system",
    ]
