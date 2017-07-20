from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, Unicode
from tgsamplecontacts.model import DeclarativeBase


class Contact(DeclarativeBase):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    first_name = Column(Unicode(80), nullable=False)
    last_name = Column(Unicode(80), nullable=True)
    # As it's a 1:1 relationship, the number may also be added here
    numbers = relationship('Number', uselist=False)

    user_id = Column(Integer, ForeignKey('tg_user.user_id'), nullable=False)
    user = relationship('User')
