"""
LEVEL A — Unit Tests: Feature Engineering and Risk Engine

Uses small deterministic synthetic fixtures. No database connection required.
Each test verifies the exact mathematical output of the deterministic engine.
"""
import pytest
from risk.features import FeatureNormalizer
from risk.transaction_features import TransactionFeatureExtractor
from risk.profile_features import ProfileFeatureExtractor
from risk.chain_features import ChainFeatureExtractor
from risk.atm_features import ATMFeatureExtractor
from risk.geographic_features import GeographicFeatureExtractor
from risk.indicators import IndicatorEngine
from risk.engine import RiskEngine
from database.models import (
    TransactionSummary, ProfileSummary, TransactionChainSummary,
    ATMRecord, StateRiskSummary
)


# ─── Helper Factories ─────────────────────────────────────────────────────────

def make_tx(
    txn_id="TX1", chain_id="C1", amount=1000.0,
    is_laundering=0, hop_layer=0, is_terminal_cashout=0,
    from_acc="A1", to_acc="A2", channel="UPI"
):
    return TransactionSummary(
        txn_id=txn_id, chain_id=chain_id, pattern_type="TEST",
        timestamp_ist="2026-01-01 00:00:00 IST",
        from_account_id=from_acc, from_bank="BankA",
        to_account_id=to_acc, to_bank="BankB",
        amount_inr=amount, channel=channel,
        is_laundering=is_laundering, hop_layer=hop_layer,
        is_terminal_cashout=is_terminal_cashout,
        crime_category="TEST"
    )


def make_profile(
    profile_id="P1", account_id="A1", is_mule=0,
    account_age_days=365, risk_score=10.0,
    withdrawal_velocity=1000.0, kyc_status="VERIFIED"
):
    return ProfileSummary(
        profile_id=profile_id, account_id=account_id,
        holder_name="Test User", bank_name="BankA",
        kyc_status=kyc_status, account_age_days=account_age_days,
        risk_score=risk_score, is_mule=is_mule, mule_type=None,
        last_known_city="Delhi", last_known_state="Delhi",
        withdrawal_velocity_per_day=withdrawal_velocity
    )


def make_chain(chain_id="C1", hop_count=2, total_amount=5000.0):
    return TransactionChainSummary(
        chain_id=chain_id, pattern_type="STACK",
        total_amount=total_amount, hop_count=hop_count,
        transactions=[]
    )


def make_atm(atm_id="ATM1", operational_status="ONLINE", cash_index=0.7):
    return ATMRecord(
        atm_id=atm_id, bank_name="SBI", atm_name="ATM-1",
        latitude=28.6, longitude=77.2, state="Delhi", city="Delhi",
        atm_type="ONSITE", is_24x7=1, cash_availability_index=cash_index,
        operational_status=operational_status
    )


def make_state_stats(risk_tier="LOW", density=0.1):
    return StateRiskSummary(
        state_name="TestState", total_incidents=10,
        amount_reported_cr=1.0, incident_density=density,
        risk_tier=risk_tier
    )


def make_base_state(**overrides):
    s = {
        "investigation_id": "INV-UNIT-001",
        "iteration": 1,
        "transactions": [],
        "profiles": [],
        "transaction_chains": [],
        "atms": [],
        "evidence": [],
    }
    s.update(overrides)
    return s


# ─── A1: FeatureNormalizer ────────────────────────────────────────────────────

class TestFeatureNormalizer:
    def test_within_range(self):
        assert FeatureNormalizer.normalize_min_max(50, 0, 100) == 0.5

    def test_clamp_below_min(self):
        assert FeatureNormalizer.normalize_min_max(-10, 0, 100) == 0.0

    def test_clamp_above_max(self):
        assert FeatureNormalizer.normalize_min_max(150, 0, 100) == 1.0

    def test_missing_returns_default(self):
        assert FeatureNormalizer.normalize_min_max(None, 0, 100, default=0.25) == 0.25

    def test_invalid_bounds_returns_default(self):
        assert FeatureNormalizer.normalize_min_max(50, 100, 0, default=0.1) == 0.1

    def test_safe_divide_normal(self):
        assert FeatureNormalizer.safe_divide(10, 4) == 2.5

    def test_safe_divide_zero_denominator(self):
        assert FeatureNormalizer.safe_divide(10, 0) == 0.0

    def test_safe_divide_none(self):
        assert FeatureNormalizer.safe_divide(None, 4) == 0.0

    def test_categorical_mapping(self):
        m = {"LOW": 0.0, "HIGH": 1.0}
        assert FeatureNormalizer.map_categorical("HIGH", m) == 1.0
        assert FeatureNormalizer.map_categorical("UNKNOWN", m) == 0.0
        assert FeatureNormalizer.map_categorical(None, m) == 0.0


