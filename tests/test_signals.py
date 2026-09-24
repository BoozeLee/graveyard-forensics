from datetime import datetime, timedelta, timezone

from graveyard_forensics.signals import classify_smells, estate_score


def test_price_claim_detected():
    smells, classification = classify_smells(
        description="AI health optimization | $299/month",
        name="health-optimizer",
        homepage=None,
        homepage_status=None,
        is_fork=False,
        is_archived=False,
        stars=0,
        pushed_at=None,
    )
    assert "price_claim" in smells
    assert classification == "vapor_price_claim"


def test_migration_stub_detected():
    smells, classification = classify_smells(
        description="Migrated to bakery-street-studio — see BoozeLee/bakery-street-studio",
        name="conduit",
        homepage=None,
        homepage_status=None,
        is_fork=False,
        is_archived=False,
        stars=0,
        pushed_at=None,
    )
    assert "migration_stub" in smells
    assert classification == "migration_stub"


def test_humanitarian_claim():
    smells, _ = classify_smells(
        description="FREE for governments and NGOs",
        name="ubi-calculator",
        homepage=None,
        homepage_status=None,
        is_fork=False,
        is_archived=False,
        stars=0,
        pushed_at=None,
    )
    assert "humanitarian_claim" in smells


def test_recent_push_is_active_unproven():
    recent = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
    smells, classification = classify_smells(
        description="Something new",
        name="capo",
        homepage=None,
        homepage_status=None,
        is_fork=False,
        is_archived=False,
        stars=0,
        pushed_at=recent,
    )
    assert classification == "active_unproven"
    assert "zero_stars" in smells


def test_dead_homepage():
    smells, _ = classify_smells(
        description="DJ platform",
        name="mixhive",
        homepage="https://mixhive.app",
        homepage_status=0,
        is_fork=False,
        is_archived=False,
        stars=0,
        pushed_at=None,
    )
    assert "dead_homepage" in smells


def test_estate_score_open_casket():
    score, band = estate_score(
        {
            "total_public_repos": 100,
            "zero_star_count": 95,
            "price_claim_repos": list(range(15)),
            "migration_stub_repos": list(range(10)),
            "missing_description_count": 20,
            "dead_homepage_repos": 5,
        }
    )
    assert score >= 75
    assert band == "open-casket"


def test_sensitive_name_flags_do_not_monetize_in_scan_path():
    # classification promotion to do_not_monetize happens in gh.scan_estate;
    # signals should at least not crash and still mark smells.
    smells, _ = classify_smells(
        description="Early disease detection",
        name="disease-predictor",
        homepage=None,
        homepage_status=None,
        is_fork=False,
        is_archived=False,
        stars=0,
        pushed_at=None,
    )
    assert "zero_stars" in smells
