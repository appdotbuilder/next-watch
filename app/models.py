from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


# Persistent models (stored in database)


class User(SQLModel, table=True):
    """Registered user with profile and preferences."""

    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=50)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password_hash: str = Field(max_length=255)
    display_name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = Field(default=None)

    # Relationships
    viewing_history: List["ViewingHistory"] = Relationship(back_populates="user")
    watching_lists: List["WatchingList"] = Relationship(back_populates="user")
    preferences: List["UserPreference"] = Relationship(back_populates="user")
    recommendations: List["Recommendation"] = Relationship(back_populates="user")


class GuestSession(SQLModel, table=True):
    """Guest session for anonymous users."""

    __tablename__ = "guest_sessions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    session_token: str = Field(unique=True, max_length=255, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field()

    # Relationships
    viewing_history: List["ViewingHistory"] = Relationship(back_populates="guest_session")
    watching_lists: List["WatchingList"] = Relationship(back_populates="guest_session")
    preferences: List["UserPreference"] = Relationship(back_populates="guest_session")
    recommendations: List["Recommendation"] = Relationship(back_populates="guest_session")


class Movie(SQLModel, table=True):
    """Movie or TV show from TMDB."""

    __tablename__ = "movies"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    tmdb_id: int = Field(unique=True, index=True)
    title: str = Field(max_length=255)
    original_title: str = Field(max_length=255)
    overview: str = Field(default="", max_length=2000)
    poster_path: Optional[str] = Field(default=None, max_length=255)
    backdrop_path: Optional[str] = Field(default=None, max_length=255)
    release_date: Optional[datetime] = Field(default=None)
    runtime: Optional[int] = Field(default=None)  # in minutes
    vote_average: Decimal = Field(default=Decimal("0"), decimal_places=1)
    vote_count: int = Field(default=0)
    popularity: Decimal = Field(default=Decimal("0"), decimal_places=3)
    adult: bool = Field(default=False)
    media_type: str = Field(max_length=20)  # 'movie' or 'tv'

    # For TV shows
    first_air_date: Optional[datetime] = Field(default=None)
    number_of_seasons: Optional[int] = Field(default=None)
    number_of_episodes: Optional[int] = Field(default=None)

    # JSON fields for complex data
    genres: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    spoken_languages: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    production_countries: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    production_companies: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    keywords: List[str] = Field(default=[], sa_column=Column(JSON))
    cast: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    crew: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))

    is_popular: bool = Field(default=False, index=True)  # For curated popular content
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    viewing_history: List["ViewingHistory"] = Relationship(back_populates="movie")
    watching_list_items: List["WatchingListItem"] = Relationship(back_populates="movie")
    recommendations: List["Recommendation"] = Relationship(back_populates="movie")


class ViewingHistory(SQLModel, table=True):
    """User's viewing history with preferences."""

    __tablename__ = "viewing_history"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    guest_session_id: Optional[int] = Field(default=None, foreign_key="guest_sessions.id", index=True)
    movie_id: int = Field(foreign_key="movies.id", index=True)

    # User's reaction to the content
    liked: bool = Field()  # True for liked, False for disliked
    watched_at: datetime = Field(default_factory=datetime.utcnow)
    rating: Optional[int] = Field(default=None, ge=1, le=10)  # Optional user rating 1-10
    notes: Optional[str] = Field(default=None, max_length=500)

    # Relationships
    user: Optional[User] = Relationship(back_populates="viewing_history")
    guest_session: Optional[GuestSession] = Relationship(back_populates="viewing_history")
    movie: Movie = Relationship(back_populates="viewing_history")


class WatchingList(SQLModel, table=True):
    """User's custom watching lists (e.g., 'Watch Later', 'Favorites')."""

    __tablename__ = "watching_lists"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    guest_session_id: Optional[int] = Field(default=None, foreign_key="guest_sessions.id", index=True)

    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_default: bool = Field(default=False)  # Default list like "Watch Later"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="watching_lists")
    guest_session: Optional[GuestSession] = Relationship(back_populates="watching_lists")
    items: List["WatchingListItem"] = Relationship(back_populates="watching_list")


class WatchingListItem(SQLModel, table=True):
    """Items in a watching list."""

    __tablename__ = "watching_list_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    watching_list_id: int = Field(foreign_key="watching_lists.id", index=True)
    movie_id: int = Field(foreign_key="movies.id", index=True)
    added_at: datetime = Field(default_factory=datetime.utcnow)
    priority: int = Field(default=0)  # For ordering within list

    # Relationships
    watching_list: WatchingList = Relationship(back_populates="items")
    movie: Movie = Relationship(back_populates="watching_list_items")


