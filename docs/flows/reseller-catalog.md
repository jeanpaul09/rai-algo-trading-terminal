# Reseller Catalog Visibility Flow

## Visibility Rules
- **Tier-based**: Resellers see products based on their tier
- **Reseller-specific**: Override visibility per reseller
- **Product-level**: Mark products as visible/hidden per reseller
- **Grade-based**: Filter by grade (A+, A, B, C, D)
- **Carrier-based**: Filter by carrier lock status
- **Inventory-based**: Only show products with available inventory

## Visibility Matrix

| Tier | Grades Visible | Carrier Options | Inventory Required |
|------|----------------|-----------------|-------------------|
| Bronze | A, B, C, D | Unlocked only | Yes |
| Silver | A+, A, B, C | Unlocked + AT&T | Yes |
| Gold | A+, A, B | All carriers | No (show all) |
| Platinum | A+, A | All carriers | No (show all) |

## Override Logic
1. Check reseller-specific override (highest priority)
2. Check tier-based rules
3. Check product-level visibility flags
4. Apply grade/carrier/inventory filters
5. Return visible products

## Catalog Endpoints
- `/api/resellers/:id/catalog` - Get visible products for reseller
- `/api/resellers/:id/catalog/:productId` - Check if product visible
- `/api/resellers/:id/pricing` - Get pricing for visible products

## Commission & Credit Limits

### Commission Calculation
- Commission = Order.total * Reseller.commissionRate
- Tracked per order
- Paid out monthly/quarterly

### Credit Limit Management
- Track current balance: sum of unpaid orders
- Check before order approval: balance + order.total <= creditLimit
- Auto-approve orders if balance < creditLimit * 0.8
- Require manual approval if balance >= creditLimit * 0.8

## Notes
- TBD: Actual visibility API endpoints
- TBD: Commission payout workflow
- TBD: Credit limit override requests
- TBD: Reseller branding (custom logos, colors)

