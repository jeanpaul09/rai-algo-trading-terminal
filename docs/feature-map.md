# Feature Map

## Overview
This document maps all discovered features, routes, APIs, entities, and permissions from the target application.

## Navigation Structure

### Main Navigation Routes
| Feature | URL(s) | Purpose | Status |
|---------|--------|---------|--------|
| Dashboard | `/dashboard` | Overview/Home | ✅ Discovered |
| Stock List | `/stock` | Product catalog with filters and pricing | ✅ Analyzed |
| Orders | `/orders` | Order management with lifecycle tracking | ✅ Analyzed |
| Cart | `/cart` | Shopping cart for order creation | ✅ Discovered |
| Customers | `/customers` | Customer/reseller management | ✅ Discovered |
| Inventory | `/inventory` | Inventory operations | ✅ Discovered |
| Pricing | `/pricing` | Pricing rules and markups | ✅ Discovered |
| Suppliers | `/suppliers` | Supplier management | ✅ Discovered |
| Channels | `/channels` | Channel management | ✅ Discovered |
| Settings | `/settings` | System settings | ✅ Discovered |

### Customer & Sales Routes
| Feature | URL(s) | Purpose | Status |
|---------|--------|---------|--------|
| Search by Email | `/search-by-customer-email` | Customer search | ✅ Discovered |
| Invite Prospects | `/invite-prospects` | Prospect invitation | ✅ Discovered |

### Product & Inventory Configuration
| Feature | URL(s) | Purpose | Status |
|---------|--------|---------|--------|
| Virtual Inventory | `/virtual-inventory` | Virtual inventory management | ✅ Discovered |
| Virtual Item Map | `/virtual-item-map` | Map virtual to physical items | ✅ Discovered |
| Item Map | `/item-map` | Item number mapping | ✅ Discovered |
| Item Attributes | `/item-attributes` | Product attributes config | ✅ Discovered |
| Grades | `/grades` | Grade definitions | ✅ Discovered |
| Stock Selection | `/stock-selection` | Stock selection tools | ✅ Discovered |

### Channels & Integrations
| Feature | URL(s) | Purpose | Status |
|---------|--------|---------|--------|
| Connect Offers | `/connect-offers` | Connect Offers integration | ✅ Discovered |
| Connect Orders | `/connect-orders` | Connect Orders integration | ✅ Discovered |
| Connect Offer Clearing | `/connect-offer-clearing` | Offer clearing for Connect | ✅ Discovered |

### Pricing & Billing
| Feature | URL(s) | Purpose | Status |
|---------|--------|---------|--------|
| Price Markup | `/price-markup` | Price markup rules | ✅ Discovered |
| Offer Clearing | `/offer-clearing` | Offer clearing management | ✅ Discovered |
| Billing and Terms | `/billing-and-terms` | Billing configuration | ✅ Discovered |

### System Routes
| Feature | URL(s) | Purpose | Status |
|---------|--------|---------|--------|
| Email Logs | `/logs/emails` | Email log viewer | ✅ Discovered |

## API Endpoints

### Authentication
| Method | Path | Purpose | Auth Required | Status |
|--------|------|---------|---------------|--------|
| POST | `cognito-idp.us-east-1.amazonaws.com/` | AWS Cognito authentication | No | ✅ Discovered |
| GET | `/account/user-info` | Current user info | Yes | ✅ Discovered |
| GET | `/security/authorities` | Get security authorities | Yes | ✅ Discovered |
| POST | `/api/auth/logout` | User logout | Yes | 🔍 Needs discovery |

### Inventory & Stock
| Method | Path | Purpose | Auth Required | Status |
|--------|------|---------|---------------|--------|
| GET | `/stocklist/items?includeOutOfStock=false` | List stock items | Yes | ✅ Discovered |
| GET | `/pxnr/stocklist/items?includeOutOfStock=false` | List stock items (PNR) | Yes | ✅ Discovered |
| GET | `/pxnr/stocklist/itemscount` | Get stock items count | Yes | ✅ Discovered |
| GET | `/pxnr/stocklist/warehouses` | List warehouses | Yes | ✅ Discovered |
| GET | `/inventory/settings` | Get inventory settings | Yes | ✅ Discovered |
| GET | `/pxn/inventory-settings` | Get inventory settings (PNX) | Yes | ✅ Discovered |
| GET | `/pxn/stocklist-settings` | Get stock list settings | Yes | ✅ Discovered |
| POST | `/inventory/import` | CSV import | Yes | 🔍 Needs discovery |
| GET | `/inventory/export` | CSV export | Yes | 🔍 Needs discovery |

### Products
| Method | Path | Purpose | Auth Required | Status |
|--------|------|---------|---------------|--------|
| GET | `/api/products` | List products | Yes | TBD |
| POST | `/api/products` | Create product | Yes | TBD |
| GET | `/api/products/:id` | Get product | Yes | TBD |
| PUT | `/api/products/:id` | Update product | Yes | TBD |
| DELETE | `/api/products/:id` | Delete product | Yes | TBD |

