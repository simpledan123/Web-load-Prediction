from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class CommunityPost(Base):
    __tablename__ = "community_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    title = Column(String, index=True)
    content = Column(Text)  # 긴 글을 저장하기 위해 Text 타입 사용
    image_url = Column(String, nullable=True)  # 이미지 경로 (S3 URL 등)
    likes = Column(Integer, default=0)  # 좋아요 수 (트래픽 가중치로 활용 가능)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 관계 설정
    author = relationship("User", back_populates="posts")