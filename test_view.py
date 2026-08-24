from app import app
from flask import session
import traceback

app.config['TESTING'] = True
client = app.test_client()

try:
    with client as c:
        with c.session_transaction() as sess:
            sess['pending_registration_username'] = 'brianfe25_1455'
        
        r = c.get('/download-registration-pdf/brianfe25_1455?preview=1')
        print("Status Code:", r.status_code)
        print("Headers:", r.headers)
        print("Data Length:", len(r.data))
        if r.status_code != 200:
            print("Response Data:", r.data[:500])
except Exception as e:
    print("Error during view execution:")
    traceback.print_exc()
