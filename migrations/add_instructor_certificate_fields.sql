-- Migración: añadir campos de certificado profesional a instructors
-- Ejecuta en phpMyAdmin o MySQL cliente

USE fitlife_db;

ALTER TABLE instructors
  ADD COLUMN certificate_url VARCHAR(500) NULL AFTER rating_avg,
  ADD COLUMN certificate_status VARCHAR(20) NOT NULL DEFAULT 'pending' AFTER certificate_url;
