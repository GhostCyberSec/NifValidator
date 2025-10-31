from flask import Flask, request, render_template
import nif_validator as nif

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('index.html', result="")

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    result = nif.valida_nif(text)
    return render_template('index.html', result=result)

app.run(host="0.0.0.0", port='9046')