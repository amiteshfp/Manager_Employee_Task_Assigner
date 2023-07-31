from flask import Flask, render_template, request, redirect, url_for, session
import employees
from datetime import date

app = Flask(__name__)
app.secret_key = 'newapp_4623'

#check if the user is logged in as a manager
def is_manager():
    return 'user_type' in session and session['user_type'] == 'manager'

#check if the user is logged in as an employee
def is_employee():
    return 'user_type' in session and session['user_type'] == 'employee'

# Route for home page
@app.route('/')
def home():
    login_link = '/login'
    register_link = '/register'
    if 'user_id' in session:
        # If the user is logged in
        if is_manager():
            return redirect(url_for('manager_view'))
        elif is_employee():
            return redirect(url_for('employee_view'))
    else:
        # If the user is not logged in
        return f"Welcome to the Todo Application! <br> <a href='{login_link}'>Login</a> | <a href='{register_link}'>Register</a>"
    

# Route for manager to assign a task
@app.route('/assign_task', methods=['GET', 'POST'])
def assign_task():
    employees_lists = employees.get_employees_list()
    if not is_manager():
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['task_name']
        description = request.form['description']
        due_date = request.form['due_date']
        assignee = request.form['assignee']
        status = 'todo'

        employees.create_task(name, description, due_date, assignee, status)
        return redirect(url_for('manager_view'))
    else:
        return render_template('assign_task.html', employees=employees_lists)

# Route to mark a task as "To Do"
@app.route('/mark_todo/<int:task_id>')
def mark_todo(task_id):
    if not is_employee():
        return redirect(url_for('login'))

    employees.mark_task_todo(task_id)
    return redirect(url_for('employee_view'))


@app.route('/mark_inprogress/<int:task_id>')
def mark_inprogress(task_id):
    if not is_employee():
        return redirect(url_for('login'))

    employees.mark_task_inprogress(task_id)
    return redirect(url_for('employee_view'))

# Route to mark a task as "Completed"
@app.route('/mark_completed/<int:task_id>')
def mark_completed(task_id):
    if not is_employee():
        return redirect(url_for('login'))

    employees.mark_task_completed(task_id)
    return redirect(url_for('employee_view'))


# Route for manager to edit a task
@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if not is_manager():
        return redirect(url_for('login'))

    task = employees.get_task(task_id)
    if not task:
        return "Task not found"

    employees_edit_list = employees.get_employees_list()

    if request.method == 'POST':
        # Handle form submission to update the task
        name = request.form['task_name']
        description = request.form['description']
        due_date = request.form['due_date']
        assignee = request.form['assignee']
        status = request.form['status']

        employees.update_task(task_id, name, description, due_date, assignee, status)
        return redirect(url_for('manager_view'))
    else:
        # Render the form with the task details and dynamically fetched employees
        return render_template('edit_task.html', task=task, employees=employees_edit_list)


# manager - delete a task
@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if not is_manager():
        return redirect(url_for('login'))

    employees.delete_task(task_id)
    return redirect(url_for('manager_view'))

# manager view - see all tasks
@app.route('/manager_view')
def manager_view():
    if not is_manager():
        return redirect(url_for('login'))

    tasks = employees.get_all_tasks()
    return render_template('manager_view.html', tasks=tasks)

# view all employees
@app.route('/view_employees')
def view_employees():
    if not is_manager():
        return redirect(url_for('login'))

    employees_list = employees.get_employees_list()
    return render_template('view_employees.html', employees=employees_list)

# employee view - see assigned tasks
@app.route('/employee_view')
def employee_view():
    if not is_employee():
        return redirect(url_for('login'))
    
    employee_tasks = employees.get_employee_tasks(session['user_id'])
    return render_template('employee_view.html', employee_tasks=employee_tasks)

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = 'manager' if request.form.get('user_type') == 'manager' else 'employee'

        employees.register_user(username, password, user_type)
        return redirect(url_for('login'))
    else:
        return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = employees.check_user_credentials(username, password)
        if user_data:
            session['user_id'] = user_data[0]
            session['user_type'] = user_data[1]
            return redirect(url_for('manager_view')) if is_manager() else redirect(url_for('employee_view'))

    return render_template('login.html')

# Route for user logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
