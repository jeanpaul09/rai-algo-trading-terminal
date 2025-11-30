# PhoneExport Application - Complete Discovery Report

## Application Overview

**Application Name**: PhoneExport (Phonexport SASS)
**Base URL**: https://admin.phonexport.com
**Architecture**: React SPA with AWS API Gateway backend
**Authentication**: AWS Cognito (JWT-based)

## Core Purpose

PhoneExport is a **B2B inventory and order management platform** for the **phone/electronics wholesale/retail industry**. It enables:

1. **Inventory Management**: Track phone inventory across multiple warehouses
2. **Order Processing**: Complete order lifecycle from creation to fulfillment
3. **Customer Management**: Manage resellers/customers with credit limits
4. **Pricing Engine**: Dynamic pricing with markups and margins
5. **Supplier Integration**: Connect with suppliers and manage supplier orders
6. **Channel Integration**: Connect with sales channels (Connect Offers/Orders)

## Key Business Entities

### Products
- **Phone Models**: iPhone, Samsung, Google phones
- **Variants**: Storage (64GB, 128GB, 256GB), Color
- **Grades**: A, B, AB (appears to be condition grades)
- **Lock Status**: GSM Unlocked, Locked (carrier-specific)
- **Parts Message**: No Part Message, Unknown Part Message (parts condition indicator)

### Inventory
- **Warehouses**: Multiple warehouses (Warehouse 1, Warehouse 2, DFW)
- **Stock Levels**: Items count, Quantity available
- **Cost**: Base cost per unit
- **Pricing**: Dynamic pricing displayed

### Orders
- **Order Types**: 
  - Regular orders (PXSTKL0000347 format)
  - Supplier orders (ORD845140, RQM0018791 formats)
- **Order Statuses**:
  - On Hold
  - Canceled
  - Awaiting Shipping Quote
  - Awaiting Payment
  - Ready for Fulfillment
  - Shipped
- **Item Status**: Allocated, Canceled
- **Payment Status**: Paid, Unpaid

### Customers/Resellers
- Customer names (e.g., "WorldTech - 1734", "ALBI LOGISTICS - 1735")
- Sales Reps assigned
- Credit limits (implied)

### Suppliers
- PXC Suppliers (PhoneX Connect suppliers)
- Supplier order numbers
- Warehouse associations

## Complete Route Map

### Main Navigation

| Route | Purpose | Key Features |
|-------|---------|--------------|
| `/dashboard` | Home/Dashboard | Overview statistics |
| `/stock` | Stock List | Product catalog with filters, pricing |
| `/orders` | Order Management | Order list, status tracking, fulfillment |
| `/cart` | Shopping Cart | Cart for creating orders |
| `/customers` | Customer Management | Customer/reseller management |
| `/inventory` | Inventory Management | Inventory operations |
| `/pricing` | Pricing Management | Pricing rules and markups |
| `/suppliers` | Supplier Management | Supplier relationships |

### Customer & Sales

| Route | Purpose |
|-------|---------|
| `/search-by-customer-email` | Search customers by email |
| `/invite-prospects` | Invite new prospects/customers |

### Product & Inventory Configuration

| Route | Purpose |
|-------|---------|
| `/virtual-inventory` | Virtual inventory management |
| `/virtual-item-map` | Map virtual items to physical |
| `/item-map` | Item number mapping |
| `/item-attributes` | Product attributes configuration |
| `/grades` | Grade definitions |
| `/stock-selection` | Stock selection tools |

### Channels & Integrations

| Route | Purpose |
|-------|---------|
| `/channels` | Channel management |
| `/connect-offers` | Connect Offers integration |
| `/connect-orders` | Connect Orders integration |
| `/connect-offer-clearing` | Offer clearing for Connect |

### Pricing & Billing

| Route | Purpose |
|-------|---------|
| `/price-markup` | Price markup rules |
| `/offer-clearing` | Offer clearing management |
| `/billing-and-terms` | Billing configuration |

### System

| Route | Purpose |
|-------|---------|
| `/settings` | System settings |
| `/logs/emails` | Email log viewer |

## Detailed Page Analysis

### 1. Stock List (`/stock`)

**Purpose**: Browse and filter available inventory

**Filters**:
- **Warehouse**: Radio buttons (Warehouse 1, Warehouse 2)
- **Category**: Radio buttons (Phones, etc.)
- **Parts Message**: Checkboxes (No Part Message, Unknown Part Message)
- **Lock Status**: Checkboxes (GSM Unlocked, Locked)
- **Grade**: Checkboxes (A, B, AB, Functional)
- **Manufacturer**: Checkboxes (Apple, Google, Samsung)

**Display**:
- Product name (e.g., "Apple iPhone 12 64GB")
- Grade badge
- Items count
- Quantity available (can show "100+" for large quantities)
- Price per unit
- "Buy or Make Offer" button

**Actions**:
- STOCK ALERTS (disabled)
- DAILY REPORT (disabled)
- IMPORT (disabled)
- EXPORT (enabled)
- Cart link (shows item count)

**Summary Stats**:
- Total items: 255
- Total quantity: 2401+

