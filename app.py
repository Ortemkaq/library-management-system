from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = 'library_secret_key'

 
def get_db_connection():
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='postgres',
        database='library_system',
        cursor_factory=RealDictCursor
    )
    return conn

 
 
 

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    
     
    cur.execute("SELECT COUNT(*) as count FROM books")
    total_books = cur.fetchone()['count']
    
    cur.execute("SELECT SUM(available_copies) as count FROM books")
    available_books = cur.fetchone()['count'] or 0
    
    cur.execute("SELECT COUNT(*) as count FROM readers")
    total_readers = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) as count FROM book_loans WHERE return_date IS NULL")
    active_loans = cur.fetchone()['count']
    
     
    cur.execute("""
        SELECT bl.id, r.full_name as reader, b.title as book, bl.issue_date, bl.due_date, bl.return_date
        FROM book_loans bl
        JOIN readers r ON bl.reader_id = r.id
        JOIN books b ON bl.book_id = b.id
        ORDER BY bl.issue_date DESC
        LIMIT 5
    """)
    recent_loans = cur.fetchall()
    
    cur.close()
    conn.close()
    

    return render_template('index.html',
                         total_books=total_books,
                         available_books=available_books,
                         total_readers=total_readers,
                         active_loans=active_loans,
                         recent_loans=recent_loans,
                         today=date.today()) 

 
 
 

@app.route('/books')
def books():
    search = request.args.get('search', '')
    conn = get_db_connection()
    cur = conn.cursor()
    
    if search:
        cur.execute("""
            SELECT b.*, a.full_name as author_name, g.name as genre_name
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            LEFT JOIN genres g ON b.genre_id = g.id
            WHERE b.title ILIKE %s OR a.full_name ILIKE %s
            ORDER BY b.title
        """, (f'%{search}%', f'%{search}%'))
    else:
        cur.execute("""
            SELECT b.*, a.full_name as author_name, g.name as genre_name
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            LEFT JOIN genres g ON b.genre_id = g.id
            ORDER BY b.title
        """)
    
    books = cur.fetchall()
    
     
    cur.execute("SELECT id, full_name FROM authors ORDER BY full_name")
    authors = cur.fetchall()
    
    cur.execute("SELECT id, name FROM genres ORDER BY name")
    genres = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('books.html', books=books, authors=authors, genres=genres, search=search)

@app.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author_id = request.form.get('author_id') or None
        genre_id = request.form.get('genre_id') or None
        year = request.form.get('year') or None
        pages = request.form.get('pages') or None
        total_copies = int(request.form.get('total_copies', 1))
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO books (title, author_id, genre_id, year, pages, total_copies, available_copies)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (title, author_id, genre_id, year, pages, total_copies, total_copies))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Книга добавлена', 'success')
        return redirect(url_for('books'))
    
     
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, full_name FROM authors ORDER BY full_name")
    authors = cur.fetchall()
    cur.execute("SELECT id, name FROM genres ORDER BY name")
    genres = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('book_form.html', authors=authors, genres=genres, title="Добавление книги")

@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        title = request.form['title']
        author_id = request.form.get('author_id') or None
        genre_id = request.form.get('genre_id') or None
        year = request.form.get('year') or None
        pages = request.form.get('pages') or None
        total_copies = int(request.form.get('total_copies', 1))
        
         
        cur.execute("SELECT total_copies FROM books WHERE id = %s", (book_id,))
        old_total = cur.fetchone()['total_copies']
        diff = total_copies - old_total
        
        cur.execute("""
            UPDATE books 
            SET title = %s, author_id = %s, genre_id = %s, year = %s, pages = %s, 
                total_copies = %s, available_copies = available_copies + %s
            WHERE id = %s
        """, (title, author_id, genre_id, year, pages, total_copies, diff, book_id))
        conn.commit()
        flash('Книга обновлена', 'success')
        cur.close()
        conn.close()
        return redirect(url_for('books'))
    
     
    cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cur.fetchone()
    cur.execute("SELECT id, full_name FROM authors ORDER BY full_name")
    authors = cur.fetchall()
    cur.execute("SELECT id, name FROM genres ORDER BY name")
    genres = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('book_form.html', book=book, authors=authors, genres=genres, title="Редактирование книги")

@app.route('/books/delete/<int:book_id>')
def delete_book(book_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Книга удалена', 'warning')
    return redirect(url_for('books'))

 
 
 

@app.route('/readers')
def readers():
    search = request.args.get('search', '')
    conn = get_db_connection()
    cur = conn.cursor()
    
    if search:
        cur.execute("""
            SELECT * FROM readers 
            WHERE full_name ILIKE %s OR phone ILIKE %s
            ORDER BY full_name
        """, (f'%{search}%', f'%{search}%'))
    else:
        cur.execute("SELECT * FROM readers ORDER BY full_name")
    
    readers = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('readers.html', readers=readers, search=search)

@app.route('/readers/add', methods=['POST'])
def add_reader():
    full_name = request.form['full_name']
    phone = request.form.get('phone') or None
    email = request.form.get('email') or None
    status = request.form.get('status', 'активен')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO readers (full_name, phone, email, status)
        VALUES (%s, %s, %s, %s)
    """, (full_name, phone, email, status))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Читатель добавлен', 'success')
    return redirect(url_for('readers'))

@app.route('/readers/edit/<int:reader_id>', methods=['POST'])
def edit_reader(reader_id):
    full_name = request.form['full_name']
    phone = request.form.get('phone') or None
    email = request.form.get('email') or None
    status = request.form['status']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE readers 
        SET full_name = %s, phone = %s, email = %s, status = %s
        WHERE id = %s
    """, (full_name, phone, email, status, reader_id))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Данные читателя обновлены', 'success')
    return redirect(url_for('readers'))

