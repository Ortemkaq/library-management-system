-- Добавление авторов
INSERT INTO authors (full_name, birth_year, country) VALUES
('Лев Толстой', 1828, 'Россия'),
('Федор Достоевский', 1821, 'Россия'),
('Александр Пушкин', 1799, 'Россия'),
('Стивен Кинг', 1947, 'США'),
('Джоан Роулинг', 1965, 'Великобритания');

-- Добавление жанров
INSERT INTO genres (name, description) VALUES
('Роман', 'Крупное эпическое произведение'),
('Детектив', 'Произведение о расследовании'),
('Фантастика', 'Произведения о вымышленных мирах'),
('Поэзия', 'Стихотворные произведения'),
('Ужасы', 'Произведения, вызывающие страх');

-- Добавление читателей
INSERT INTO readers (full_name, phone, email, status) VALUES
('Иванов Петр Сергеевич', '+7-999-111-22-33', 'ivanov@mail.ru', 'активен'),
('Петрова Анна Ивановна', '+7-999-222-33-44', 'petrova@mail.ru', 'активен'),
('Сидоров Алексей Владимирович', '+7-999-333-44-55', 'sidorov@mail.ru', 'активен'),
('Козлова Елена Дмитриевна', '+7-999-444-55-66', 'kozlova@mail.ru', 'активен'),
('Морозов Денис Андреевич', '+7-999-555-66-77', 'morozov@mail.ru', 'активен');

-- Добавление сотрудников
INSERT INTO employees (full_name, position) VALUES
('Смирнова Мария Ивановна', 'Библиотекарь'),
('Васильев Алексей Петрович', 'Старший библиотекарь'),
('Николаева Ольга Сергеевна', 'Администратор');

-- Добавление книг
INSERT INTO books (title, author_id, genre_id, year, pages, total_copies, available_copies) VALUES
('Война и мир', 1, 1, 2010, 1300, 3, 3),
('Преступление и наказание', 2, 1, 2015, 650, 2, 2),
('Евгений Онегин', 3, 4, 2018, 320, 2, 2),
('Оно', 4, 5, 2014, 1100, 2, 2),
('Гарри Поттер', 5, 3, 2016, 400, 3, 3),
('Анна Каренина', 1, 1, 2012, 850, 2, 2),
('Идиот', 2, 1, 2017, 600, 2, 2);

-- Добавление выдач
INSERT INTO book_loans (book_id, reader_id, employee_id, issue_date, due_date) VALUES
(1, 1, 1, CURRENT_DATE - 30, CURRENT_DATE - 16),
(2, 2, 1, CURRENT_DATE - 15, CURRENT_DATE - 1),
(3, 3, 2, CURRENT_DATE - 5, CURRENT_DATE + 9);


SELECT * FROM authors;
SELECT * FROM book_loans;
SELECT * FROM books;
SELECT * FROM employees;
SELECT * FROM genres;
SELECT * FROM readers;

