PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS configs;
CREATE TABLE configs (
	automatic_enrollment BOOLEAN NOT NULL
);

DROP TABLE IF EXISTS department;
CREATE TABLE department (
	code TEXT PRIMARY KEY, 
	dept_name TEXT NOT NULL
);

DROP TABLE IF EXISTS instructor;
CREATE TABLE instructor (
	id INTEGER PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL
);

DROP TABLE IF EXISTS student;
CREATE TABLE student (
	id INTEGER PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL
);

DROP TABLE IF EXISTS course;
CREATE TABLE course (
	department_code TEXT NOT NULL REFERENCES department(code),
	course_no INTEGER NOT NULL,
	title TEXT NOT NULL,
	PRIMARY KEY (department_code, course_no)
);

CREATE TABLE class (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	dept_code TEXT NOT NULL,
	course_num INTEGER NOT NULL,
	section_no INTEGER NOT NULL,
	academic_year INTEGER NOT NULL,
	semester TEXT NOT NULL,
	instructor_id INTEGER NOT NULL REFERENCES instructor(id),
	room_num INTEGER NOT NULL,
	room_capacity INTEGER NOT NULL,
	course_start_date DATETIME NOT NULL,
	enrollment_start DATETIME NOT NULL,
	enrollment_end DATETIME NOT NULL,
	UNIQUE (dept_code, course_num, section_no, academic_year, semester),
	FOREIGN KEY (dept_code, course_num) REFERENCES course(department_code, course_no)
);

CREATE INDEX idx_room_capacity ON class (room_capacity);
CREATE INDEX idx_course_start_date ON class (course_start_date);
CREATE INDEX idx_enrollment_start ON class (enrollment_start);
CREATE INDEX idx_enrollment_end ON class (enrollment_end);
CREATE INDEX idx_class_instructor ON class(instructor_id);

DROP TABLE IF EXISTS enrollment;
CREATE TABLE enrollment (
	class_id INTEGER NOT NULL REFERENCES class(id) ON DELETE RESTRICT ON UPDATE CASCADE,
	student_id INTEGER NOT NULL REFERENCES student(id),
	enrollment_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(class_id, student_id)
);

DROP TABLE IF EXISTS waitlist;
CREATE TABLE waitlist (
	class_id INTEGER NOT NULL REFERENCES class(id) ON DELETE CASCADE ON UPDATE CASCADE,
	student_id INTEGER NOT NULL REFERENCES student(id),
	waitlist_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(class_id, student_id)
);

CREATE INDEX idx_waitlist_id_date ON waitlist(class_id, waitlist_date);
CREATE INDEX idx_waitlist_student ON waitlist(student_id);

DROP TABLE IF EXISTS droplist;
CREATE TABLE droplist (
	class_id INTEGER NOT NULL REFERENCES class(id) ON DELETE RESTRICT ON UPDATE CASCADE,
	student_id INTEGER NOT NULL REFERENCES student(id),
	drop_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	administrative BOOLEAN NOT NULL DEFAULT FALSE,
	PRIMARY KEY(class_id, student_id)
);

COMMIT;
