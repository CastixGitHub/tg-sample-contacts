from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String
from tgsamplecontacts.model import DeclarativeBase


class Number(DeclarativeBase):
    __tablename__ = 'numbers'

    id = Column(Integer, primary_key=True)
    number = Column(String(20), nullable=False)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    contact = relationship("Contact", back_populates='numbers')
