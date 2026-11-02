-- One row per patient with clinical and sample-level features.
-- LEFT JOIN so a patient with no sample would still show up (with NULLs).
SELECT
    p.patient_id,
    p.sex,
    p.age_at_diagnosis,
    p.stage,
    s.tissue_source_site,
    s.tmb_nonsynonymous
FROM patients p
LEFT JOIN samples s
    ON s.patient_id = p.patient_id