### 2. Orders (`/orders`)

**Purpose**: Manage order lifecycle

**Status Filters** (with counts and totals):
- On Hold (0) $0
- Canceled (6) $0
- Awaiting Shipping Quote (0) $0
- Awaiting Payment (0) $0
- Ready for Fulfillment (0) $0
- Shipped (17) $148,968.00

**Additional Filters**:
- PXC Supplier
- Sales Reps
- Customer
- Item Status
- Item Change
- Payment Status
- Create Date
- Update Date
- Warehouse

**Data Table Columns**:
1. PhoneX Order # (clickable, links to `/orders/{ORDER_ID}`)
2. Supplier Order #
3. PXC Supplier
4. Created (date)
5. Updated (date)
6. Warehouse Code
7. Sales Rep
8. Customer
9. Total (currency)
10. Margin (currency)
11. Margin % (percentage)
12. Item Status
13. Fulfillment Status
14. Days in Status (duration)
15. Payment Status
16. Days in Unpaid

**Actions**:
- Add (create new order)
- Import
- Export
- Text search
- Bulk selection

**Order Detail Pages**: `/orders/{ORDER_ID}` (e.g., `/orders/PXSTKL0000347`)

## API Architecture

### Base API Gateway
```
https://fcrrsl2n1f.execute-api.us-east-1.amazonaws.com/Integration/px-api-gateway/
```

### API Endpoints Discovered

#### Authentication
- `POST cognito-idp.us-east-1.amazonaws.com/` - Cognito authentication

#### Account & User
- `GET /account/user-info` - Current user info
- `GET /account/settings` - Account settings
- `GET /account/salesreps` - Sales reps list

#### Inventory & Stock
- `GET /stocklist/items?includeOutOfStock=false` - Get stock items
- `GET /pxnr/stocklist/items?includeOutOfStock=false` - Get stock items (PNR)
- `GET /pxnr/stocklist/itemscount` - Get stock items count
- `GET /pxnr/stocklist/warehouses` - Get warehouses
- `GET /inventory/settings` - Inventory settings
- `GET /pxn/inventory-settings` - Inventory settings (PNX)

#### Orders
- `GET /sales-order/settings` - Sales order settings
- `GET /pxn/salesorder-settings` - Sales order settings (PNX)

#### Settings & Configuration
- `GET /module-contracts/tenant-contracts` - Tenant contracts
- `GET /security/authorities` - Security authorities
- `GET /stocklist/pricing/settings` - Stock list pricing settings
- `GET /pxn/stocklist-settings` - Stock list settings
- `GET /pxnr/config/suppliers` - Supplier configuration

#### Billing
- `GET /billing/client/payment-methods` - Payment methods

## Key Workflows

### Order Lifecycle
1. **Cart** → Add items from stock list
2. **Create Order** → Submit cart as order
3. **On Hold** → Order placed on hold
4. **Awaiting Shipping Quote** → Waiting for shipping costs
5. **Awaiting Payment** → Waiting for payment
6. **Ready for Fulfillment** → Payment received, ready to ship
7. **Shipped** → Order fulfilled
8. **Canceled** → Order canceled at any stage

### Inventory Flow
1. **Stock Import** → Import inventory (CSV/API)
2. **Stock Management** → Update quantities, prices
3. **Stock Alerts** → Low stock notifications
4. **Daily Reports** → Inventory reports
5. **Stock Export** → Export inventory data

### Pricing Flow
1. **Base Cost** → Set per inventory item
2. **Price Markup Rules** → Apply markup percentages
3. **Dynamic Pricing** → Calculate final price
4. **Margin Calculation** → Track margin per order

## Business Logic Insights

### Order Numbering
- PhoneX Orders: `PXSTKL{7 digits}` (e.g., PXSTKL0000347)
- Supplier Orders: Various formats (ORD845140, RQM0018791)

### Pricing Structure
- Base cost per item
- Margin calculation (absolute and percentage)
- Price displayed per unit
- Total order value

### Warehouse Management
- Multiple warehouses (Warehouse 1, Warehouse 2, DFW)
- Warehouse codes (W1, W2, DFW)
- Warehouse-specific inventory

### Customer Management
- Customer names with IDs (e.g., "WorldTech - 1734")
- Sales rep assignment
- Credit limits (implied)

## Technology Stack

### Frontend
- React (SPA)
- Material-UI (MUI) components
- Micro-frontend architecture (remoteEntry.js)
- CloudFront CDN for assets

### Backend
- AWS API Gateway
- AWS Cognito (authentication)
- AWS Lambda (presumably)
- S3 (asset storage)

### Infrastructure
- AWS CloudFront (CDN)
- AWS S3 (static assets)
- Multi-tenant SaaS architecture

## Next Steps for Implementation

1. **API Integration**: Map all API endpoints to tRPC/Next.js API routes
2. **Data Models**: Refine Prisma schema based on discovered entities
3. **UI Components**: Replicate key UI patterns (filters, tables, forms)
4. **Workflows**: Implement order lifecycle state machine
5. **Pricing Engine**: Implement pricing calculation logic
6. **Authentication**: Integrate with Cognito or implement equivalent

