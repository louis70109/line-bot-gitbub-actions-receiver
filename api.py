from utils import sqlite
from controller.image_controller import ImageController
from controller.line_controller import LineController
from flask_restful import Api
from flask_cors import CORS
from flask import Flask, request
import logging
import os

from utils.datetimeutil import compare_time_arrange_mins, utc_to_tpe

debug = False
if os.getenv('PY_ENV') != 'production':
    from dotenv import load_dotenv
    load_dotenv()
    debug = True


logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)

api = Api(app)


@app.get("/")
def check():
    return {"message": "Hello World!"}


@app.post("/github")
def github_webhook():
    check_run = request.json.get('check_run')
    complete_date = check_run.get('completed_at')
    if check_run is not None:
        status = check_run.get('status')
        job = check_run.get('details_url')
    if complete_date is not None:
        repo = request.json.get('repository').get('full_name')
        logger.debug('Deploy status: '+status)
        logger.debug('Deploy Job: '+job)
        logger.debug('Deploy Repo: '+repo)
        logger.debug('complete_date: '+complete_date)

        try:
            with sqlite.connect() as con:
                select_query = sqlite.exec_one(
                    con,
                    f"SELECT * from github_actions WHERE repo = '{repo}';")
                logger.info('Select: '+str(select_query))
                if select_query is not None:
                    result = compare_time_arrange_mins(select_query['completed_at'], complete_date)
                    logger.debug(result)
            if select_query is None:
                with sqlite.connect() as con:
                    sqlite.insert(
                        con,
                        f"INSERT INTO github_actions (repo, job, completed_at) VALUES ('{repo}', '{job}','{complete_date}');")
            else:
                with sqlite.connect() as con:
                    sqlite.insert(
                        con,
                        f"UPDATE github_actions SET repo = '{repo}', job = '{job}', completed_at = '{complete_date}';")
        except Exception as e:
            logger.warning(e)
    return {"status": "200"}


api.add_resource(LineController, '/webhooks/line')
api.add_resource(ImageController, '/image')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'), debug=debug)
