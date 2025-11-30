# Pricing Engine Flow

## Rule Types
- **Global**: Applies to all products/resellers
- **Reseller**: Applies to specific reseller
- **Tier**: Applies to reseller tier (bronze, silver, gold, platinum)
- **Model**: Applies to specific product model

## Rule Precedence (Highest to Lowest)
1. Reseller-specific override
2. Tier-specific rule
3. Model-specific rule
4. Global rule

## Pricing Formula Components
- **Base Cost**: From InventoryItem.cost
- **Markup %**: Percentage markup on cost
- **Floor**: Minimum selling price
- **Cap**: Maximum selling price
- **Fixed Price**: Override with fixed price

## Calculation Flow

```
1. Start with base cost (InventoryItem.cost)
2. Apply global rule (if exists)
3. Apply model rule (if exists and higher priority)
4. Apply tier rule (if reseller has tier and higher priority)
5. Apply reseller override (if exists and highest priority)
6. Apply floor constraint (ensure price >= floor)
7. Apply cap constraint (ensure price <= cap)
8. Return final price
```

## Rule Evaluation
- Only active rules are considered
- Rules are evaluated in priority order
- Later rules override earlier rules
- Floor/cap constraints are applied last

## Example Scenarios

### Scenario 1: Global + Reseller Override
- Base cost: $100
- Global rule: +20% markup → $120
- Reseller override: +10% markup → $110
- Final price: $110 (reseller override wins)

### Scenario 2: Model + Tier + Floor
- Base cost: $100
- Model rule: +15% markup → $115
- Tier rule: +5% markup → $105
- Floor: $110
- Final price: $110 (floor constraint applies)

## Price Preview Component
- Show base cost
- Show all applicable rules
- Show calculation steps
- Show final price with breakdown

## Notes
- TBD: Actual formula format (JSON structure)
- TBD: Rule UI composer interface
- TBD: Bulk price calculation API
- TBD: Price history/audit trail

