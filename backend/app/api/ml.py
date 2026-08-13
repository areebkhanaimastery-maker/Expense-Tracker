"""
Machine Learning API Router.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.deps import get_anomaly_service, get_prediction_service
from backend.app.schemas.common import APIResponse
from backend.app.schemas.ml import (
    AnomalyResponse,
    AnomalyItem,
    PredictionResponse,
    PredictionItem,
    ModelTrainResponse,
)

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.get("/anomalies", response_model=APIResponse[AnomalyResponse])
def get_anomalies(
    contamination: float = Query(0.02, gt=0, lt=0.5),
    anomaly_service=Depends(get_anomaly_service),
):
    """Detect unusual transactions using Isolation Forest."""
    try:
        results = anomaly_service.detect()
        anomalies = []
        for r in results:
            # Determine severity based on anomaly score or amount
            score = abs(r.anomaly_score)
            severity = "High" if score > 0.1 else ("Medium" if score > 0.05 else "Low")
            anomalies.append(
                AnomalyItem(
                    expense_id=r.expense_id,
                    amount=r.amount,
                    category=r.category,
                    description=r.description,
                    date=r.date,
                    anomaly_score=r.anomaly_score,
                    is_anomaly=r.is_anomaly,
                    severity=severity,
                )
            )

        total_analyzed = len(anomaly_service.repository.get_all())
        return APIResponse(
            success=True,
            data=AnomalyResponse(
                total_analyzed=total_analyzed,
                total_anomalies=len(anomalies),
                anomalies=anomalies,
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "ANOMALY_DETECTION_ERROR", "message": str(e)},
        )


@router.get("/predictions", response_model=APIResponse[PredictionResponse])
def get_predictions(prediction_service=Depends(get_prediction_service)):
    """Retrieve machine learning spending predictions."""
    try:
        res = prediction_service.predict_next_month()
        if "error" in res:
            next_month = 0.0
            model_name = "Model Training Required"
            disclaimer = res["error"]
        else:
            next_month = float(res.get("total", 0.0))
            model_name = res.get("model", "HistGradientBoostingRegressor")
            disclaimer = res.get(
                "note",
                "Predictions are statistical estimates based on historical spending patterns and are not guaranteed outcomes.",
            )

        predictions = [
            PredictionItem(horizon="Next Day", predicted_amount=round(next_month / 30.0, 2)),
            PredictionItem(horizon="Next 7 Days", predicted_amount=round((next_month / 30.0) * 7.0, 2)),
            PredictionItem(horizon="Next 30 Days", predicted_amount=round(next_month, 2)),
            PredictionItem(horizon="Next Month", predicted_amount=round(next_month, 2)),
        ]

        return APIResponse(
            success=True,
            data=PredictionResponse(
                next_month_prediction=round(next_month, 2),
                predictions=predictions,
                model_name=model_name,
                disclaimer=disclaimer,
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "PREDICTION_ERROR", "message": str(e)},
        )


@router.post("/train", response_model=APIResponse[ModelTrainResponse])
def train_models():
    """Trigger retraining of spending prediction models."""
    try:
        from ml.train import train_and_save_model
        metrics = train_and_save_model()
        return APIResponse(
            success=True,
            data=ModelTrainResponse(
                success=True,
                message=f"Model successfully trained with RMSE={metrics.get('test_rmse', 0):.2f}, MAE={metrics.get('test_mae', 0):.2f}",
                trained_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "TRAINING_FAILED", "message": str(e)},
        )