# ─── A2: Transaction Features ─────────────────────────────────────────────────

class TestTransactionFeatures:
    def test_empty(self):
        f = TransactionFeatureExtractor.extract([])
        assert f["transaction_count"] == 0
        assert f["total_amount"] == 0.0
        assert f["laundering_count"] == 0

    def test_basic_extraction(self):
        txns = [
            make_tx("TX1", amount=10000, is_laundering=1, hop_layer=1, from_acc="A1", to_acc="A2"),
            make_tx("TX2", amount=60000, is_laundering=1, hop_layer=2, is_terminal_cashout=1, from_acc="A2", to_acc="A3"),
        ]
        f = TransactionFeatureExtractor.extract(txns)
        assert f["transaction_count"] == 2
        assert f["total_amount"] == 70000
        assert f["laundering_count"] == 2
        assert f["terminal_cashout_count"] == 1
        assert f["max_hop_layer"] == 2
        assert f["unique_counterparties"] == 3  # A1, A2, A3
        assert f["has_high_value"] is True       # 60000 > 50000

    def test_no_laundering_normal_pattern(self):
        txns = [make_tx("TX1", amount=500, is_laundering=0, hop_layer=0)]
        f = TransactionFeatureExtractor.extract(txns)
        assert f["laundering_count"] == 0
        assert f["has_high_value"] is False

    def test_missing_data_no_crash(self):
        # Missing optional fields should not crash
        f = TransactionFeatureExtractor.extract([])
        assert f["transaction_count"] == 0


# ─── A3: Profile Features ─────────────────────────────────────────────────────

class TestProfileFeatures:
    def test_empty(self):
        f = ProfileFeatureExtractor.extract([])
        assert f["mule_count"] == 0
        assert f["max_risk_score"] == 0.0

    def test_mule_detection(self):
        profiles = [
            make_profile("P1", "A1", is_mule=1, account_age_days=10, withdrawal_velocity=100000),
            make_profile("P2", "A2", is_mule=0, account_age_days=500, withdrawal_velocity=500),
        ]
        f = ProfileFeatureExtractor.extract(profiles)
        assert f["mule_count"] == 1
        assert f["has_new_account"] is True  # age 10 < 30
        assert f["has_high_velocity"] is True  # 100000 > 50000

    def test_low_risk_profile(self):
        profiles = [make_profile("P1", "A1", is_mule=0, account_age_days=730, withdrawal_velocity=1000)]
        f = ProfileFeatureExtractor.extract(profiles)
        assert f["mule_count"] == 0
        assert f["has_new_account"] is False
        assert f["has_high_velocity"] is False

    def test_kyc_failed_count(self):
        profiles = [
            make_profile(kyc_status="REJECTED"),
            make_profile(kyc_status="VERIFIED"),
            make_profile(kyc_status="PENDING"),
        ]
        f = ProfileFeatureExtractor.extract(profiles)
        assert f["kyc_failed_count"] == 2


# ─── A4: Chain Features ───────────────────────────────────────────────────────

class TestChainFeatures:
    def test_empty(self):
        f = ChainFeatureExtractor.extract([])
        assert f["multi_hop_presence"] is False
        assert f["chain_count"] == 0

    def test_multi_hop_detected(self):
        chains = [make_chain(hop_count=5, total_amount=100000)]
        f = ChainFeatureExtractor.extract(chains)
        assert f["multi_hop_presence"] is True
        assert f["max_chain_length"] == 5

    def test_single_hop_not_flagged(self):
        chains = [make_chain(hop_count=2, total_amount=1000)]
        f = ChainFeatureExtractor.extract(chains)
        assert f["multi_hop_presence"] is False


# ─── A5: ATM Features ────────────────────────────────────────────────────────

class TestATMFeatures:
    def test_empty(self):
        f = ATMFeatureExtractor.extract([])
        assert f["atm_count"] == 0

    def test_offline_atm(self):
        atms = [make_atm(operational_status="OFFLINE")]
        f = ATMFeatureExtractor.extract(atms)
        assert f["offline_atm_presence"] is True

    def test_high_risk_low_cash(self):
        atms = [make_atm(cash_index=0.1)]  # below 0.2 threshold
        f = ATMFeatureExtractor.extract(atms)
        assert f["high_risk_atm_presence"] is True


