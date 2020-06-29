from flask import Flask, request
from functools import wraps
import os, logging, subprocess
from timeit import default_timer as timer

app = Flask(__name__)

def logged(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        log.debug(f.__name__)
        return f(*args, **kwargs)
    return decorated

def load_files():    
    return os.listdir(scripts_path)

def run_script(fullname):
    start = timer()
    output = subprocess.run([fullname], check=True, capture_output=True)
    timespan = timer() - start

    decoded_output = output.stdout.decode("utf-8") 

    return decoded_output, timespan

def page(title, content):
    return f'''
<html>
    <head>
        <title>{title}</title>
        <style>
            body{{ font-family:monospace }}
            pre{{ font-size: 8pt }}
            ul{{ list-style: decimal;  }}
        </style>
    </head>
    <body>
    {content}
    </body>
</html>
'''

@app.route('/')
@logged
def index():
    content = f'''
<div>available scripts:</div>
<ul>
'''

    for script in load_files():
        content += f'''
<li>
    <a 
        href="run?name={script}" 
        onclick="return confirm('Are you sure you want to execute {script}?')">
        
        {script}
    </a>
</li>
'''

    content += '</ul>'

    return page('scripts', content)

@app.route('/run')
@logged
def run():
    name = request.args.get('name')

    if name not in load_files():
        return '['+name+'] not found'

    fullname = scripts_path + name

    script_output, span = run_script(fullname)

    return page('output', f'''
<div>{fullname}</div>
<div>elapsed: {span}s</div>
<pre>{script_output}</pre>
''')

#https://blog.sneawo.com/blog/2017/12/20/no-cache-headers-in-flask/
@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.errorhandler(Exception)
def all_exception_handler(error):
    log.debug(error)
    return 'Error', 500

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, filename='log.txt')
    log = logging.getLogger(os.path.basename(__file__))
    
    scripts_path = os.path.dirname(os.path.realpath(__name__)) + '/scripts/'

    app.run(debug=True, port=5000)