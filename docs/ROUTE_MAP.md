# Phase 1 Discovery - Complete Route Map

## Base URL
https://admin.phonexport.com

## Authentication
- **Login URL**: `/` (redirects to login if not authenticated)
- **Auth Provider**: AWS Cognito (`cognito-idp.us-east-1.amazonaws.com`)
- **Login Flow**: Email/Password → Cognito authentication → JWT token → Session

## Discovered Routes

### Main Navigation Routes

| Route | Label | Description | Status |
|-------|-------|-------------|--------|
| `/` | Admin Menu | Root/Home - redirects after login | ✅ |
| `/dashboard` | Home | Dashboard/Home page | ⏳ |
| `/stock` | StockList | Stock/Inventory listing (currently viewing) | ✅ |
| `/cart` | Cart | Shopping cart | ⏳ |
| `/orders` | Orders | Order management | ⏳ |
| `/customers` | Customers | Customer management | ⏳ |
| `/inventory` | Inventory | Inventory management | ⏳ |
| `/pricing` | Pricing | Pricing management | ⏳ |
| `/suppliers` | Suppliers | Supplier management | ⏳ |
| `/settings` | Settings | System settings | ⏳ |

### Customer & Sales Routes

| Route | Label | Description |
|-------|-------|-------------|
| `/search-by-customer-email` | Search By Email | Customer search functionality |
| `/invite-prospects` | Invite Prospects | Prospect invitation system |

### Inventory & Product Routes

| Route | Label | Description |
|-------|-------|-------------|
| `/virtual-inventory` | Virtual Inventory | Virtual inventory management |
| `/virtual-item-map` | Virtual Item # Map | Mapping virtual items |
| `/item-map` | Item # Map | Item number mapping |
| `/item-attributes` | Item Attributes | Product attributes management |
| `/grades` | Grades | Grade management |
| `/stock-selection` | Stock Selection | Stock selection tools |

### Channels & Integration Routes

| Route | Label | Description |
|-------|-------|-------------|
| `/channels` | Channels | Channel management |
| `/connect-offers` | Connect Offers | Connect offers integration |
| `/connect-orders` | Connect Orders | Connect orders integration |
| `/connect-offer-clearing` | Offer Clearing | Offer clearing for Connect |

### Pricing & Billing Routes

| Route | Label | Description |
|-------|-------|-------------|
| `/price-markup` | Price Markup | Price markup rules |
| `/offer-clearing` | Offer Clearing | Offer clearing management |
| `/billing-and-terms` | Billing and Terms | Billing configuration |

### System Routes

| Route | Label | Description |
|-------|-------|-------------|
| `/settings` | Settings | System settings |
| `/logs/emails` | Email Sent | Email log viewer |

## Current Page Analysis: `/stock`

### URL Parameters
- `warehouseGroup=101` - Filters by warehouse group

### Features Observed
1. **Filters**:
   - Warehouse (radio buttons)
   - Category (radio buttons - Phones, etc.)
   - Parts Message (checkboxes - No Part Message, Unknown Part Message)
   - Lock Status (checkboxes - GSM Unlocked, Locked)
   - Grade (checkboxes - A, B, AB, Functional)
   - Manufacturer (checkboxes - Apple, Google, Samsung)

2. **Actions**:
   - STOCK ALERTS (disabled)
   - DAILY REPORT (disabled)
   - IMPORT (disabled)
   - EXPORT (enabled)
   - Cart link (shows count "0")

3. **Product Display**:
   - Product name (e.g., "Apple iPhone 12 64GB")
   - Grade badge (A, B, AB)
   - Items count
   - Quantity available
   - Price per unit
   - "Buy or Make Offer" button

4. **Pagination**:
   - Page numbers (1-6+)
   - First/Previous/Next/Last navigation
   - "Top of Results" button

5. **Summary Stats**:
   - Total items: 255
   - Total quantity: 2401+

6. **Last Updated**: Shows timestamp "Thu Oct 30 2025, 06:06:39 PM"

## API Endpoints Discovered

### Base API Gateway
```
https://fcrrsl2n1f.execute-api.us-east-1.amazonaws.com/Integration/px-api-gateway/
```

### Account & User Management
- `GET /account/user-info` - Get current user info
- `GET /account/settings` - Get account settings
- `GET /account/salesreps` - Get sales reps list

### Inventory & Stock
- `GET /stocklist/items?includeOutOfStock=false` - Get stock items
- `GET /pxnr/stocklist/items?includeOutOfStock=false` - Get stock items (PNR)
- `GET /pxnr/stocklist/itemscount` - Get stock items count
- `GET /pxnr/stocklist/warehouses` - Get warehouses list
- `GET /inventory/settings` - Get inventory settings
- `GET /pxn/inventory-settings` - Get inventory settings (PNX)

### Settings & Configuration
- `GET /inventory/settings` - Inventory settings
- `GET /sales-order/settings` - Sales order settings
- `GET /pxn/settings` - PNX settings
- `GET /pxn/salesorder-settings` - Sales order settings
- `GET /pxnr/config/suppliers` - Supplier configuration
- `GET /stocklist/pricing/settings` - Stock list pricing settings
- `GET /pxn/stocklist-settings` - Stock list settings

### Billing
- `GET /billing/client/payment-methods` - Get payment methods

### Other
- `GET /module-contracts/tenant-contracts` - Tenant contracts
- `GET /security/authorities` - Security authorities

## Authentication Flow

1. User enters email/password on login page
2. POST to `cognito-idp.us-east-1.amazonaws.com/`
3. Receives JWT tokens
4. Redirects to `/stock?warehouseGroup=101` (or dashboard)
5. Subsequent API calls use JWT in Authorization header

## Next Steps
- Explore each route systematically
- Capture API request/response schemas
- Document form structures and validation
- Map RBAC permissions
- Document workflows

