-- ============================================
-- Insertar ejercicios para crear rutinas
-- Ejecuta este script en phpMyAdmin (pestaña SQL) o en tu cliente MySQL
-- ============================================

USE fitlife_db;

-- Opcional: si quieres empezar de cero, descomenta la siguiente línea:
-- DELETE FROM exercises;

INSERT INTO exercises (id, name, description, muscle_group, difficulty) VALUES
(UUID(), 'Sentadillas', 'Cuádriceps y glúteos', 'Piernas', 'BEGINNER'),
(UUID(), 'Press banca', 'Pectorales y tríceps', 'Pecho', 'INTERMEDIATE'),
(UUID(), 'Dominadas', 'Espalda y bíceps', 'Espalda', 'INTERMEDIATE'),
(UUID(), 'Plancha', 'Core', 'Core', 'BEGINNER'),
(UUID(), 'Peso muerto', 'Cadena posterior', 'Espalda', 'ADVANCED'),
(UUID(), 'Remo con barra', 'Espalda', 'Espalda', 'INTERMEDIATE'),
(UUID(), 'Press militar', 'Hombros', 'Hombros', 'INTERMEDIATE'),
(UUID(), 'Curl bíceps', 'Bíceps', 'Brazos', 'BEGINNER');

-- Verificar
SELECT COUNT(*) AS total_ejercicios FROM exercises;
