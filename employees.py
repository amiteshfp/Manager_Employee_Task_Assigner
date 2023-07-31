import sqlite3
from datetime import date, datetime
DATABASE = 'employees.db'
def create_connection():
    return sqlite3.connect(DATABASE)


def create_tables():
    with create_connection() as conn:
        cursor = conn.cursor()

        # USERS - user information - ID,NAME,PASSWORD,TYPE-MANAGER/EMPLOYEE
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                user_type TEXT NOT NULL
            )
        ''')

        # Create the tasks table to store task information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                due_date DATE,
                assignee INTEGER,
                status TEXT NOT NULL,
                FOREIGN KEY (assignee) REFERENCES users (id)
            )
        ''')

        conn.commit()

# Register a new user in the database
def register_user(username, password, user_type):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)', (username, password, user_type))
        conn.commit()

# Check user credentials during login
def check_user_credentials(username, password):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, user_type FROM users WHERE username = ? AND password = ?', (username, password))
        return cursor.fetchone()

# Create a new task in the database
def create_task(name, description, due_date, assignee, status):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (name, description, due_date, assignee, status) VALUES (?, ?, ?, ?, ?)',
                       (name, description, due_date, assignee, status))
        conn.commit()

# Mark a task as completed
def mark_task_completed(task_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET status = "completed" WHERE id = ?', (task_id,))
        conn.commit()

# mark task todo
def mark_task_todo(task_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET status = "todo" WHERE id = ?', (task_id,))
        conn.commit()

# Mark a task as in progress
def mark_task_inprogress(task_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET status = "inprogress" WHERE id = ?', (task_id,))
        conn.commit()

# Retrieve a task by its ID
def get_task(task_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))

        return cursor.fetchone()

# Update a task in the database
def update_task(task_id, name, description, due_date, assignee, status):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks
            SET name = ?, description = ?, due_date = ?, assignee = ?, status = ?
            WHERE id = ?
        ''', (name, description, due_date, assignee, status, task_id))
        conn.commit()

# Delete a task from the database
def delete_task(task_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()

# all tasks from the database
def get_all_tasks():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        cursor.execute("SELECT tasks.id, tasks.name, tasks.description, tasks.due_date, tasks.status, tasks.assignee, users.username FROM tasks LEFT JOIN users ON tasks.assignee = users.id")
        task_rows = cursor.fetchall()
        today = datetime.today().date()
        tasks = []
        for task_row in task_rows:
            task = {
                'id': task_row[0],
                'task_name': task_row[1],
                'description': task_row[2],
                'due_date': datetime.strptime(task_row[3], "%Y-%m-%d").date(),
                'status': task_row[4],
                'assignee': task_row[5],
                'username': task_row[6],
                'overdue': False
            }

            if (task['status'] == 'todo' or task['status']== 'inprogress') and task['due_date'] < today:
                task['overdue'] = True

            tasks.append(task)

        return tasks

# tasks assigned to a specific employee
def get_employee_tasks(employee_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE assignee = ?', (employee_id,))
        return cursor.fetchall()
    
# get all employees
def get_employees_list():
     with create_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_type='employee'")
        employees = cur.fetchall()
        return employees
    
# Call the function to create tables when this module is imported
create_tables()
