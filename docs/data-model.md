# Data Model

## Overview
This document describes the inferred data model from the target application.

## Entities

### User
| Field | Type | Nullable | Unique | Description |
|-------|------|----------|--------|-------------|
| id | string | No | Yes | Primary key |
| email | string | No | Yes | User email |
| name | string | No | No | Display name |
| role | enum | No | No | admin, manager, rep, reseller |
| resellerId | string | Yes | No | Foreign key to Reseller |
| createdAt | datetime | No | No | Creation timestamp |
| updatedAt | datetime | No | No | Update timestamp |

### Reseller
| Field | Type | Nullable | Unique | Description |
|-------|------|----------|--------|-------------|
| id | string | No | Yes | Primary key |
| name | string | No | No | Reseller name |
| tier | enum | No | No | Tier level (bronze, silver, gold, platinum) |
| creditLimit | decimal | No | No | Credit limit |
| commissionRate | decimal | Yes | No | Commission percentage |
| active | boolean | No | No | Active status |
| createdAt | datetime | No | No | Creation timestamp |
| updatedAt | datetime | No | No | Update timestamp |

### Supplier
| Field | Type | Nullable | Unique | Description |
|-------|------|----------|--------|-------------|
| id | string | No | Yes | Primary key |
| name | string | No | No | Supplier name |
| contactEmail | string | Yes | No | Contact email |
| contactPhone | string | Yes | No | Contact phone |
| address | string | Yes | No | Physical address |
| createdAt | datetime | No | No | Creation timestamp |
| updatedAt | datetime | No | No | Update timestamp |

### Warehouse
| Field | Type | Nullable | Unique | Description |
|-------|------|----------|--------|-------------|
| id | string | No | Yes | Primary key |
| name | string | No | No | Warehouse name |
| address | string | No | No | Physical address |
| latitude | decimal | Yes | No | GPS latitude |
| longitude | decimal | Yes | No | GPS longitude |
| active | boolean | No | No | Active status |
| createdAt | datetime | No | No | Creation timestamp |
| updatedAt | datetime | No | No | Update timestamp |

### Product
| Field | Type | Nullable | Unique | Description |
|-------|------|----------|--------|-------------|
| id | string | No | Yes | Primary key |
| sku | string | No | Yes | Stock keeping unit |
| model | string | No | No | Phone model (e.g., iPhone 14) |
| color | string | No | No | Color variant |
| storage | string | No | No | Storage capacity (e.g., 128GB) |
| grade | enum | No | No | Condition grade (A+, A, B, C, D) |
| carrier | enum | Yes | No | Carrier lock status (unlocked, verizon, att, tmobile) |
| createdAt | datetime | No | No | Creation timestamp |
| updatedAt | datetime | No | No | Update timestamp |

### InventoryItem
| Field | Type | Nullable | Unique | Description |
|-------|------|----------|--------|-------------|
| id | string | No | Yes | Primary key |
| productId | string | No | No | Foreign key to Product |
| warehouseId | string | No | No | Foreign key to Warehouse |
| quantity | integer | No | No | Available quantity |
| cost | decimal | No | No | Cost per unit |
| supplierId | string | Yes | No | Foreign key to Supplier |
| batchCode | string | Yes | No | Batch/lot code |
| createdAt | datetime | No | No | Creation timestamp |
| updatedAt | datetime | No | No | Update timestamp |

### PriceRule
| Field | Type | Nullable | Unique | Description |
|-------|------|----------|--------|-------------|
| id | string | No | Yes | Primary key |
| name | string | No | No | Rule name |
| scope | enum | No | No | global, reseller, tier, model |
| scopeId | string | Yes | No | ID of scope target (resellerId, tier, model) |
| formula | json | No | No | Pricing formula (markup %, floor, cap) |
| priority | integer | No | No | Rule precedence order |
| active | boolean | No | No | Active status |
| createdAt | datetime | No | No | Creation timestamp |
| updatedAt | datetime | No | No | Update timestamp |

### Order
| Field | Type | Nullable | Unique | Description |
|-------|------|----------|--------|-------------|
| id | string | No | Yes | Primary key |
| resellerId | string | No | No | Foreign key to Reseller |
| status | enum | No | No | draft, submitted, approved, paid, fulfilled, canceled, returned |
| subtotal | decimal | No | No | Subtotal before tax |
| tax | decimal | No | No | Tax amount |
| total | decimal | No | No | Total amount |
| notes | text | Yes | No | Order notes |
| createdAt | datetime | No | No | Creation timestamp |
| updatedAt | datetime | No | No | Update timestamp |
| fulfilledAt | datetime | Yes | No | Fulfillment timestamp |

### OrderItem
| Field | Type | Nullable | Unique | Description |
|-------|------|----------|--------|-------------|
| id | string | No | Yes | Primary key |
| orderId | string | No | No | Foreign key to Order |
| inventoryId | string | No | No | Foreign key to InventoryItem |
| quantity | integer | No | No | Ordered quantity |
| unitPrice | decimal | No | No | Price per unit at time of order |
| createdAt | datetime | No | No | Creation timestamp |

### AuditLog
| Field | Type | Nullable | Unique | Description |
|-------|------|----------|--------|-------------|
| id | string | No | Yes | Primary key |
| actorId | string | No | No | Foreign key to User |
| action | string | No | No | Action performed (create, update, delete, approve, etc.) |
| entity | string | No | No | Entity type (Order, InventoryItem, etc.) |
| entityId | string | No | No | ID of affected entity |
| diff | json | Yes | No | Change diff (before/after) |
| ipAddress | string | Yes | No | IP address of request |
| userAgent | string | Yes | No | User agent string |
| createdAt | datetime | No | No | Timestamp |

## Relationships

```
User ──┬──> Reseller (optional, many-to-one)
       │
       └──> AuditLog (one-to-many)

Reseller ──> Order (one-to-many)
Reseller ──> PriceRule (one-to-many, optional)

Product ──> InventoryItem (one-to-many)
Product ──> PriceRule (one-to-many, optional, via scope)

Warehouse ──> InventoryItem (one-to-many)

Supplier ──> InventoryItem (one-to-many, optional)

Order ──> OrderItem (one-to-many)
Order ──> AuditLog (one-to-many)

InventoryItem ──> OrderItem (one-to-many)
```

## Indexes

### Primary Keys
- All entities have `id` as primary key (UUID or auto-increment)

### Unique Constraints
- User.email
- Product.sku
- (OrderItem: orderId + inventoryId) - composite unique?

### Foreign Key Indexes
- InventoryItem.productId
- InventoryItem.warehouseId
- InventoryItem.supplierId
- Order.resellerId
- OrderItem.orderId
- OrderItem.inventoryId
- PriceRule.scopeId

### Query Indexes
- Product.grade
- Product.carrier
- InventoryItem.quantity
- Order.status
- Order.createdAt
- AuditLog.entity + entityId
- AuditLog.createdAt

## Constraints & Validation

### Business Rules
- InventoryItem.quantity >= 0
- OrderItem.quantity > 0
- PriceRule.priority must be unique within scope
- Order.total = OrderItem.quantity * OrderItem.unitPrice (sum)
- Reseller.creditLimit >= 0
- Product.grade in [A+, A, B, C, D]
- Order.status transitions: draft → submitted → approved → paid → fulfilled (or canceled/returned)

## Notes
- All timestamps use UTC
- Decimal fields use precision appropriate for currency (e.g., 10,2)
- JSON fields store flexible schema data (formulas, diffs)
- Soft deletes may be implemented (deletedAt field) - TBD

