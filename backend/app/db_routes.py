
import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
import uuid

from .limiter import limiter
from .database import get_async_db
from .models import *

from .config import DB_SECRET_KEY
# from backend.utils.Numerology import Person
from sqlalchemy.orm import class_mapper
from sqlalchemy.engine import Row


from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import asc, desc
from sqlalchemy.sql import text
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Type, Any
from pydantic import BaseModel
 

router = APIRouter()

# Helper: Validate UUID
def is_valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False
    

def row_to_dict(row):
    """
    Convert SQLAlchemy Row object, tuple, or ORM model instance to dictionary.
    """
    print("row:", row)
    
    # If the row is a Row object (which is a dictionary-like object)
    if isinstance(row, Row):
        return {column: value for column, value in zip(row.keys(), row)}
    
    # If the row is a tuple (a plain result from select)
    elif isinstance(row, tuple):
        # Handling the case when the row is a tuple with model instances
        # The first element of the tuple is the model instance
        return {f"column_{idx}": value for idx, value in enumerate(row)}

    # If the row is an ORM model instance, extract its attributes
    elif hasattr(row, '__dict__'):
        # This is an SQLAlchemy model instance, extract its attributes
        # Convert it to a dictionary, skipping private attributes
        return {column: getattr(row, column) for column in row.__dict__ if not column.startswith('_')}
    
    else:
        raise ValueError(f"Unsupported row type: {type(row)}")



# 1. Dynamic ORM Query Handler
async def dynamic_query(
    db: AsyncSession,
    # db: Session,
    model: Type[Any],
    filters: Optional[dict] = None,
    sort_by: Optional[str] = None,
    order: Optional[str] = "asc",
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    include_relations: Optional[List[str]] = None,
) -> List[dict]:
    """
    Perform a dynamic query on a given SQLAlchemy model.
    """
    pass

    # CANT SHARE THIS IMPLEMENTATION, AS IT IS A PART OF ADMIN PANEL