from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Prediction(Base):
    """One saved irrigation prediction (one row per analysis)."""
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now)
    soil_moisture: Mapped[float]
    temperature: Mapped[float]
    humidity: Mapped[float]
    irrigation_level: Mapped[float]
    irrigation_category: Mapped[str]
    recommendation: Mapped[str]
