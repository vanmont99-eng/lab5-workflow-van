
WITH target_genes(gene_symbol) AS (
    VALUES ('TP53'), ('KRAS'), ('EGFR'), ('STK11'), ('KEAP1')
)
SELECT
    p.patient_id,
    g.gene_symbol,
    COUNT(m.mutation_id) AS n_protein_altering
FROM patients p
JOIN samples s
    ON s.patient_id = p.patient_id
CROSS JOIN target_genes g
LEFT JOIN mutations m
    ON  m.sample_id = s.sample_id
    AND m.gene_symbol = g.gene_symbol
    AND m.variant_classification <> 'Silent'
GROUP BY p.patient_id, g.gene_symbol
ORDER BY p.patient_id, g.gene_symbol;