from sqlalchemy import func
from models import Rating

def get_average_rating(movie):
    avg_rating = Rating.query.with_entities(func.avg(Rating.score).label('average')).filter_by(movie_id=movie.id).first()
    return round(avg_rating.average, 1) if avg_rating.average else None
