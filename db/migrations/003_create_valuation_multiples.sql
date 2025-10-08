CREATE TABLE IF NOT EXISTS valuation_multiples (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL,
    calculation_date DATE NOT NULL,
    
    -- Equity multiples (from EquityMultiplesEngine)
    forward_pe FLOAT NOT NULL,
    forward_price_to_book FLOAT NOT NULL,
    forward_price_to_sales FLOAT NOT NULL,
    trailing_pe FLOAT NOT NULL,
    
    -- Firm multiples (from FirmMultiplesEngine, excluding forward_ev_to_ebit & forward_ev_to_sales)
    trailing_ev_to_ebit FLOAT NOT NULL,
    trailing_ev_to_sales FLOAT NOT NULL,
    
    -- Metadata
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE KEY unique_valuation (company_id, calculation_date),
    INDEX idx_calc_date (calculation_date)
) 
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE UNIQUE INDEX idx_unique_valuation ON valuation_multiples(company_id, calculation_date);

CREATE INDEX idx_company_id ON valuation_multiples(company_id);

-- Equity multiples indexes
CREATE INDEX idx_forward_pe ON valuation_multiples(forward_pe);
CREATE INDEX idx_forward_price_to_book ON valuation_multiples(forward_price_to_book);
CREATE INDEX idx_forward_price_to_sales ON valuation_multiples(forward_price_to_sales);
CREATE INDEX idx_trailing_pe ON valuation_multiples(trailing_pe);
-- Firm multiples indexes
CREATE INDEX idx_trailing_ev_to_ebit ON valuation_multiples(trailing_ev_to_ebit);
CREATE INDEX idx_trailing_ev_to_sales ON valuation_multiples(trailing_ev_to_sales);