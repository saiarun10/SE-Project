import pytest
from app import create_app
from model import db as _db
from config import TestingConfig

@pytest.fixture(scope='session')
def app():
    """
    Session-wide test Flask application.
    This fixture creates an application instance with a testing configuration,
    ensuring that the tests run in an isolated environment.
    """
    app = create_app()
    app.config.from_object(TestingConfig)
    
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    """
    Session-wide test database.
    This fixture creates all database tables before the test session starts
    and drops them all after the session ends, ensuring a clean slate.
    """
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    """
    Function-scoped database session.
    This fixture ensures that each test function has a clean database state
    by using a nested transaction (savepoint) and rolling back after the test.
    This prevents test side-effects from affecting other tests.
    """
    # Start a nested transaction (uses a SAVEPOINT)
    db.session.begin_nested()
    
    # Yield the session object to the test function
    yield db.session
    
    # Rollback the transaction, undoing any changes made in the test
    db.session.rollback()


@pytest.fixture(scope='function')
def client(app):
    """
    Function-scoped test client.
    Provides a Flask test client for making requests to the application
    within each test function.
    """
    return app.test_client()

@pytest.fixture
def runner(app):
    """
    A test runner for the Flask command-line interface (CLI).
    """
    return app.test_cli_runner()
