import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.new_question = {
                "question":"What chemical has formalu Na?",
                "answer":"Sodium",
                "category": "Science",
                "Difficulty": 2
                }
        # self.database_path = "postgres://{}/{}".format('localhost:5000', self.database_name)
        self.database_path = "postgresql://postgres:19alema@localhost:5432/trivia_test"
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
           
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
      
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["status"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
    
    def test_404_request_beyond_valid_page(self):
        res = self.client().get("/questions?page=100000")
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["status"], False)
        self.assertEqual(data["message"], " Not found")



    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["status"], True)
        self.assertTrue(data["question_created"])

    def test_delete_question(self):
        res = self.client().delete("/questions/7")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 7).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["status"], True)
        self.assertEqual(data["deleted question"], 7)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_422_for_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["status"], False)



    def test_get_questions_search_with_results(self):
        res = self.client().post("/searchquestions", json={"searchTerm": "medicine"})
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
       

    def test_get_questions_search_without_results(self):
        res = self.client().post("/searchquestions", json={"searchTerm": "11 "})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"], 0)



    def test_get_question_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['status'], True)
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['total_questions', 2])

    def test_get_question_by_category_not_found(self):
        res = self.client().get('/categories/88/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')



    def test_play_quiz(self):
        res = self.client().post('/quizzes', json={'quiz_category':1, 'previous_questions':[]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['status'], True)
        self.assertTrue(data['question'])
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()