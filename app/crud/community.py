from sqlalchemy.orm import Session
from .. import models, schemas

# 전체 게시글 조회 (최신순) - SNS 피드처럼
def get_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.CommunityPost)\
             .order_by(models.CommunityPost.created_at.desc())\
             .offset(skip).limit(limit).all()

# 게시글 작성
def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.CommunityPost(
        **post.dict(),
        user_id=user_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post