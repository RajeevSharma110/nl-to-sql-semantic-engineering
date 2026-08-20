from nl_sql.models import TrustEvidence


def test_low_confidence_requires_clarification():
    evidence = TrustEvidence(0.2, 0.2, 0.0, 0.0, 0.8, 0.5)
    assert evidence.decision == "clarify"


def test_high_confidence_executes():
    evidence = TrustEvidence(1, 1, 1, 1, 0, 1)
    assert evidence.score == 1
    assert evidence.decision == "execute"