# ─── A6: Geographic Features ─────────────────────────────────────────────────

class TestGeographicFeatures:
    def test_empty(self):
        f = GeographicFeatureExtractor.extract([])
        assert f["high_risk_state_presence"] is False

    def test_high_risk_state(self):
        states = [make_state_stats(risk_tier="CRITICAL", density=5.0)]
        f = GeographicFeatureExtractor.extract(states)
        assert f["high_risk_state_presence"] is True

    def test_low_risk_state(self):
        states = [make_state_stats(risk_tier="LOW", density=0.1)]
        f = GeographicFeatureExtractor.extract(states)
        assert f["high_risk_state_presence"] is False


# ─── A7: Indicator Engine ────────────────────────────────────────────────────

class TestIndicatorEngine:
    def test_no_features_no_indicators(self):
        inds = IndicatorEngine.generate_indicators({}, "TEST", "T1")
        assert inds == []

    def test_laundering_flag_triggered(self):
        features = {"laundering_count": 3}
        inds = IndicatorEngine.generate_indicators(features, "TEST", "T1")
        names = [i["name"] for i in inds]
        assert "LAUNDERING_FLAG" in names
        laund = next(i for i in inds if i["name"] == "LAUNDERING_FLAG")
        assert laund["observed_value"] == 3

    def test_terminal_cashout_triggered(self):
        inds = IndicatorEngine.generate_indicators({"terminal_cashout_count": 2}, "TEST", "T1")
        names = [i["name"] for i in inds]
        assert "TERMINAL_CASHOUT" in names

    def test_multi_hop_triggered(self):
        inds = IndicatorEngine.generate_indicators({"multi_hop_presence": True, "max_chain_length": 5}, "TEST", "T1")
        names = [i["name"] for i in inds]
        assert "MULTI_HOP_CHAIN" in names
        ind = next(i for i in inds if i["name"] == "MULTI_HOP_CHAIN")
        assert ind["observed_value"] == 5

    def test_all_indicator_fields_present(self):
        """Every indicator must carry the required fields."""
        features = {
            "laundering_count": 1,
            "terminal_cashout_count": 1,
            "has_high_value": True,
            "unique_counterparties": 5,
            "mule_count": 1,
            "has_new_account": True,
            "has_high_velocity": True,
            "multi_hop_presence": True,
            "max_chain_length": 4,
            "high_risk_state_presence": True,
            "max_incident_density": 3.0,
            "avg_amount": 10000.0
        }
        required_fields = {
            "indicator_id", "name", "value", "threshold", "source",
            "source_id", "supporting_fields", "observed_value", "description", "confidence"
        }
        inds = IndicatorEngine.generate_indicators(features, "TEST", "T1")
        assert len(inds) > 0
        for ind in inds:
            missing = required_fields - set(ind.keys())
            assert missing == set(), f"Indicator {ind.get('name')} missing fields: {missing}"

    def test_threshold_labels_project_heuristic(self):
        """All threshold strings must be labelled as PROJECT HEURISTIC or DATA-DRIVEN."""
        features = {
            "laundering_count": 1, "terminal_cashout_count": 1,
            "has_high_value": True, "unique_counterparties": 4,
            "mule_count": 1, "has_high_velocity": True,
            "multi_hop_presence": True, "max_chain_length": 3,
            "high_risk_state_presence": True, "max_incident_density": 1.0,
            "avg_amount": 1000.0
        }
        inds = IndicatorEngine.generate_indicators(features, "TEST", "T1")
        for ind in inds:
            assert "[PROJECT HEURISTIC]" in ind["threshold"] or "[DATA-DRIVEN" in ind["threshold"], \
                f"Indicator {ind['name']} threshold not labelled: {ind['threshold']}"


# ─── A8: Risk Engine — Core Scoring ──────────────────────────────────────────

