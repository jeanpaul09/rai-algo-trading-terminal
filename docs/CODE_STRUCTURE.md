# Project Structure & Quick Reference

## 📁 Key Directories

### `/lib` - Core Business Logic
- **`lib/suppliers/`** - Supplier integration framework
  - `base.ts` - Adapter interface
  - `wesellcellular.ts` - WesellCellular implementation
  - `registry.ts` - Supplier registry/manager
  
- **`lib/services/`** - Business services
  - `order-forwarding.ts` - Order forwarding to suppliers
  - `notifications.ts` - Email notification service
  - `inventory-sync.ts` - Inventory synchronization
  
- **`lib/encryption.ts`** - Credential encryption utilities
- **`lib/auth.ts`** - Authentication (NextAuth)
- **`lib/rbac.ts`** - Role-based access control
- **`lib/i18n.ts`** - Internationalization
- **`lib/utils.ts`** - Utility functions

### `/app` - Next.js App Router

#### `/app/api` - API Routes
- **`api/suppliers/`** - Supplier CRUD endpoints
- **`api/suppliers/[supplierId]/sync-inventory/`** - Inventory sync
- **`api/orders/`** - Order management
- **`api/orders/[orderId]/forward/`** - Forward order to supplier
- **`api/webhooks/supplier/[supplierId]/`** - Webhook receiver

#### `/app/(dashboard)` - Protected Routes
- `dashboard/page.tsx` - Dashboard
- `orders/page.tsx` - Orders list
- `suppliers/page.tsx` - Supplier management
- `inventory/page.tsx` - Inventory
- `products/page.tsx` - Products
- `resellers/page.tsx` - Resellers
- `pricing/page.tsx` - Pricing rules
- `warehouses/page.tsx` - Warehouses
- `users/page.tsx` - User management
- `settings/page.tsx` - Settings

### `/components` - React Components
- **`components/suppliers/`** - Supplier UI components
  - `supplier-management.tsx` - Main supplier management UI
  
- **`components/orders/`** - Order UI components
  - `orders-list.tsx` - Orders list with forwarding
  
- **`components/ui/`** - shadcn/ui components (buttons, cards, dialogs, etc.)

### `/prisma` - Database
- **`schema.prisma`** - Database schema definition
  - Models: User, Reseller, Supplier, Order, Product, InventoryItem, etc.
  - Includes supplier integration models

### `/tests` - Tests
- **`tests/unit/`** - Unit tests (Vitest)
  - `suppliers.test.ts` - Supplier adapter tests
  - `utils.test.ts` - Utility tests
  
- **`tests/e2e/`** - E2E tests (Playwright)
  - `supplier-integration.spec.ts` - Integration tests

### `/docs` - Documentation
- **`DISCOVERY_LOG.md`** - Discovery phase log
- **`ROUTE_MAP.md`** - Discovered routes
- **`SUPPLIER_INTEGRATION.md`** - Integration overview
- **`SUPPLIER_INTEGRATION_DESIGN.md`** - Design details
- **`IMPLEMENTATION_COMPLETE.md`** - Implementation summary
- **`FINAL_SUMMARY.md`** - Final summary

## 🔍 How to Inspect the Code

### 1. Start with Core Integration
**File**: `lib/suppliers/base.ts`
- See the adapter interface
- Understand the contract suppliers must implement

**File**: `lib/suppliers/wesellcellular.ts`
- See WesellCellular implementation
- Understand how orders are forwarded

### 2. Check Order Flow
**File**: `lib/services/order-forwarding.ts`
- See how orders are forwarded to suppliers
- Understand status updates

**File**: `app/api/orders/[orderId]/forward/route.ts`
- See the API endpoint
- Understand how to call it

### 3. Inspect Webhooks
**File**: `app/api/webhooks/supplier/[supplierId]/route.ts`
- See webhook handler
- Understand signature verification

### 4. Check Database Schema
**File**: `prisma/schema.prisma`
- See all data models
- Understand relationships
- Check supplier integration tables

### 5. View UI Components
**File**: `components/suppliers/supplier-management.tsx`
- See supplier management UI
- Understand user interactions

**File**: `components/orders/orders-list.tsx`
- See orders list UI
- Understand order forwarding UI

## 🚀 Quick Start Commands

```bash
# Navigate to project
cd phoneexport-next

# Install dependencies (if not done)
npm install

# Generate Prisma client
npm run db:generate

# Run development server
npm run dev

# Run tests
npm test

# Run E2E tests
npm run test:e2e

# View database schema
npm run db:studio
```

## 📝 Key Files to Review

### Supplier Integration (CRITICAL)
1. `lib/suppliers/base.ts` - Interface
2. `lib/suppliers/wesellcellular.ts` - Implementation
3. `lib/services/order-forwarding.ts` - Order forwarding
4. `app/api/webhooks/supplier/[supplierId]/route.ts` - Webhooks

### Database
1. `prisma/schema.prisma` - Full schema

### UI
1. `components/suppliers/supplier-management.tsx` - Supplier UI
2. `components/orders/orders-list.tsx` - Orders UI

### Configuration
1. `package.json` - Dependencies
2. `.env.example` - Environment variables (if exists)

## 🎯 What's Been Implemented

✅ **Supplier Integration Framework**
- Adapter pattern for suppliers
- WesellCellular adapter
- Supplier registry

✅ **Order Forwarding**
- Forward orders to suppliers
- Status tracking
- Order mapping

✅ **Webhook System**
- Receive supplier updates
- Signature verification
- Status updates

✅ **Notifications**
- Email notifications
- Template system
- Batch processing

✅ **Inventory Sync**
- Sync from suppliers
- Update inventory
- Logging

✅ **UI Components**
- Supplier management
- Orders list
- Forwarding UI

✅ **Security**
- Credential encryption
- Webhook verification
- Secure storage

## 📊 Database Models

Check `prisma/schema.prisma` for:
- `Supplier` - Supplier configuration
- `SupplierOrder` - Order mapping
- `SupplierSyncLog` - Sync logs
- `Notification` - Email queue
- `Order` - Orders
- `Product` - Products
- `InventoryItem` - Inventory
- `Reseller` - Resellers
- `User` - Users

## 🔗 API Endpoints

- `GET /api/suppliers` - List suppliers
- `POST /api/suppliers` - Create supplier
- `GET /api/orders` - List orders
- `POST /api/orders` - Create order
- `POST /api/orders/:orderId/forward` - Forward order
- `POST /api/webhooks/supplier/:supplierId` - Webhook
- `POST /api/suppliers/:supplierId/sync-inventory` - Sync inventory

## 🧪 Testing

- Unit tests: `tests/unit/`
- E2E tests: `tests/e2e/`
- Run: `npm test` or `npm run test:e2e`

## 📚 Documentation

All documentation in `/docs` folder:
- Discovery logs
- API specs
- Integration designs
- Implementation guides