### Orders
| Method | Path | Purpose | Auth Required | Status |
|--------|------|---------|---------------|--------|
| GET | `/sales-order/settings` | Get sales order settings | Yes | ✅ Discovered |
| GET | `/pxn/salesorder-settings` | Get sales order settings (PNX) | Yes | ✅ Discovered |
| GET | `/api/orders` | List orders | Yes | 🔍 Needs discovery |
| POST | `/api/orders` | Create order | Yes | 🔍 Needs discovery |
| GET | `/orders/:id` | Order detail page | Yes | ✅ Discovered (route) |
| POST | `/api/orders/:id/approve` | Approve order | Yes | 🔍 Needs discovery |
| POST | `/api/orders/:id/fulfill` | Fulfill order | Yes | 🔍 Needs discovery |
| POST | `/api/orders/:id/cancel` | Cancel order | Yes | 🔍 Needs discovery |

### Customers/Resellers
| Method | Path | Purpose | Auth Required | Status |
|--------|------|---------|---------------|--------|
| GET | `/account/salesreps` | Get sales reps list | Yes | ✅ Discovered |
| GET | `/api/customers` | List customers | Yes | 🔍 Needs discovery |
| POST | `/api/customers` | Create customer | Yes | 🔍 Needs discovery |
| GET | `/api/customers/:id` | Get customer | Yes | 🔍 Needs discovery |
| PUT | `/api/customers/:id` | Update customer | Yes | 🔍 Needs discovery |
| DELETE | `/api/customers/:id` | Delete customer | Yes | 🔍 Needs discovery |

### Pricing
| Method | Path | Purpose | Auth Required | Status |
|--------|------|---------|---------------|--------|
| GET | `/api/pricing/rules` | List pricing rules | Yes | TBD |
| POST | `/api/pricing/rules` | Create pricing rule | Yes | TBD |
| GET | `/api/pricing/rules/:id` | Get pricing rule | Yes | TBD |
| PUT | `/api/pricing/rules/:id` | Update pricing rule | Yes | TBD |
| DELETE | `/api/pricing/rules/:id` | Delete pricing rule | Yes | TBD |
| POST | `/api/pricing/calculate` | Calculate price | Yes | TBD |

### Warehouses
| Method | Path | Purpose | Auth Required | Status |
|--------|------|---------|---------------|--------|
| GET | `/api/warehouses` | List warehouses | Yes | TBD |
| POST | `/api/warehouses` | Create warehouse | Yes | TBD |
| GET | `/api/warehouses/:id` | Get warehouse | Yes | TBD |
| PUT | `/api/warehouses/:id` | Update warehouse | Yes | TBD |
| DELETE | `/api/warehouses/:id` | Delete warehouse | Yes | TBD |

### Suppliers
| Method | Path | Purpose | Auth Required | Status |
|--------|------|---------|---------------|--------|
| GET | `/pxnr/config/suppliers` | Get supplier configuration | Yes | ✅ Discovered |
| GET | `/api/suppliers` | List suppliers | Yes | 🔍 Needs discovery |
| POST | `/api/suppliers` | Create supplier | Yes | 🔍 Needs discovery |
| GET | `/api/suppliers/:id` | Get supplier | Yes | 🔍 Needs discovery |
| PUT | `/api/suppliers/:id` | Update supplier | Yes | 🔍 Needs discovery |
| DELETE | `/api/suppliers/:id` | Delete supplier | Yes | 🔍 Needs discovery |

### Users
| Method | Path | Purpose | Auth Required | Status |
|--------|------|---------|---------------|--------|
| GET | `/api/users` | List users | Yes | TBD |
| POST | `/api/users` | Create user | Yes | TBD |
| GET | `/api/users/:id` | Get user | Yes | TBD |
| PUT | `/api/users/:id` | Update user | Yes | TBD |
| DELETE | `/api/users/:id` | Delete user | Yes | TBD |

## Entities & Relationships

### Core Entities
- **User**: id, email, name, role, resellerId (optional)
- **Reseller**: id, name, tier, creditLimit, commissionRate
- **Supplier**: id, name, contactInfo
- **Warehouse**: id, name, address, location
- **Product**: id, model, color, storage, grade, carrier, sku (unique)
- **InventoryItem**: id, productId, warehouseId, quantity, cost, supplierId, batchCode
- **PriceRule**: id, name, scope (global|reseller|tier|model), formula, active
- **Order**: id, resellerId, status, subtotal, total, timestamps
- **OrderItem**: id, orderId, inventoryId, quantity, unitPrice

### Relationships
- User → Reseller (optional, many-to-one)
- InventoryItem → Product (many-to-one)
- InventoryItem → Warehouse (many-to-one)
- InventoryItem → Supplier (optional, many-to-one)
- Order → Reseller (many-to-one)
- OrderItem → Order (many-to-one)
- OrderItem → InventoryItem (many-to-one)
- PriceRule → Reseller (optional, many-to-one)

## Permissions & RBAC

### Roles (TBD)
- Admin
- Manager
- Rep
- Reseller

### Role Permissions (TBD)
| Role | Inventory | Products | Orders | Resellers | Pricing | Users | Settings |
|------|-----------|----------|--------|-----------|---------|-------|----------|
| Admin | Full | Full | Full | Full | Full | Full | Full |
| Manager | Read/Write | Read/Write | Read/Write | Read | Read/Write | Read | Read |
| Rep | Read | Read | Create/Read | Read | Read | None | None |
| Reseller | Read (filtered) | Read (filtered) | Create/Read (own) | None | Read (own) | None | None |

## Notes
- All endpoints require authentication unless noted
- Pagination: TBD (offset-based vs cursor-based)
- Filtering: TBD (query params format)
- Sorting: TBD (sort param format)
- Rate Limits: TBD
- Error Codes: TBD

