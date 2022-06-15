import random
from typing import List, Optional, Union, Tuple
from fastapi import Depends, Query, HTTPException
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select, and_


class Hatim(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    creator_id: int = Field(index=True)
    hatim_pieces: Optional[List["HatimPiece"]] = Relationship(back_populates="hatim")


class HatimPieceBase(SQLModel):
    hatim_id: int = Field(index=True, default=None, foreign_key="hatim.id")
    five_page_piece_id: int = Field(index=True)
    user_id: int = Field(index=True)
    is_read: Optional[bool] = False


class HatimPiece(HatimPieceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hatim: Hatim = Relationship(back_populates="hatim_pieces")


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(
    sqlite_url, echo=False, connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def create_new_hatim(
    creator_id: int,
    session: Session = next(get_session()),
) -> Hatim:
    hatim = Hatim(creator_id=creator_id)
    session.add(hatim)
    session.commit()
    session.refresh(hatim)
    return hatim


def delete_hatim(
    hatim_id: int,
    session: Session = next(get_session()),
) -> Hatim:
    hatim = session.exec(select(Hatim).where(Hatim.id == hatim_id)).first()
    if not hatim:
        raise HTTPException(status_code=404, detail=f"Hatim does not exist")

    session.delete(hatim)
    session.commit()
    hatim = session.exec(select(Hatim).where(Hatim == hatim)).first()
    return hatim is None


def get_all_hatims(
    session: Session = next(get_session()),
    offset: int = 0,
    limit: int = 100,
) -> List[Hatim]:
    hatim_list = session.exec(select(Hatim).offset(offset).limit(limit)).all()
    return hatim_list


def get_users_created_hatims(
    user_id: int,
    session: Session = next(get_session()),
) -> List[Hatim]:
    hatim_list = session.exec(select(Hatim).where(Hatim.creator_id == user_id)).all()
    return hatim_list


def select_hatim_piece(
    hatim_piece: HatimPieceBase,
    session: Session = next(get_session()),
) -> Hatim:
    exists = session.exec(
        select(HatimPiece).where(
            and_(
                HatimPiece.hatim_id == hatim_piece.hatim_id,
                HatimPiece.five_page_piece_id == hatim_piece.five_page_piece_id,
            )
        )
    ).first()
    if exists:
        raise HTTPException(
            status_code=404,
            detail=f"Hatim piece is already selected by user_id: {exists.user_id}",
        )

    hatim_piece = HatimPiece.from_orm(hatim_piece)
    session.add(hatim_piece)
    session.commit()
    session.refresh(hatim_piece)
    return hatim_piece


def unselect_hatim_piece(
    hatim_piece: HatimPieceBase,
    session: Session = next(get_session()),
) -> bool:
    piece = session.exec(
        select(HatimPiece).where(
            and_(
                HatimPiece.hatim_id == hatim_piece.hatim_id,
                HatimPiece.five_page_piece_id == hatim_piece.five_page_piece_id,
            )
        )
    ).first()
    if not piece:
        raise HTTPException(status_code=404, detail=f"Hatim piece does not exist")

    session.delete(piece)
    session.commit()
    piece = session.exec(
        select(HatimPiece).where(
            and_(
                HatimPiece.hatim_id == hatim_piece.hatim_id,
                HatimPiece.five_page_piece_id == hatim_piece.five_page_piece_id,
            )
        )
    ).first()
    return piece is None


def get_hatim_pieces(
    hatim_id: int,
    session: Session = next(get_session()),
) -> List[HatimPiece]:
    hatim_list = session.exec(
        select(HatimPiece).where(HatimPiece.hatim_id == hatim_id)
    ).all()
    return hatim_list


def get_users_hatim_pieces(
    user_id: int,
    session: Session = next(get_session()),
) -> List[HatimPiece]:
    hatim_list = session.exec(
        select(HatimPiece).where(HatimPiece.user_id == user_id)
    ).all()
    return hatim_list


def piece_is_read(
    hatim_piece: HatimPieceBase,
    session: Session = next(get_session()),
) -> HatimPiece:
    piece = session.exec(
        select(HatimPiece).where(
            and_(
                HatimPiece.hatim_id == hatim_piece.hatim_id,
                HatimPiece.five_page_piece_id == hatim_piece.five_page_piece_id,
                HatimPiece.user_id == hatim_piece.user_id,
            )
        )
    ).one()
    piece.is_read = True
    session.add(piece)
    session.commit()
    session.refresh(piece)
    return piece


def piece_is_unread(
    hatim_piece: HatimPieceBase,
    session: Session = next(get_session()),
) -> HatimPiece:
    piece = session.exec(
        select(HatimPiece).where(
            and_(
                HatimPiece.hatim_id == hatim_piece.hatim_id,
                HatimPiece.five_page_piece_id == hatim_piece.five_page_piece_id,
                HatimPiece.user_id == hatim_piece.user_id,
            )
        )
    ).one()
    piece.is_read = False
    session.add(piece)
    session.commit()
    session.refresh(piece)
    return piece
