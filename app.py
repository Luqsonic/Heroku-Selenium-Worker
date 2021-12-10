import os
from flask import Flask, request, jsonify
from rq import Queue
from worker import conn
from utils import scrapeWebsite
import json
from time import sleep

app = Flask(__name__)
q = Queue(connection=conn)

def get_status(job):
    return 'Your Selenium job failed' if job.is_failed else 'your job is pending, please wait around 30 seconds for final result' if job.result == None else job.result

@app.route("/")
def handle_job():
    query_name = request.args.get('website')
    if query_name:
        job = q.enqueue(scrapeWebsite, query_name)
        output = get_status(job)

        while job.result == None:
            sleep(5)
        else:
            output = get_status(job)
    else:
        return "Please include a website url: ?website=yoururl"
    
    data = {"status":"complete","result":output}
    myJSON = jsonify(data)
    myJSON.headers["Content-Type"] = "application/json; charset=utf-8"
	#myJSON.headers["Transfer-Encoding"] = "chunked"
    myJSON.headers["Connection"] = "keep-alive"
    myJSON.headers["Access-Control-Allow-Origin"] = "*"
    myJSON.headers["Access-Control-Allow-Methods"] = "GET"
    myJSON.headers["Access-Control-Expose-Headers"] = "ETag, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset, Retry-After, Content-Length, Content-Range"
    myJSON.headers["Access-Control-Allow-Origin"] = "*"		
		  	
    return myJSON    

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
