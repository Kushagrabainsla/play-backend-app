from play_backend_app import app
import os
            
@app.route('/demoApi1')
def demoApi1():
    SECRET_KEY = os.getenv("MY_SECRET")
    return 'DEMO API 1 IS {secret}'.format(secret=SECRET_KEY)
