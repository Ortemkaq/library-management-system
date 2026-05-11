-- Активные читатели
CREATE VIEW view_active_readers AS
SELECT 
    id,
    full_name,
    phone,
    email,
    registration_date
FROM readers
WHERE status = 'активен'
ORDER BY full_name;

-- Текущие выдачи с деталями
CREATE VIEW view_current_loans AS
SELECT 
    bl.id AS loan_id,
    r.full_name AS reader_name,
    b.title AS book_title,
    a.full_name AS author_name,
    e.full_name AS issued_by,
    bl.issue_date,
    bl.due_date,
    (bl.due_date - CURRENT_DATE) AS days_left,
    CASE 
        WHEN bl.due_date < CURRENT_DATE THEN 'ПРОСРОЧЕНА'
        ELSE 'в сроке'
    END AS status_text
FROM book_loans bl
JOIN readers r ON bl.reader_id = r.id
JOIN books b ON bl.book_id = b.id
LEFT JOIN authors a ON b.author_id = a.id
JOIN employees e ON bl.employee_id = e.id
WHERE bl.return_date IS NULL
ORDER BY bl.due_date;

-- Статистика по читателям (только те, кто брал больше 2 книг)
CREATE VIEW view_top_readers AS
SELECT 
    r.id,
    r.full_name,
    COUNT(bl.id) AS total_loans,
    COUNT(CASE WHEN bl.return_date IS NULL THEN 1 END) AS active_loans,
    COUNT(CASE WHEN bl.due_date < CURRENT_DATE AND bl.return_date IS NULL THEN 1 END) AS overdue_loans
FROM readers r
LEFT JOIN book_loans bl ON r.id = bl.reader_id
GROUP BY r.id, r.full_name
HAVING COUNT(bl.id) > 2
ORDER BY total_loans DESC;

-- Статистика по книгам (популярность)
CREATE VIEW view_book_popularity AS
SELECT 
    b.id,
    b.title,
    a.full_name AS author,
    COUNT(bl.id) AS times_borrowed,
    COUNT(DISTINCT bl.reader_id) AS unique_readers
FROM books b
LEFT JOIN authors a ON b.author_id = a.id
LEFT JOIN book_loans bl ON b.id = bl.book_id
GROUP BY b.id, b.title, a.full_name
HAVING COUNT(bl.id) > 0
ORDER BY times_borrowed DESC;