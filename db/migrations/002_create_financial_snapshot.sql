CREATE TABLE IF NOT EXISTS financial_snapshot (
    id SERIAL PRIMARY KEY,
    
    company_id BIGINT UNSIGNED NOT NULL,
    snapshot_date DATE NOT NULL,
    marginal_tax_rate NUMERIC(3,1) DEFAULT 21.0,

    last_annual_revenue NUMERIC(16,2) NOT NULL,
    last_annual_ebit NUMERIC(16,2) NOT NULL,
    last_annual_net_income NUMERIC(16,2) NOT NULL,
    last_annual_interest_expense NUMERIC(16,2) NOT NULL,
    last_annual_tax_paid NUMERIC(16,2) NOT NULL,
    trailing_sales NUMERIC(16,2),
    trailing_ebit NUMERIC(16,2),

    last_annual_debt NUMERIC(16,2) NOT NULL,
    last_annual_cash NUMERIC(16,2),
    last_annual_equity NUMERIC(16,2) NOT NULL,

    last_annual_capex NUMERIC(16,2) NOT NULL,
    last_annual_chng_wc NUMERIC(16,2) NOT NULL,
    last_annual_da NUMERIC(16,2) NOT NULL,

    market_cap NUMERIC(16,2) NOT NULL,
    current_shares_outstanding INT NOT NULL,
    current_beta FLOAT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_company FOREIGN KEY (company_id)
        REFERENCES company(id)
        ON DELETE CASCADE,

    UNIQUE (company_id, snapshot_date)
)
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_company_id ON financial_snapshot(company_id);
CREATE INDEX idx_snapshot_date ON financial_snapshot(snapshot_date);
CREATE INDEX idx_market_cap ON financial_snapshot(market_cap);
CREATE INDEX idx_beta ON financial_snapshot(current_beta);