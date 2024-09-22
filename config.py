# config.py
class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:@localhost:3306/forecasting_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