class UserPreference(SQLModel, table=True):
    """User preferences for recommendation algorithm."""

    __tablename__ = "user_preferences"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    guest_session_id: Optional[int] = Field(default=None, foreign_key="guest_sessions.id", index=True)

    # Preference types and values
    preference_type: str = Field(max_length=50, index=True)  # 'genre', 'actor', 'director', 'keyword', etc.
    preference_value: str = Field(max_length=255, index=True)  # The actual value
    weight: Decimal = Field(default=Decimal("1.0"), decimal_places=2)  # Preference strength

    # Context for the preference
    source: str = Field(max_length=50)  # 'liked_movie', 'disliked_movie', 'manual'
    source_movie_id: Optional[int] = Field(default=None, foreign_key="movies.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="preferences")
    guest_session: Optional[GuestSession] = Relationship(back_populates="preferences")


class Recommendation(SQLModel, table=True):
    """AI-generated recommendations for users."""

    __tablename__ = "recommendations"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    guest_session_id: Optional[int] = Field(default=None, foreign_key="guest_sessions.id", index=True)
    movie_id: int = Field(foreign_key="movies.id", index=True)

    # Recommendation details
    score: Decimal = Field(decimal_places=4)  # AI confidence score 0-1
    reason: str = Field(max_length=500)  # AI-generated reason
    recommendation_type: str = Field(max_length=50)  # 'similar_genre', 'similar_cast', 'ai_generated', etc.

    # User interaction with recommendation
    shown_at: Optional[datetime] = Field(default=None)
    user_action: Optional[str] = Field(
        default=None, max_length=50
    )  # 'liked', 'disliked', 'added_to_list', 'watched_and_liked', etc.
    user_action_at: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)  # For recommendation freshness

    # Relationships
    user: Optional[User] = Relationship(back_populates="recommendations")
    guest_session: Optional[GuestSession] = Relationship(back_populates="recommendations")
    movie: Movie = Relationship(back_populates="recommendations")


class SwipeSession(SQLModel, table=True):
    """Tracks swiping sessions for recommendation flow."""

    __tablename__ = "swipe_sessions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    guest_session_id: Optional[int] = Field(default=None, foreign_key="guest_sessions.id", index=True)

    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = Field(default=None)
    total_swipes: int = Field(default=0)
    likes: int = Field(default=0)
    dislikes: int = Field(default=0)
    watched_and_liked: int = Field(default=0)
    watched_and_disliked: int = Field(default=0)
    added_to_list: int = Field(default=0)


# Non-persistent schemas (for validation, forms, API requests/responses)


class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8)
    display_name: str = Field(max_length=100)


class UserUpdate(SQLModel, table=False):
    display_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)


class UserLogin(SQLModel, table=False):
    username_or_email: str = Field(max_length=255)
    password: str = Field()


class GuestSessionCreate(SQLModel, table=False):
    session_token: str = Field(max_length=255)
    expires_in_days: int = Field(default=30, ge=1, le=365)


class MovieSearch(SQLModel, table=False):
    query: str = Field(max_length=255)
    media_type: Optional[str] = Field(default=None)  # 'movie', 'tv', or None for both
    genre_ids: Optional[List[int]] = Field(default=None)
    year: Optional[int] = Field(default=None)
    page: int = Field(default=1, ge=1)


class MovieUpdate(SQLModel, table=False):
    """For updating movie data from TMDB."""

    tmdb_id: int
    title: str = Field(max_length=255)
    original_title: str = Field(max_length=255)
    overview: str = Field(default="", max_length=2000)
    poster_path: Optional[str] = Field(default=None, max_length=255)
    backdrop_path: Optional[str] = Field(default=None, max_length=255)
    release_date: Optional[str] = Field(default=None)  # Will be converted to datetime
    runtime: Optional[int] = Field(default=None)
    vote_average: Decimal = Field(decimal_places=1)
    vote_count: int
    popularity: Decimal = Field(decimal_places=3)
    adult: bool = Field(default=False)
    media_type: str = Field(max_length=20)
    genres: List[Dict[str, Any]] = Field(default=[])
    spoken_languages: List[Dict[str, Any]] = Field(default=[])
    production_countries: List[Dict[str, Any]] = Field(default=[])
    production_companies: List[Dict[str, Any]] = Field(default=[])
    keywords: List[str] = Field(default=[])
    cast: List[Dict[str, Any]] = Field(default=[])
    crew: List[Dict[str, Any]] = Field(default=[])


class ViewingHistoryCreate(SQLModel, table=False):
    movie_id: int
    liked: bool
    rating: Optional[int] = Field(default=None, ge=1, le=10)
    notes: Optional[str] = Field(default=None, max_length=500)


class WatchingListCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class WatchingListUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class WatchingListItemCreate(SQLModel, table=False):
    watching_list_id: int
    movie_id: int
    priority: int = Field(default=0)


class RecommendationCreate(SQLModel, table=False):
    movie_id: int
    score: Decimal = Field(decimal_places=4)
    reason: str = Field(max_length=500)
    recommendation_type: str = Field(max_length=50)
    expires_in_days: Optional[int] = Field(default=None, ge=1)


class RecommendationUpdate(SQLModel, table=False):
    user_action: str = Field(max_length=50)  # 'liked', 'disliked', 'added_to_list', etc.


class SwipeAction(SQLModel, table=False):
    """Schema for handling swipe actions."""

    recommendation_id: int
    action: str = Field(max_length=50)  # 'like', 'dislike', 'watched_and_liked', 'watched_and_disliked', 'add_to_list'
    watching_list_id: Optional[int] = Field(default=None)  # For 'add_to_list' action
    rating: Optional[int] = Field(default=None, ge=1, le=10)  # For watched actions
    notes: Optional[str] = Field(default=None, max_length=500)  # For watched actions


class RecommendationResponse(SQLModel, table=False):
    """Response schema for recommendations with movie details."""

    id: int
    movie_id: int
    score: Decimal
    reason: str
    recommendation_type: str
    created_at: str  # ISO format
    movie: Dict[str, Any]  # Full movie details


class PopularMoviesResponse(SQLModel, table=False):
    """Response schema for popular movies list."""

    movies: List[Dict[str, Any]]
    page: int
    total_pages: int
    total_results: int
