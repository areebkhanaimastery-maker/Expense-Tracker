from app.cli.app import ExpenseTrackerCLI
from app.config import settings
from app.logging_config import configure_logging
from app.repositories.sqlite_repository import SQLiteExpenseRepository
from app.services.analytics_service import AnalyticsService
from app.services.anomaly_service import AnomalyService
from app.services.expense_service import ExpenseService
from app.services.intelligence_service import IntelligenceService
from app.services.prediction_service import PredictionService


def main():
    configure_logging(settings.log_level)

    repository = SQLiteExpenseRepository()

    expense_service = ExpenseService(repository)
    analytics_service = AnalyticsService(repository)
    anomaly_service = AnomalyService(repository)
    prediction_service = PredictionService(repository)
    intelligence_service = IntelligenceService(
        repository, anomaly_service=anomaly_service
    )

    application = ExpenseTrackerCLI(
        service=expense_service,
        analytics=analytics_service,
        anomaly_service=anomaly_service,
        prediction_service=prediction_service,
        intelligence_service=intelligence_service,
    )

    application.run()


if __name__ == "__main__":
    main()