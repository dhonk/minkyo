from flask import Flask, render_template
import os

app = Flask(__name__, 
    template_folder='./src',
    static_folder='./src/static',
    static_url_path='/static')
print(os.getcwd())

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000) 