from sqlalchemy.orm import Session


class BaseService:

    @staticmethod
    def commit(db: Session, *instances) -> None:
        
        db.commit()

        for instance in instances:
            db.refresh(instance)