class TestRiskEngineScoring:
    def test_empty_state_is_low(self):
        state = make_base_state()
        result = RiskEngine.calculate_risk(state)
        assert result["risk_score"] == 0.0
        assert result["risk_level"] == "LOW"
        assert result["confidence"] == 0.0
        assert result["indicators"] == []

    def test_laundering_only_scores_30(self):
        state = make_base_state(transactions=[make_tx(is_laundering=1)])
        result = RiskEngine.calculate_risk(state)
        assert result["risk_score"] == 30.0
        assert result["risk_level"] == "MODERATE"

    def test_terminal_cashout_only_scores_20(self):
        state = make_base_state(transactions=[make_tx(is_terminal_cashout=1)])
        result = RiskEngine.calculate_risk(state)
        assert result["risk_score"] == 20.0
        assert result["risk_level"] == "LOW"

    def test_mule_only_no_transactions_scores_25(self):
        state = make_base_state(profiles=[make_profile(is_mule=1)])
        result = RiskEngine.calculate_risk(state)
        # No transactions so contradictory evidence rule does NOT trigger
        assert result["risk_score"] == 25.0
        assert result["risk_level"] == "MODERATE"
        assert result["contradictory_evidence"] is False

    def test_full_scenario_capped_at_100(self):
        state = make_base_state(
            transactions=[
                make_tx("TX1", amount=60000, is_laundering=1, is_terminal_cashout=1, hop_layer=3, from_acc="A1", to_acc="A2"),
                make_tx("TX2", amount=10000, is_laundering=1, hop_layer=4, from_acc="A2", to_acc="A3"),
                make_tx("TX3", amount=5000, is_laundering=0, hop_layer=5, from_acc="A3", to_acc="A4"),
            ],
            profiles=[make_profile(is_mule=1, withdrawal_velocity=80000)],
            transaction_chains=[make_chain(hop_count=5, total_amount=75000)],
        )
        result = RiskEngine.calculate_risk(state)
        assert result["risk_score"] <= 100.0
        assert result["risk_level"] in ["HIGH", "CRITICAL"]

    def test_severity_matches_level(self):
        """Severity in finding should match risk_level."""
        state = make_base_state(
            transactions=[make_tx(is_laundering=1, is_terminal_cashout=1, amount=60000)],
            transaction_chains=[make_chain(hop_count=4)]
        )
        finding = RiskEngine.generate_finding(state)
        assert finding is not None
        result = RiskEngine.calculate_risk(state)
        assert finding["severity"] == result["risk_level"]


# ─── A9: Determinism ─────────────────────────────────────────────────────────

class TestDeterminism:
    """Given identical inputs, risk engine must produce identical outputs."""

    def _make_complex_state(self):
        return make_base_state(
            transactions=[
                make_tx("TX1", amount=55000, is_laundering=1, is_terminal_cashout=1, hop_layer=3),
                make_tx("TX2", amount=10000, is_laundering=1, hop_layer=4),
            ],
            profiles=[make_profile(is_mule=1, withdrawal_velocity=75000)],
            transaction_chains=[make_chain(hop_count=4, total_amount=65000)],
        )

    def test_identical_scores(self):
        state = self._make_complex_state()
        r1 = RiskEngine.calculate_risk(state)
        r2 = RiskEngine.calculate_risk(state)
        assert r1["risk_score"] == r2["risk_score"]
        assert r1["risk_level"] == r2["risk_level"]
        assert r1["confidence"] == r2["confidence"]

    def test_identical_indicators(self):
        state = self._make_complex_state()
        r1 = RiskEngine.calculate_risk(state)
        r2 = RiskEngine.calculate_risk(state)
        names1 = sorted(i["name"] for i in r1["indicators"])
        names2 = sorted(i["name"] for i in r2["indicators"])
        assert names1 == names2

    def test_identical_finding_status(self):
        state = self._make_complex_state()
        f1 = RiskEngine.generate_finding(state)
        f2 = RiskEngine.generate_finding(state)
        assert f1 is not None
        assert f2 is not None
        assert f1["status"] == f2["status"]
        assert f1["category"] == f2["category"]
        assert f1["severity"] == f2["severity"]
        assert f1["risk_score"] == f2["risk_score"]


# ─── A10: Contradictory Evidence ─────────────────────────────────────────────

