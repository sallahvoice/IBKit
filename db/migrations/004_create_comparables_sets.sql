-- 1. Comparable sets (one per target company)
CREATE TABLE IF NOT EXISTS comparable_sets (
    id SERIAL PRIMARY KEY,
    target_company_id BIGINT UNSIGNED NOT NULL,
    name VARCHAR(255) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_target_company FOREIGN KEY (target_company_id)
        REFERENCES companies(id)
        ON DELETE CASCADE,

    UNIQUE KEY unique_target_company (target_company_id)
)
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE UNIQUE INDEX idx_unique_target_company ON comparable_sets(target_company_id);


-- 2. Companies that belong to that set (the target + its peers)
CREATE TABLE IF NOT EXISTS comparable_set_companies (
    id SERIAL PRIMARY KEY,
    set_id BIGINT UNSIGNED NOT NULL,
    company_id BIGINT UNSIGNED NOT NULL,

    -- Optionally tag which is the target inside the set
    is_target BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (set_id) REFERENCES comparable_sets(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,

    UNIQUE KEY unique_company_per_set (set_id, company_id)
)
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE UNIQUE INDEX idx_unique_company_per_set ON comparable_set_companies(set_id, company_id);
CREATE INDEX idx_set_id ON comparable_set_companies(set_id);


CREATE TABLE IF NOT EXISTS comparable_set_multiples (
    id SERIAL PRIMARY KEY,
    set_id BIGINT UNSIGNED NOT NULL,
    company_id BIGINT UNSIGNED NOT NULL,
    valuation_multiple_id BIGINT UNSIGNED NOT NULL,

    FOREIGN KEY (set_id) REFERENCES comparable_sets(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (valuation_multiple_id) REFERENCES valuation_multiples(id) ON DELETE CASCADE,

    UNIQUE KEY unique_multiple_per_company (set_id, company_id)
)
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE UNIQUE INDEX idx_unique_multiple_per_company ON comparable_set_multiples(set_id, company_id);
CREATE INDEX idx_valuation_multiple_id ON comparable_set_multiples(valuation_multiple_id);