@app.route('/readers/delete/<int:reader_id>')
def delete_reader(reader_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM readers WHERE id = %s", (reader_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Читатель удален', 'warning')
    return redirect(url_for('readers'))

 
 
 

@app.route('/loans')
def loans():
    status_filter = request.args.get('status', '')
    conn = get_db_connection()
    cur = conn.cursor()
    
    if status_filter and status_filter != 'все':
        cur.execute("""
            SELECT bl.*, r.full_name as reader_name, b.title as book_title
            FROM book_loans bl
            JOIN readers r ON bl.reader_id = r.id
            JOIN books b ON bl.book_id = b.id
            WHERE bl.status = %s
            ORDER BY bl.issue_date DESC
        """, (status_filter,))
    else:
        cur.execute("""
            SELECT bl.*, r.full_name as reader_name, b.title as book_title
            FROM book_loans bl
            JOIN readers r ON bl.reader_id = r.id
            JOIN books b ON bl.book_id = b.id
            ORDER BY bl.issue_date DESC
        """)
    
    loans = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('loans.html', loans=loans, status_filter=status_filter)

@app.route('/loans/add', methods=['GET', 'POST'])
def add_loan():
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        book_id = request.form['book_id']
        reader_id = request.form['reader_id']
        employee_id = request.form['employee_id']
        due_days = int(request.form.get('due_days', 14))
        
        issue_date = date.today()
        due_date = issue_date + timedelta(days=due_days)
        
        try:
            cur.execute("""
                INSERT INTO book_loans (book_id, reader_id, employee_id, issue_date, due_date)
                VALUES (%s, %s, %s, %s, %s)
            """, (book_id, reader_id, employee_id, issue_date, due_date))
            conn.commit()
            flash('Книга выдана', 'success')
        except Exception as e:
            flash(f'Ошибка: {str(e)}', 'danger')
        
        cur.close()
        conn.close()
        return redirect(url_for('loans'))
    
     
    cur.execute("SELECT id, full_name FROM readers WHERE status = 'активен' ORDER BY full_name")
    readers = cur.fetchall()
    
    cur.execute("SELECT id, title, available_copies FROM books WHERE available_copies > 0 ORDER BY title")
    books = cur.fetchall()
    
    cur.execute("SELECT id, full_name FROM employees ORDER BY full_name")
    employees = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('loan_form.html', readers=readers, books=books, employees=employees)

@app.route('/loans/return/<int:loan_id>')
def return_loan(loan_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE book_loans 
        SET return_date = CURRENT_DATE
        WHERE id = %s AND return_date IS NULL
    """, (loan_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Книга возвращена', 'success')
    return redirect(url_for('loans'))

 
 
 

@app.route('/authors')
def authors():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM authors ORDER BY full_name")
    authors = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('authors.html', authors=authors)

@app.route('/authors/add', methods=['POST'])
def add_author():
    full_name = request.form['full_name']
    birth_year = request.form.get('birth_year') or None
    country = request.form.get('country') or None
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO authors (full_name, birth_year, country)
        VALUES (%s, %s, %s)
    """, (full_name, birth_year, country))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Автор добавлен', 'success')
    return redirect(url_for('authors'))

@app.route('/authors/delete/<int:author_id>')
def delete_author(author_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM authors WHERE id = %s", (author_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Автор удален', 'warning')
    return redirect(url_for('authors'))

 
 
 

@app.route('/employees')
def employees():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees ORDER BY full_name")
    employees = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('employees.html', employees=employees)

@app.route('/employees/add', methods=['POST'])
def add_employee():
    full_name = request.form['full_name']
    position = request.form['position']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO employees (full_name, position, hire_date)
        VALUES (%s, %s, CURRENT_DATE)
    """, (full_name, position))
    conn.commit()
    cur.close()
    conn.close()
    
    flash('Сотрудник добавлен', 'success')
    return redirect(url_for('employees'))

@app.route('/employees/delete/<int:employee_id>')
def delete_employee(employee_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Сотрудник удален', 'warning')
    return redirect(url_for('employees'))

 
 
 

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/reports/active_readers')
def report_active_readers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM view_active_readers")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('report_results.html', 
                         report_name="Активные читатели",
                         data=data,
                         columns=['full_name', 'phone', 'email', 'registration_date'])

@app.route('/reports/current_loans')
def report_current_loans():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM view_current_loans")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('report_results.html',
                         report_name="Текущие выдачи",
                         data=data,
                         columns=['reader_name', 'book_title', 'author_name', 'issue_date', 'due_date', 'days_left', 'status_text'])

@app.route('/reports/top_readers')
def report_top_readers():
    min_loans = request.args.get('min_loans', 2, type=int)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM view_top_readers 
        WHERE total_loans >= %s
        ORDER BY total_loans DESC
    """, (min_loans,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('report_results.html',
                         report_name=f"Топ читателей (более {min_loans} книг)",
                         data=data,
                         columns=['full_name', 'total_loans', 'active_loans', 'overdue_loans'])

@app.route('/reports/popular_books')
def report_popular_books():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM view_book_popularity LIMIT 20")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('report_results.html',
                         report_name="Самые популярные книги",
                         data=data,
                         columns=['title', 'author', 'times_borrowed', 'unique_readers'])

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)