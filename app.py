from flask import Flask
from application.database import db
app=None

# App description and config
def create_app():
    app=Flask(__name__)
    app.debug=True
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///hospital_management.sqlite3'
    db.init_app(app)
    app.app_context().push()
    return app 

app=create_app()
from application.controllers import * # routes are imported after app creation.

if __name__ == "__main__":
    # db.create_all()
    # user1=User(username="admin123",password="password",type=0)
    # db.session.add(user1)
    # db.session.commit()
    # if User.query.filter_by(username="admin123").first():
    #     admin1=Admin(id=user1.id,username=user1.username,password=user1.password)
    #     db.session.add(admin1)
    #     db.session.commit()
    app.run()

# When we run this app module, it will create a proxy object as current_app which we will import in 
# controllers.py to avoid circular imports and error mapping.
