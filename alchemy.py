from sqlalchemy import create_engine
from sqlalchemy import text


engine = create_engine("mysql+pymysql://user:password@host/dbname")
