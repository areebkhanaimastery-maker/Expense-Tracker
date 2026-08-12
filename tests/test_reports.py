import pytest

from app.repositories.sqlite_repository import SQLiteExpenseRepository
from app.services.expense_service import ExpenseService


@pytest.fixture
def service(tmp_path):
    db_path = tmp_path / "test_reports.db"
    repo = SQLiteExpenseRepository(db_path)
    return ExpenseService(repository=repo)


def test_reports_empty(service):
    report = service.get_reports()

    assert report["count"] == 0
    assert report["total"] == 0
    assert report["average"] == 0
    assert report["highest"] is None
    assert report["lowest"] is None
    assert report["categories"] == {}


def test_reports_total(service):
    service.add_expense(100, "Food", "Lunch")
    service.add_expense(200, "Food", "Dinner")
    service.add_expense(300, "Bills", "Internet")

    report = service.get_reports()

    assert report["total"] == 600


def test_reports_count(service):
    service.add_expense(100, "Food", "Lunch")
    service.add_expense(200, "Food", "Dinner")

    report = service.get_reports()

    assert report["count"] == 2


def test_reports_average(service):
    service.add_expense(100, "Food", "Lunch")
    service.add_expense(300, "Food", "Dinner")

    report = service.get_reports()

    assert report["average"] == 200.0


def test_reports_highest(service):
    service.add_expense(50, "Food", "Snack")
    service.add_expense(500, "Bills", "Internet")
    service.add_expense(100, "Transport", "Taxi")

    report = service.get_reports()

    assert report["highest"].amount == 500
    assert report["highest"].description == "Internet"


def test_reports_lowest(service):
    service.add_expense(50, "Food", "Snack")
    service.add_expense(500, "Bills", "Internet")
    service.add_expense(100, "Transport", "Taxi")

    report = service.get_reports()

    assert report["lowest"].amount == 50
    assert report["lowest"].description == "Snack"


def test_reports_categories(service):
    service.add_expense(10, "Food", "Burgers")
    service.add_expense(30, "Food", "Pizza")
    service.add_expense(60, "Bills", "Internet")

    report = service.get_reports()

    assert report["categories"]["Food"] == 40
    assert report["categories"]["Bills"] == 60


def test_reports_single_expense(service):
    service.add_expense(250, "Shopping", "Shoes")

    report = service.get_reports()

    assert report["count"] == 1
    assert report["total"] == 250
    assert report["average"] == 250
    assert report["highest"].amount == 250
    assert report["lowest"].amount == 250
