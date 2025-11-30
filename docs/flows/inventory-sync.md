# Inventory Import/Sync Flow

## Import Sources
- CSV file upload
- API sync (from supplier systems)
- Manual entry

## CSV Import Process

1. **Upload** - User uploads CSV file
2. **Parse** - System parses CSV and validates format
3. **Map Columns** - User maps CSV columns to entity fields
4. **Validate** - System validates data (types, required fields, duplicates)
5. **Preview** - User reviews validation report and preview
6. **Dry Run** (optional) - System simulates import without changes
7. **Import** - System creates/updates inventory items
8. **Report** - System generates import summary (success/failures)

## Validation Rules
- SKU must be unique or match existing product
- Warehouse must exist
- Quantity >= 0
- Cost > 0
- Date formats must be valid
- Required fields: SKU, Warehouse, Quantity, Cost

## Conflict Resolution
- **Duplicate SKU**: Update existing vs create new
- **Missing Product**: Create product automatically vs error
- **Invalid Warehouse**: Skip vs error
- **Negative Quantity**: Skip vs error

## API Sync Process

1. **Trigger** - Scheduled or manual sync trigger
2. **Authenticate** - Authenticate with supplier API
3. **Fetch** - Fetch inventory data from supplier
4. **Transform** - Map supplier data to internal format
5. **Dedupe** - Identify duplicates (by SKU + Warehouse)
6. **Merge** - Merge with existing inventory (additive vs replace)
7. **Update** - Update inventory items
8. **Notify** - Send sync summary notification

## Deduplication Strategy
- Match by: SKU + Warehouse + BatchCode (if available)
- Merge strategy: Additive (sum quantities) vs Replace (use latest)
- Conflict resolution: Prefer higher cost vs lower cost vs most recent

## Notes
- TBD: Actual CSV format and column mapping UI
- TBD: Supplier API endpoints and authentication
- TBD: Batch processing and rate limiting

