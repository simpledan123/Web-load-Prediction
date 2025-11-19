from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# [기본]
class PostBase(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None  # 이미지는 없을 수도 있음 (Optional)

# [생성]
class PostCreate(PostBase):
    pass

# [응답]
class Post(PostBase):
    id: int
    user_id: int
    likes: int
    created_at: datetime

    class Config:
        from_attributes = True