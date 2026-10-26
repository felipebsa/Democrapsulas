#import every model here so Base.metadata knows all tables (used by alembic)
from app.models.user import User
from app.models.capsule import Capsule
from app.models.vote import Vote
from app.models.favorite import Favorite
from app.models.report import Report
