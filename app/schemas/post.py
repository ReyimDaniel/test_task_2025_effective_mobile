from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    tittle: str
    description: str


class PostCreate(PostBase):
    # required_access_id: int
    pass


class PostRead(BaseModel):
    id: int
    tittle: str
    description: str
    required_access_id: int
    owner_id: int

    class Config:
        from_attributes = True


class PostUpdate(PostBase):
    tittle: str | None = None
    description: str | None = None
    required_access_id: int | None = None


# class PostUpdatePartial(BaseModel):
#     tittle: str | None = None
#     description: str | None = None
#     required_access_id: int | None = None

class Post(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
