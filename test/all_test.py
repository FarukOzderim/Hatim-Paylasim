import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from hatim.app import *
from hatim.db import *


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestEndpoints:
    def test_create_hatim(self, session):
        assert Hatim(id=1, creator_id=1) == create_hatim(session=session, creator_id=1)


class TestDatabase:
    def test_db(self, session):
        assert Hatim(id=1, creator_id=1) == create_new_hatim(1, session)
        assert Hatim(id=2, creator_id=1) == create_new_hatim(1, session)
        assert [Hatim(id=1, creator_id=1), Hatim(id=2, creator_id=1)] == get_all_hatims(
            session
        )
        assert [
            Hatim(id=1, creator_id=1),
            Hatim(id=2, creator_id=1),
        ] == get_users_created_hatims(1, session)
        assert HatimPiece(
            id=1, hatim_id=1, five_page_piece_id=1, user_id=1, is_read=False
        ) == select_hatim_piece(
            HatimPiece(hatim_id=1, five_page_piece_id=1, user_id=1),
            session=session,
        )
        assert HatimPiece(
            id=2, hatim_id=1, five_page_piece_id=2, user_id=1, is_read=False
        ) == select_hatim_piece(
            HatimPiece(hatim_id=1, five_page_piece_id=2, user_id=1),
            session=session,
        )
        with pytest.raises(HTTPException):
            assert HatimPiece(
                id=1, hatim_id=1, five_page_piece_id=1, user_id=1, is_read=False
            ) == select_hatim_piece(
                HatimPiece(hatim_id=1, five_page_piece_id=1, user_id=1),
                session=session,
            )
        with pytest.raises(HTTPException):
            assert HatimPiece(
                id=1, hatim_id=1, five_page_piece_id=1, user_id=1, is_read=False
            ) == select_hatim_piece(
                HatimPiece(hatim_id=1, five_page_piece_id=1, user_id=2),
                session=session,
            )
        with pytest.raises(HTTPException):
            assert HatimPiece(
                id=1, hatim_id=1, five_page_piece_id=2, user_id=1, is_read=False
            ) == select_hatim_piece(
                HatimPiece(hatim_id=1, five_page_piece_id=2, user_id=2),
                session=session,
            )
        assert [
            HatimPiece(
                id=1, hatim_id=1, five_page_piece_id=1, user_id=1, is_read=False
            ),
            HatimPiece(
                id=2, hatim_id=1, five_page_piece_id=2, user_id=1, is_read=False
            ),
        ] == get_hatim_pieces(1, session)
        assert [
            HatimPiece(
                id=1, hatim_id=1, five_page_piece_id=1, user_id=1, is_read=False
            ),
            HatimPiece(
                id=2, hatim_id=1, five_page_piece_id=2, user_id=1, is_read=False
            ),
        ] == get_users_hatim_pieces(1, session)
        assert HatimPiece(
            id=2, hatim_id=1, five_page_piece_id=2, user_id=1, is_read=True
        ) == piece_is_read(
            HatimPiece(hatim_id=1, five_page_piece_id=2, user_id=1),
            session=session,
        )
        assert HatimPiece(
            id=2, hatim_id=1, five_page_piece_id=2, user_id=1, is_read=False
        ) == piece_is_unread(
            HatimPiece(hatim_id=1, five_page_piece_id=2, user_id=1),
            session=session,
        )

        assert unselect_hatim_piece(
            HatimPiece(hatim_id=1, five_page_piece_id=2, user_id=1),
            session=session,
        )
        assert [
            HatimPiece(
                id=1, hatim_id=1, five_page_piece_id=1, user_id=1, is_read=False
            ),
        ] == get_hatim_pieces(1, session)

        assert HatimPiece(
            id=2, hatim_id=1, five_page_piece_id=2, user_id=1, is_read=False
        ) == select_hatim_piece(
            HatimPiece(hatim_id=1, five_page_piece_id=2, user_id=1),
            session=session,
        )
        assert delete_hatim(hatim_id=1, session=session)
        assert [Hatim(id=2, creator_id=1)] == get_all_hatims(session)
        assert [] == get_hatim_pieces(1, session)
