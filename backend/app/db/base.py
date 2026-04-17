from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here so they are registered with Base.metadata
import app.models.domain  # noqa
import app.models.brief_archive # noqa
import app.models.strategic_scenario # noqa
import app.models.v2  # noqa
