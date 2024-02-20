from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)
Conversation = []

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        question = request.form['question']
        Conversation.insert(0, "Please code the backend")
        Conversation.insert(1, question)
        return redirect('/')
    else:
        return render_template('index.html', Conversation=Conversation)

if __name__ == "__main__":
    app.run()