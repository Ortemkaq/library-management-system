-- Обновляет available_copies в books при выдаче/возврате

CREATE OR REPLACE FUNCTION update_book_availability()
RETURNS TRIGGER AS $$
BEGIN
    -- При выдаче книги
    IF TG_OP = 'INSERT' THEN
        UPDATE books 
        SET available_copies = available_copies - 1
        WHERE id = NEW.book_id;
        
        -- Проверяем, что книга доступна
        IF (SELECT available_copies FROM books WHERE id = NEW.book_id) < 0 THEN
            RAISE EXCEPTION 'Нет доступных экземпляров книги';
        END IF;
        
        RETURN NEW;
    
    -- При возврате книги
    ELSIF TG_OP = 'UPDATE' AND NEW.return_date IS NOT NULL AND OLD.return_date IS NULL THEN
        UPDATE books 
        SET available_copies = available_copies + 1
        WHERE id = NEW.book_id;
        
        RETURN NEW;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_loans_availability
    AFTER INSERT OR UPDATE OF return_date ON book_loans
    FOR EACH ROW
    EXECUTE FUNCTION update_book_availability();


-- Автоматически обновляет статус выдачи и блокирует читателя при просрочке

CREATE OR REPLACE FUNCTION check_overdue_and_block()
RETURNS TRIGGER AS $$
DECLARE
    v_overdue_count INTEGER;
BEGIN
    -- При вставке или обновлении даты возврата
    IF TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND NEW.return_date IS NULL) THEN
        -- Проверяем, не просрочена ли выдача
        IF NEW.due_date < CURRENT_DATE THEN
            NEW.status := 'просрочена';
        END IF;
    END IF;
    
    -- При возврате проверяем просрочку
    IF TG_OP = 'UPDATE' AND NEW.return_date IS NOT NULL AND OLD.return_date IS NULL THEN
        IF NEW.return_date > OLD.due_date THEN
            -- Можно добавить запись о штрафе (но у нас нет таблицы fines)
            NEW.status := 'возвращена с опозданием';
        ELSE
            NEW.status := 'возвращена';
        END IF;
    END IF;
    
    -- Проверяем, не заблокировать ли читателя (если больше 3 просрочек)
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        SELECT COUNT(*) INTO v_overdue_count
        FROM book_loans
        WHERE reader_id = NEW.reader_id
        AND status = 'просрочена'
        AND return_date IS NULL;
        
        IF v_overdue_count >= 3 THEN
            UPDATE readers 
            SET status = 'заблокирован'
            WHERE id = NEW.reader_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_loans_status
    BEFORE INSERT OR UPDATE ON book_loans
    FOR EACH ROW
    EXECUTE FUNCTION check_overdue_and_block();

-- Проверяет, что читатель не заблокирован при выдаче

CREATE OR REPLACE FUNCTION check_reader_not_blocked()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF EXISTS (
            SELECT 1 FROM readers 
            WHERE id = NEW.reader_id AND status = 'заблокирован'
        ) THEN
            RAISE EXCEPTION 'Читатель заблокирован, выдача невозможна';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_loans_check_reader
    BEFORE INSERT ON book_loans
    FOR EACH ROW
    EXECUTE FUNCTION check_reader_not_blocked();