# Migration Exercise Starter

This exercise gives you practice setting up and using Flask-Migrate in an existing Flask + SQLAlchemy project.

You are not building a brand-new domain model.
Instead, you are taking an existing application and learning how to evolve its database schema safely.

---

## Learning goals

By the end of this exercise, you should be able to:

- initialize SQLAlchemy and Flask-Migrate in a Flask app
- create an initial database migration from existing models
- apply that migration to a database
- update a model by adding a new column
- generate and apply a second migration
- update route logic so the API supports the new column

## Starter location

Work inside:

```text
src/migration_exercises/
```

---
## Part 1: Install dependencies

Confirm that requirements.txt includes:

- Flask
- Flask-SQLAlchemy
- Flask-Migrate

create a virtual environment and install dependencies by running in the terminal from the project root:

```bash
pip install -r requirements.txt
```

## Part 2: Complete the app setup TODOs

Open `src/migration_exercises/app.py`.

### TODO 1

Initialize SQLAlchemy with the app.

### TODO 2

Initialize Flask-Migrate with the app and database.

When you are done, your app factory should connect both extensions.

## Part 3: Complete the manage file TODO

Open `src/migration_exercises/manage.py`.

### TODO 3

Import the database object and the models so Flask-Migrate can see them.
Why is this important?
Flask-Migrate compares the database schema to the SQLAlchemy models it knows about. If the models are never imported, migration detection may not work correctly.

## Part 4: Run the initial migration workflow

From the project root, run:
```bash
flask --app src.migration_exercises.manage db init
```
This creates the migrations/ folder.
Add it to git so it is tracked by version control:
```bash
git add src/migration_exercises/migrations
```

Then generate the initial migration:
```bash
flask --app src.migration_exercises.manage db migrate -m "initial schema"
```
Then apply it:
```bash
flask --app src.migration_exercises.manage db upgrade
``` 
At this point, your database should contain these tables:

- students
- assignments
- grades

## Part 5: Start the app and test the starter API

Run:
```bash
flask --app src.migration_exercises.manage run
```
## Test a few endpoints.

### Create a student

From postman or curl, send:
```html
POST /exercises/students
Content-Type: application/json
{
"name": "Ava",
"email": "ava@example.com"
}
Create an assignment
POST /exercises/assignments
Content-Type: application/json
{
"title": "ORM Practice",
"max_score": 100
}
Create a grade
POST /exercises/grades
Content-Type: application/json
{
"score": 95,
"student_id": 1,
"assignment_id": 1
}

```

### Part 6: Evolve the schema

Now pretend the client has changed the requirements.
```text
The school wants to support assignment due dates and allow teachers to leave a short comment on each grade.
```
This is more realistic than adding one extra text field to Student, because it affects two different parts of the schema:

- Assignment needs a due_date
- Grade needs a comment

Open src/migration_exercise/models.py.

### TODO 5

Add this new column to Assignment:
```python
due_date = db.Column(db.Date, nullable=True)
```

### TODO 6

Add this new column to Grade:
```python
comment = db.Column(db.String(200), nullable=True)
```
These changes update the Python models, but not yet the actual database tables.

### Part 7: Generate a second migration

After adding the new model fields, run:
```bash
flask --app src.migration_exercise.manage db migrate -m "add due_date to assignment and comment to grade"
```
Then apply it:
```bash
flask --app src.migration_exercise.manage db upgrade
```
Open the generated migration file and inspect it.

You should see logic that adds:

- a due_date column to the assignments table
- a comment column to the grades table

## Part 8: Update the JSON output

Open src/migration_exercises/models.py.

### TODO 8

 - Update Assignment.to_dict() so that the new due_date field appears in the JSON response.

Since due_date is a Python date object, convert it to a string before returning it.

One common pattern is:

"due_date": self.due_date.isoformat() if self.due_date else None
### TODO 9

Update Grade.to_dict() so that the new comment field appears in the JSON response.

After that:

GET /exercies/assignments should include due_date

GET /exercies/grades should include comment

Part 9: Update the POST routes

Open src/migration_exercises/routes.py.

### TODO 10

Modify the POST /exercises/assignments route so it accepts due_date from the request body.

Use ISO format strings such as:
```html
{
"title": "ORM Practice2",
"max_score": 100,
"due_date": "2026-04-01"
}
```
You will need to convert that string into a Python date object before storing it.

Hint:

from datetime import date
parsed_date = date.fromisoformat(due_date_string)
### TODO 11

Modify the POST /exercises/grades route so it accepts an optional comment from the request body.

Example request:
```html
{
"score": 95,
"student_id": 1,
"assignment_id": 1,
"comment": "Great improvement from last week"
}
```
## Part 10: Verify the new schema through the API

Start the app again if needed:
```bash
flask --app src.migration_exercises.manage run
```
Now create an assignment with a due date:
```html
POST /exercises/assignments
Content-Type: application/json
{
"title": "ORM Practice2",
"max_score": 100,
"due_date": "2026-04-01"
}
```
Then create a grade with a comment:
```html
POST /exercises/grades
Content-Type: application/json
{
"score": 95,
"student_id": 1,
"assignment_id": 1,
"comment": "Great improvement from last week"
}
```
Then test in browser or postman that the new fields appear in the responses for:

GET /exercises/assignments

and

GET /exercises/grades

Make sure the responses include the new fields.

Reflection questions

Answer these in your own words.
- Why is changing the SQLAlchemy model not enough by itself?
SQLAlchemy models are just python code. You have to make sql commands to change the database.
- What is the purpose of the migrations/ folder?
- it acts as a version control system for the database schema. it keeps a chronological history of evry change made to the database to allow developers to upgrade or downgrade their database states safely and consistently.
- Why is db upgrade safer than deleting and recreating the database?
- deleting and recreating a database destroys all the user data inside of it. dp upgrade modifies the structure of the tables while keeping all the existing rows and data perfectly intact.
- Why do date columns usually need conversion before being returned in JSON?
json doesnt support a date data type so it needs to be converted to a string before being transmitted as json
What could go wrong if a production database already contains real data?
if you add a new column and set it to nullable-False, the database will reject the migration. You either have to make a new column or provide a default value to the existing rows.