import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import traceback

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(selection, request):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  paginated_questions = selection[start: end]
  formated_questions = [question.format() for question in paginated_questions]
  return formated_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)



  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response



  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    categories_formated = {category.id: category.type for category in categories}

    return jsonify({
      'success': True,
      'categories': categories_formated,
      'total_categories': len(categories_formated)
    })



  @app.route('/questions')
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    paginated_questions = paginate_questions(selection, request)

    if len(paginated_questions) == 0:
      abort(404)

    categories = Category.query.order_by(Category.id).all()
    formated_categories = {category.id: category.type for category in categories}

    return jsonify({
      'success': True,
      'questions': paginated_questions,
      'total_questions': len(selection),
      'categories': formated_categories,
      'current_category': None
    })


  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.get(question_id)

    if question is None:
      abort(404)

    question.delete()

    return jsonify({
      'success': True,
      'deleted': question_id,
      'total_questions': len(Question.query.all())
    })



  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()

    question = body.get('question')
    answer = body.get('answer')
    category = body.get('category')
    difficulty = body.get('difficulty')

    search_term = body.get('searchTerm')

    try:
      if search_term:
        result = Question.query.order_by(Question.id).filter(Question.question.ilike('%' + search_term + '%'))
        current_questions = paginate_questions(result, request)

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(result.all())
        })
      else:
        question_record = Question(
          question = question,
          answer = answer,
          category = category,
          difficulty = difficulty
        )
        question_record.insert()

        return jsonify({
          'success': True,
          'created': question_record.id,
          'total_questions': len(Question.query.all())
        })
    except:
      traceback.print_exc()
      abort(422)



  @app.route('/categories/<int:category_id>/questions')
  def get_questions_of_category(category_id):
    question = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
    current_questions = paginate_questions(question, request)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(question),
      'current_category': category_id
    })



  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

  return app