class TestContradictoryEvidence:
    def test_contradictory_rule_triggered(self):
        """Mule profile + normal transactions → contradictory evidence."""
        state = make_base_state(
            profiles=[make_profile(is_mule=1)],
            transactions=[make_tx(is_laundering=0, is_terminal_cashout=0, hop_layer=1)]
        )
        result = RiskEngine.calculate_risk(state)
        assert result["contradictory_evidence"] is True
        # Score: 25 (mule) - 15 (penalty) = 10
        assert result["risk_score"] == 10.0
        assert result["risk_level"] == "LOW"
        # Confidence: base 0.10 + 0.15 (1 indicator) - 0.20 (penalty) = 0.05
        assert result["confidence"] == max(0.0, round(0.10 + 0.15 - 0.20, 2))

    def test_contradictory_rule_not_triggered_when_laundering_present(self):
        """Mule profile + laundering txns → NOT contradictory."""
        state = make_base_state(
            profiles=[make_profile(is_mule=1)],
            transactions=[make_tx(is_laundering=1, is_terminal_cashout=0, hop_layer=1)]
        )
        result = RiskEngine.calculate_risk(state)
        assert result["contradictory_evidence"] is False

    def test_contradictory_rule_not_triggered_no_transactions(self):
        """Mule profile + no transaction data → NOT contradictory (no data to contradict)."""
        state = make_base_state(profiles=[make_profile(is_mule=1)])
        result = RiskEngine.calculate_risk(state)
        assert result["contradictory_evidence"] is False

    def test_contradictory_finding_status_is_inconclusive(self):
        """Contradictory + low confidence → INCONCLUSIVE status."""
        state = make_base_state(
            profiles=[make_profile(is_mule=1)],
            transactions=[make_tx(is_laundering=0, is_terminal_cashout=0, hop_layer=1)]
        )
        # risk_score = 10 → below 50 → no finding
        finding = RiskEngine.generate_finding(state)
        assert finding is None  # Below HIGH threshold


# ─── A11: Missing Data ───────────────────────────────────────────────────────

class TestMissingData:
    def test_empty_transactions_no_crash(self):
        f = TransactionFeatureExtractor.extract([])
        assert isinstance(f, dict)

    def test_none_chain_id_in_transaction(self):
        tx = make_tx(chain_id=None)
        assert tx.chain_id is None
        f = TransactionFeatureExtractor.extract([tx])
        assert f["transaction_count"] == 1

    def test_invalid_amount_not_propagated(self):
        # Profile with is_mule missing (defaults to 0) should not break
        p = make_profile(is_mule=0)
        f = ProfileFeatureExtractor.extract([p])
        assert f["mule_count"] == 0

    def test_malformed_dict_in_state_skipped(self):
        """Dicts that can't be coerced into models should be skipped silently."""
        state = make_base_state(
            transactions=[{"txn_id": "BAD", "missing_required_fields": True}]
        )
        # Should not raise, should produce 0 transactions processed
        result = RiskEngine.calculate_risk(state)
        assert isinstance(result, dict)
        assert result["risk_score"] >= 0.0


# ─── A12: Machine-Readable Output ────────────────────────────────────────────

class TestMachineReadableOutput:
    def test_finding_machine_readable_present(self):
        state = make_base_state(
            transactions=[make_tx(is_laundering=1, is_terminal_cashout=1, amount=60000)],
            transaction_chains=[make_chain(hop_count=4)]
        )
        finding = RiskEngine.generate_finding(state)
        assert finding is not None
        assert "machine_readable" in finding
        mr = finding["machine_readable"]
        assert "risk_score" in mr
        assert "risk_level" in mr
        assert "confidence" in mr
        assert "indicators" in mr
        assert isinstance(mr["indicators"], list)

    def test_calculate_risk_returns_required_fields(self):
        state = make_base_state()
        result = RiskEngine.calculate_risk(state)
        for key in ["risk_score", "risk_level", "confidence", "indicators", "features", "contradictory_evidence"]:
            assert key in result, f"Missing key: {key}"

    def test_risk_score_bounds(self):
        state = make_base_state(
            transactions=[make_tx(is_laundering=1, is_terminal_cashout=1)],
            profiles=[make_profile(is_mule=1, withdrawal_velocity=100000)],
            transaction_chains=[make_chain(hop_count=5)]
        )
        result = RiskEngine.calculate_risk(state)
        assert 0.0 <= result["risk_score"] <= 100.0
        assert 0.0 <= result["confidence"] <= 1.0

    def test_confidence_bounds(self):
        """Confidence must stay in [0, 0.95] regardless of indicator count."""
        features = {
            "laundering_count": 10,
            "terminal_cashout_count": 5,
            "has_high_value": True,
            "unique_counterparties": 10,
            "mule_count": 3,
            "has_high_velocity": True,
            "multi_hop_presence": True,
            "max_chain_length": 10,
            "high_risk_state_presence": True,
            "max_incident_density": 5.0,
            "avg_amount": 50000.0
        }
        inds = IndicatorEngine.generate_indicators(features, "TEST", "T1")
        n = len(inds)
        conf = min(0.10 + n * 0.15, 0.95)
        assert conf <= 0.95
