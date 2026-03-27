-- FitLife Database Schema (MySQL)

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('USER', 'INSTRUCTOR', 'ADMIN') NOT NULL DEFAULT 'USER',
    is_active BOOLEAN DEFAULT TRUE,
    full_name VARCHAR(255),
    version INT NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Refresh Tokens table
CREATE TABLE IF NOT EXISTS refresh_tokens (
    token VARCHAR(255) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    expires_at DATETIME NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Assessments table
CREATE TABLE IF NOT EXISTS assessments (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    fitness_score FLOAT NOT NULL,
    category ENUM('POOR', 'FAIR', 'GOOD', 'EXCELLENT') NOT NULL,
    body_age FLOAT NOT NULL,
    comparison ENUM('BODY_OLDER', 'BODY_YOUNGER', 'BODY_EQUAL') NOT NULL,
    responses JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Physical Records table
CREATE TABLE IF NOT EXISTS physical_records (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    weight FLOAT NOT NULL,
    height FLOAT NOT NULL,
    body_fat_percentage FLOAT,
    waist FLOAT,
    hip FLOAT,
    activity_level VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. Exercises table
CREATE TABLE IF NOT EXISTS exercises (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    muscle_group VARCHAR(100),
    difficulty VARCHAR(50)
);

-- 6. Routines table
CREATE TABLE IF NOT EXISTS routines (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    goal VARCHAR(255),
    level ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED') NOT NULL,
    exercises_data JSON NOT NULL,
    creator_id CHAR(36) NOT NULL,
    FOREIGN KEY (creator_id) REFERENCES users(id)
);

-- 7. Routine Assignments table
CREATE TABLE IF NOT EXISTS routine_assignments (
    user_id CHAR(36) NOT NULL,
    routine_id CHAR(36) NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (user_id, routine_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (routine_id) REFERENCES routines(id)
);

-- 8. Workout Completions table
CREATE TABLE IF NOT EXISTS workout_completions (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    routine_id CHAR(36) NOT NULL,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    effort_level INT NOT NULL,
    notes VARCHAR(500),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (routine_id) REFERENCES routines(id)
);

-- 9. Nutrition Plans table
CREATE TABLE IF NOT EXISTS nutrition_plans (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    week_number INT NOT NULL,
    year INT NOT NULL,
    plans_data JSON NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 10. Profile Audit Logs table
CREATE TABLE IF NOT EXISTS profile_audit_logs (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    changed_by CHAR(36) NOT NULL,
    changes JSON NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id)
);
