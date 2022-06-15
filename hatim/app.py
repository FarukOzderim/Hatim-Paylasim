from fastapi import FastAPI, Depends
from .db import Hatim, create_db_and_tables, create_new_hatim, get_session, Session

app = FastAPI()
create_db_and_tables()


@app.post("/create_hatim", response_model=Hatim)
def create_hatim(*, session: Session = Depends(get_session), creator_id: int) -> Hatim:
    return create_new_hatim(creator_id, session=session)
