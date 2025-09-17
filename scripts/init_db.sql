-- Initialize the main property database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create properties table if it doesn't exist
CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    price NUMERIC(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'AED',
    bedrooms INTEGER,
    bathrooms INTEGER,
    area NUMERIC(10,2),
    property_type VARCHAR(50),
    location VARCHAR(255),
    description TEXT,
    amenities TEXT,
    url VARCHAR(500),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(location);
CREATE INDEX IF NOT EXISTS idx_properties_type ON properties(property_type);
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price);
CREATE INDEX IF NOT EXISTS idx_properties_bedrooms ON properties(bedrooms);
