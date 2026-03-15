-- Таблица авторов
CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    birth_year INTEGER,
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица жанров
CREATE TABLE genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- Таблица читателей
CREATE TABLE readers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) UNIQUE,
    email VARCHAR(100) UNIQUE,
    registration_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'активен',
    CONSTRAINT check_reader_status CHECK (status IN ('активен', 'заблокирован'))
);

-- Таблица книг
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author_id INTEGER,
    genre_id INTEGER,
    year INTEGER,
    pages INTEGER,
    total_copies INTEGER DEFAULT 1,
    available_copies INTEGER DEFAULT 1,
    CONSTRAINT fk_books_author FOREIGN KEY (author_id) 
        REFERENCES authors(id) ON DELETE SET NULL,
    CONSTRAINT fk_books_genre FOREIGN KEY (genre_id) 
        REFERENCES genres(id) ON DELETE SET NULL,
    CONSTRAINT check_year CHECK (year BETWEEN 1400 AND EXTRACT(YEAR FROM CURRENT_DATE)),
    CONSTRAINT check_pages CHECK (pages > 0),
    CONSTRAINT check_copies CHECK (available_copies >= 0 AND available_copies <= total_copies)
);

-- Таблица сотрудников
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    position VARCHAR(50) NOT NULL,
    hire_date DATE DEFAULT CURRENT_DATE
);


-- Таблица выдачи книг (связывает все сущности)
CREATE TABLE book_loans (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    reader_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE,
    status VARCHAR(20) DEFAULT 'выдана',
    CONSTRAINT fk_loans_book FOREIGN KEY (book_id) 
        REFERENCES books(id) ON DELETE RESTRICT,
    CONSTRAINT fk_loans_reader FOREIGN KEY (reader_id) 
        REFERENCES readers(id) ON DELETE RESTRICT,
    CONSTRAINT fk_loans_employee FOREIGN KEY (employee_id) 
        REFERENCES employees(id) ON DELETE RESTRICT,
    CONSTRAINT check_dates CHECK (due_date > issue_date),
    CONSTRAINT check_return_date CHECK (return_date IS NULL OR return_date >= issue_date),
    CONSTRAINT check_loan_status CHECK (status IN ('выдана', 'возвращена', 'просрочена'))
);

-- Индексы
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author_id);
CREATE INDEX idx_books_genre ON books(genre_id);
CREATE INDEX idx_readers_name ON readers(full_name);
CREATE INDEX idx_readers_phone ON readers(phone);
CREATE INDEX idx_book_loans_dates ON book_loans(issue_date, due_date);
CREATE INDEX idx_book_loans_status ON book_loans(status);
CREATE INDEX idx_book_loans_reader ON book_loans(reader_id);

