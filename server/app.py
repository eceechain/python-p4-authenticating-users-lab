from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):
    def delete(self):
        session['user_id'] = None
        response_dict = {
            'message': '200: OK'
        }
        response = make_response(
            jsonify(response_dict),
            200
        )
        return response

class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):
    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:
            article = Article.query.filter(Article.id == id).first()
            if article:
                article_json = jsonify(article.to_dict())
                return make_response(article_json, 200)
            else:
                return {'message': '404: Article not found'}, 404
        else:
            return {'message': '401: Maximum pageview limit reached'}, 401

class Login(Resource):
    def post(self):
        user = User.query.filter(User.username == request.get_json()['username']).first()
        if user:
            session['user_id'] = user.id
            response = make_response(
                jsonify(user.to_dict()),
                200
            )
            return response
        else:
            return {'message': '404: User not found'}, 404
    
class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        response_dict = {
            'message': 'No content'
        }
        response = make_response(
            jsonify(response_dict),
            204
        )
        return response
    
class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            if user:
                response = make_response(
                    jsonify(user.to_dict()),
                    200
                )
                return response
        response_dict = {
            'message': ' Not Authorized'
        }
        response = make_response(
            jsonify(response_dict),
            401
        )
        return response


api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')

if __name__ == "__main__":
    app.run(port=5555)
