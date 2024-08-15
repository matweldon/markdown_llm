from flask import Flask, request, jsonify, render_template
import json

app = Flask(__name__)

TASKS_FILE = 'tasks.json'

def read_tasks():
    try:
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def write_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f)

@app.route('/')
def index():
    return render_template('index.html', tasks=read_tasks())

@app.route('/add-task', methods=['POST'])
def add_task():
    task = request.form.get('task')
    if task:
        tasks = read_tasks()
        tasks.append({"id": len(tasks) + 1, "text": task})
        write_tasks(tasks)
        return render_template('task.html', task=tasks[-1])
    return '', 400

@app.route('/delete-task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = read_tasks()
    tasks = [task for task in tasks if task['id'] != task_id]
    write_tasks(tasks)
    return '', 200

if __name__ == '__main__':
    app.run(debug=True)
