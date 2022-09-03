import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10

# general function to create pagination in large data

def create_pagination(request, selected_data):
  page = request.args.get('page', 1, type=int)

  start_index = (page-1) * QUESTIONS_PER_PAGE;
  end_index = start_index + QUESTIONS_PER_PAGE

  format_selection = [question.format() for question in selected_data]

  current_selection = format_selection[start_index:end_index]

  return current_selection

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE"
        )
        response.headers.add(
          "Access-Control-Allow-Origin", "*"
        )
        return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_all_categories():
    all_category =  Category.query.all()

    formatted_category={}

 
    if not all_category:
      abort(404) # if no category, then the api returns 404 not found

    else:
     
      for category in all_category:
        formatted_category[category.id] = category.type

      return jsonify({
      'success': True,
      'categories':  formatted_category,
      'current_category': None
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    all_questions =   Question.query.all()
    all_category =  Category.query.all()

   


    formatted_category = {}

    for category in all_category:
      formatted_category[category.id] = category.type

    if all_questions:
      current_selection= create_pagination(request, all_questions)
      return jsonify({
      'status': True,
      'categories': formatted_category,
      'questions': current_selection,
      'total_questions': len(all_questions),
      'current_category': None
    })

    else:
      abort(404)
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])

  def delete_question(id):
    question = Question.query.filter(Question.id == id).one_or_none();

    if not question:
      abort(422)
    else:
      question.delete()

      questions = Question.query.order_by(Question.id).all()
      current_questions = create_pagination(request, questions)

      return jsonify({
        'status':True,
        'deleted question':id,
        'questions': current_questions,
        'total': len(questions)
      })
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
 
 
  @app.route('/questions', methods=['POST'])
  def create_question():
            body = request.get_json()
    
            question = body.get('question', None);
            answer = body.get('answer', None);
            difficulty = body.get('difficulty', None);
            category = body.get('category',  None);
            try:

                    new_question = Question(
                        question=question, 
                        answer=answer, 
                        difficulty=difficulty, 
                        category=category
                      )
                    new_question.insert()

                    questions = Question.query.order_by(Question.id).all()
                    questions = create_pagination(request, questions)

                    return jsonify({
                        'success': True,
                        'created_id':new_question.id,
                        'question_created': new_question.question,
                        'questions': questions,
                        'total_questions': len(questions)
                    })
            except:
                abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/searchquestions', methods=['POST'])
  def search_questions(): 
    body = request.get_json()
    searchTerm = body.get('searchTerm', None);

    try:
      questions = Question.query.filter(Question.question.ilike('%{}%'.format(searchTerm))).all()
      paginate_quiz = create_pagination(request, questions);
                      
      return jsonify({
            'success': True,
            'questions':  paginate_quiz,
            'total_questions': len(Question.query.all()),
            'current_category': 'Science'
          });

    except Exception as e:
      print(e)
      abort(405)


    
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def filter_questions(category_id):

    all_questions = Question.query.filter(Question.category==category_id).all()
    print(all_questions)
    if all_questions:

      selected_questions = create_pagination(request, all_questions)
      return jsonify({
      'status':True,
      'questions':selected_questions,
      'total_questions': len(all_questions),
      'current_category':None
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

  @app.route('/quizzes', methods=['POST'])
  def play_quizz():

      try:
        body = request.get_json()
        prev_quiz= body.get('previous_questions', None)
        category = body.get('quiz_category', None)
    
        if category['id'] != 0:

            questions = Question.query.filter_by(category=category['id']).filter(Question.id.notin_((prev_quiz))).all()    
        else:
            questions = Question.query.filter(Question.id.notin_((prev_quiz))).all()
        
        if len(questions) > 0:
            next_quiz = random.choice(questions).format()
        

        return jsonify({
      'success':True,
      'questions':next_quiz
      })

      except:
        abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404) 
  def not_found(error):
    return jsonify({
      'status':False,
      'error': 404,
      'message': 'Not Found'
    })


  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal server error'
    })

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
    'status': False,
    'error': 405,
    'message': 'Method Not allowed'
  })

  @app.errorhandler(422)
  def not_allowed(error):
    return jsonify({
      'status': False,
      'error': 422,
      'message': 'Unprocessible'
    })

  @app.errorhandler(400) 
  def bad_request_error(error):
    return jsonify({
      'status': False,'error':400,'message':'bad request'
    })
  return app

 
