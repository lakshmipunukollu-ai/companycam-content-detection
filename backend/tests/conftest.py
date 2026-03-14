"""Shared test fixtures using PostgreSQL with savepoint isolation."""
import os
import uuid
import pytest

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

os.environ.setdefault("UPLOAD_DIR", "./test_uploads")

from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, engine, get_db
from app.main import app
from app.models.user import User
from app.models.project import Project
from app.models.photo import Photo
from app.models.detection import Detection
from app.models.classification import Classification
from app.models.damage_assessment import DamageAssessment
from app.models.correction import Correction
from app.auth.jwt_handler import hash_password, create_access_token


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables at the start of test session."""
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(scope="function")
def db_session():
    """Create a test DB session using nested transactions (savepoints).

    Each test runs inside a savepoint. Any commits within the test
    (e.g., from endpoint handlers) become savepoint releases. After the
    test, we roll back the outer transaction so no data persists.
    """
    connection = engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()

    # Begin a nested savepoint
    nested = connection.begin_nested()

    # When the session commits, re-open a new nested savepoint
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, trans):
        nonlocal nested
        if trans.nested and not trans._parent.nested:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with DB session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    os.makedirs("./test_uploads", exist_ok=True)

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user and return (user, token)."""
    user = User(
        id=uuid.uuid4(),
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("password123"),
        full_name="Test User",
        role="contractor",
    )
    db_session.add(user)
    db_session.flush()
    token = create_access_token(str(user.id), user.role)
    return user, token


@pytest.fixture
def auth_headers(test_user):
    """Return auth headers for test user."""
    _, token = test_user
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_project(db_session, test_user):
    """Create a test project."""
    user, _ = test_user
    project = Project(
        id=uuid.uuid4(),
        name="Test Project",
        description="A test project",
        address="123 Test St",
        owner_id=user.id,
    )
    db_session.add(project)
    db_session.flush()
    return project


@pytest.fixture
def test_photo(db_session, test_user, test_project):
    """Create a test photo."""
    user, _ = test_user
    photo = Photo(
        id=uuid.uuid4(),
        project_id=test_project.id,
        uploaded_by=user.id,
        filename="test_photo.jpg",
        file_path="./test_uploads/test_photo.jpg",
        photo_type="roof",
        status="completed",
        width=1920,
        height=1080,
    )
    db_session.add(photo)
    db_session.flush()
    return photo


@pytest.fixture
def test_detection(db_session, test_photo):
    """Create a test detection."""
    detection = Detection(
        id=uuid.uuid4(),
        photo_id=test_photo.id,
        stage="cv",
        label="shingle_bundle",
        confidence=0.92,
        bbox_x=120.0,
        bbox_y=80.0,
        bbox_w=200.0,
        bbox_h=150.0,
    )
    db_session.add(detection)
    db_session.flush()
    return detection


@pytest.fixture
def test_classification(db_session, test_photo):
    """Create a test classification."""
    cls = Classification(
        id=uuid.uuid4(),
        photo_id=test_photo.id,
        category="material",
        subcategory="shingle_bundle",
        description="Bundle of architectural shingles",
        quantity_estimate=12.0,
        unit="bundles",
        confidence=0.87,
        requires_review=False,
    )
    db_session.add(cls)
    db_session.flush()
    return cls


@pytest.fixture
def test_damage_assessment(db_session, test_photo):
    """Create a test damage assessment."""
    da = DamageAssessment(
        id=uuid.uuid4(),
        photo_id=test_photo.id,
        damage_type="hail_impact",
        severity="high",
        location_description="Northeast section",
        affected_area_pct=25.5,
        repair_urgency="urgent",
    )
    db_session.add(da)
    db_session.flush()
    return da
