import logging
from collections import ChainMap
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from devtools import debug
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy_utils.functions import get_class_by_table, get_mapper

from app.db.base_class import Base

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


# def clear_debug(*args):
#     print("\n\n\n")
#     debug(*args)
#     print("\n\n\n")
def clear_debug(*args):
    pass


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List[Dict]] = None,
    ) -> List[ModelType]:
        clear_debug("Calling get multi")
        if not filters:
            obj = db.query(self.model).offset(skip).limit(limit).all()
            clear_debug(jsonable_encoder(obj))
            return obj

        else:
            filters = ChainMap(*filters)
            return (
                db.query(self.model)
                .filter_by(**filters)
                .offset(skip)
                .limit(limit)
                .all()
            )

    def create_or_match(
        self, db: Session, *, obj_in: CreateSchemaType, owner_id: int, model=None
    ):
        # print("=====Start=====")
        obj = self.create_or_match_loopfn(
            db, obj_in=obj_in, owner_id=owner_id, model=model
        )
        db.commit()
        # print("=====End=====")
        # get the object anew so we have all the content
        clear_debug(model)
        obj = db.query(self.model).filter(self.model.id == obj.id).first()
        clear_debug(jsonable_encoder(obj))
        # clear_debug(obj.parts)
        return jsonable_encoder(obj)

    def create_or_match_loopfn(
        self, db: Session, *, obj_in: Any, owner_id: int, model=None
    ):
        """
        Match an object if it exists, or if not create one.

        This function is recursive and always returns the outmost
        object.
        """
        clear_debug("Starting loop")
        if not model:
            model = self.model

        clear_debug(obj_in)
        safe_filter = {
            k: v
            for k, v in dict(obj_in).items()
            if any((isinstance(v, str), isinstance(v, int), isinstance(v, float)))
        }
        db_obj = model(owner_id=owner_id)

        clear_debug("Querying")
        query = db.query(model).filter_by(**safe_filter)
        try:
            d = query.one()
            mapper = get_mapper(d)
            return d
        except MultipleResultsFound:
            logger.info(f"Multiple matches found for {obj_in}, using first")
            clear_debug(f"Multiple matches found for {obj_in}, using first")
            d = query.first()
            return d
        except NoResultFound:
            logger.info(f"No matches for {obj_in}, creating")
            clear_debug(f"No matches for {obj_in}, creating")
            clear_debug("mapping")
            mapper = get_mapper(db_obj)
            for name, target in mapper.relationships.items():
                clear_debug(f"Creating target {name} of type {target}")
                if target.secondary is not None:
                    clear_debug("Target has secondary table.")
                    target_model = get_class_by_table(Base, target.target)
                    try:
                        target_data = getattr(obj_in, name)
                    except AttributeError:
                        clear_debug("Input has no value, skipping")
                        continue
                    if not target_data:
                        clear_debug("Input value is empty, skipping")
                        continue
                    for entry in target_data:
                        clear_debug("Getting current data")
                        current = getattr(db_obj, name)

                        clear_debug("Looping")
                        new = self.create_or_match_loopfn(
                            db, obj_in=entry, owner_id=owner_id, model=target_model
                        )
                        if new in current:
                            # always duplicate identical lines
                            new = target_model(**jsonable_encoder(entry))
                        current.append(new)

                        setattr(db_obj, name, current)
                    delattr(obj_in, name)

                else:
                    clear_debug(
                        f"Making or getting non many-to-many object {name} of type {target}"
                    )
                    target_model = get_class_by_table(Base, target.target)
                    try:
                        target_data = getattr(obj_in, name)
                    except AttributeError:
                        continue
                    if not target_data:
                        continue

                    new = self.create_or_match_loopfn(
                        db, obj_in=target_data, owner_id=owner_id, model=target_model
                    )

                    setattr(db_obj, name, new)
                    delattr(obj_in, name)
                # else:
                #     clear_debug(f"Got here, need to make obj {target.target}")

        for k, v in obj_in:
            # print(f"k: {k}, v: {v}")
            try:
                setattr(db_obj, k, v)
            except (TypeError, AttributeError):
                pass
        db.add(db_obj)

        return db_obj

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj


CRUDType = TypeVar("CRUDType", bound=CRUDBase)


class CRUDWithOwnerBase(CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]):
    def create_with_owner(
        self, db: Session, *, obj_in: CreateSchemaType, owner_id: int
    ) -> ModelType:
        obj_in = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self,
        db: Session,
        *,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List[Dict]] = None,
    ) -> List[ModelType]:
        if not filters:
            return (
                db.query(self.model)
                .filter(self.model.owner_id == owner_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        else:
            filters = ChainMap(*filters)
            return (
                db.query(self.model)
                .filter(self.model.owner_id == owner_id)
                .filter_by(**filters)
                .offset(skip)
                .limit(limit)
                .all()
            )
