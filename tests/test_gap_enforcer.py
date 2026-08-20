from divergence.gap_enforcer import FORCED_CERTAINTY, enforce


def test_enforce_forces_only_regimes_with_missing_dependencies():
    record = {
        "regimes": [
            {
                "regime": "gst_export",
                "certainty": "settled",
                "depends_on_missing": ["FIRC"],
            },
            {
                "regime": "income_tax_on_receipt",
                "certainty": "inference",
                "depends_on_missing": [],
            },
        ]
    }

    updated, forced = enforce(record)

    assert updated["regimes"][0]["certainty"] == FORCED_CERTAINTY
    assert updated["regimes"][1]["certainty"] == "inference"
    assert forced == [
        {
            "regime": "gst_export",
            "was": "settled",
            "depends_on_missing": ["FIRC"],
        }
    ]
