# Supplier Integration Architecture - Complete Design

## Core Integration Flow

```
┌─────────────┐         ┌─────────────┐         ┌──────────────────┐
│   Client    │ ──────> │ PhoneExport │ ──────> │   PhoneX API     │
│ (Reseller)  │  Order  │  (Your App) │  Push   │  (Middleware)    │
└─────────────┘         └─────────────┘         └──────────────────┘
                                                         │
                                                         │ Forward
                                                         ▼
                                                 ┌──────────────────┐
                                                 │ WesellCellular   │
                                                 │  (Supplier)      │
                                                 └──────────────────┘

┌─────────────┐         ┌─────────────┐         ┌──────────────────┐
│   Client    │ <────── │ PhoneExport │ <────── │   PhoneX API     │
│ (Reseller)  │  Update │  (Your App) │  Webhook│  (Middleware)    │
└─────────────┘         └─────────────┘         └──────────────────┘
                                                         │
                                                         │ Updates
                                                         ▼
                                                 ┌──────────────────┐
                                                 │ WesellCellular   │
                                                 │  (Supplier)      │
                                                 └──────────────────┘
```

## Integration Components

### 1. Order Forwarding (Outbound)
**When**: Client places order in PhoneExport  
**Action**: Forward order to WesellCellular via PhoneX  
**Data Flow**:
1. Order created in PhoneExport database
2. Transform order to PhoneX format
3. POST to PhoneX API with order details
4. PhoneX forwards to WesellCellular
5. Receive confirmation/order ID from PhoneX
6. Store supplier order ID in PhoneExport

### 2. Status Updates (Inbound)
**When**: WesellCellular updates order status  
**Action**: Receive webhook from PhoneX, update PhoneExport  
**Data Flow**:
1. WesellCellular updates order
2. PhoneX receives update
3. PhoneX sends webhook to PhoneExport
4. Parse webhook payload
5. Update order status in database
6. Send email notification to client
7. Update UI in real-time

### 3. Email Notifications
**Trigger Events**:
- New order placed
- Order accepted/rejected
- Order fulfillment started
- Order shipped
- Order status changed
- Inventory updates

**Notification Types**:
- Order confirmation
- Status change alerts
- Fulfillment notifications
- Shipping updates

### 4. Inventory Sync
**When**: Supplier inventory changes  
**Action**: Sync inventory levels  
**Data Flow**:
1. Periodic sync from PhoneX/WesellCellular
2. Update inventory quantities
3. Update pricing if changed
4. Alert on low stock

## PhoneX Integration API (Inferred)

### Order Forwarding
```http
POST https://api.phonex.com/v1/orders
Authorization: Bearer {phonex_api_key}
Content-Type: application/json

{
  "supplier": "wesellcellular",
  "order_id": "PXSTKL0000347",
  "customer_id": "worldtech-1734",
  "items": [
    {
      "sku": "IPHONE12-64GB-A",
      "quantity": 10,
      "unit_price": 231.00
    }
  ],
  "shipping_address": {...},
  "metadata": {...}
}
```

### Webhook Endpoint (Your App)
```http
POST https://your-app.com/api/webhooks/phonex
X-PhoneX-Signature: {signature}
Content-Type: application/json

{
  "event": "order.status_updated",
  "order_id": "PXSTKL0000347",
  "supplier_order_id": "ORD845140",
  "status": "shipped",
  "tracking_number": "1Z999AA10123456784",
  "updated_at": "2025-10-30T18:06:39Z"
}
```

## Replacement Architecture

### Option 1: Direct WesellCellular Integration (Recommended)

**If WesellCellular has API**:
- Direct API integration
- Eliminate PhoneX dependency
- More control over integration
- Lower cost (no middleware fees)

**Implementation**:
```typescript
// lib/suppliers/wesellcellular.ts
export class WesellCellularClient {
  async createOrder(order: Order): Promise<SupplierOrder> {
    // Direct API call to WesellCellular
  }
  
  async getOrderStatus(orderId: string): Promise<OrderStatus> {
    // Poll or webhook from WesellCellular
  }
}
```

### Option 2: PhoneX-Compatible Adapter

**If PhoneX is required**:
- Build PhoneX-compatible connector
- Maintain existing supplier relationships
- Gradual migration path

### Option 3: Universal Supplier Framework

**Multi-supplier support**:
```typescript
// lib/suppliers/base.ts
interface SupplierAdapter {
  createOrder(order: Order): Promise<SupplierOrder>;
  getOrderStatus(orderId: string): Promise<OrderStatus>;
  syncInventory(): Promise<InventoryUpdate[]>;
  handleWebhook(payload: WebhookPayload): Promise<void>;
}

// lib/suppliers/wesellcellular.ts
export class WesellCellularAdapter implements SupplierAdapter {
  // WesellCellular-specific implementation
}

// lib/suppliers/phonex.ts
export class PhoneXAdapter implements SupplierAdapter {
  // PhoneX integration implementation
}
```

## Implementation Plan

### Phase 1: Supplier Connector Framework
1. Create base `SupplierAdapter` interface
2. Implement supplier registry
3. Build webhook handler system
4. Create notification service

### Phase 2: WesellCellular Integration
1. Explore WesellCellular API (if available)
2. Build direct integration OR PhoneX adapter
3. Implement order forwarding
4. Implement status sync

### Phase 3: Notification System
1. Email notification service
2. Real-time UI updates (WebSocket/SSE)
3. Event logging
4. Notification preferences

### Phase 4: Inventory Sync
1. Periodic inventory sync job
2. Real-time inventory updates
3. Price sync
4. Stock level alerts

## Database Schema Updates

### Supplier Integration Tables
```prisma
model Supplier {
  id          String   @id @default(uuid())
  name        String
  type        String   // "direct", "phonex", "custom"
  apiEndpoint String?
  apiKey      String?  @db.Text // Encrypted
  webhookUrl  String?
  active      Boolean  @default(true)
  
  orders      SupplierOrder[]
  syncLogs    SupplierSyncLog[]
}

model SupplierOrder {
  id              String   @id @default(uuid())
  orderId         String   // PhoneExport order ID
  supplierId      String
  supplier        Supplier @relation(fields: [supplierId], references: [id])
  supplierOrderId String?  // Order ID from supplier system
  status          String   // "pending", "confirmed", "shipped", "canceled"
  trackingNumber  String?
  syncedAt        DateTime @default(now())
  updatedAt       DateTime @updatedAt
  
  order           Order    @relation(fields: [orderId], references: [id])
}

model SupplierSyncLog {
  id         String   @id @default(uuid())
  supplierId String
  supplier   Supplier @relation(fields: [supplierId], references: [id])
  type       String   // "inventory", "order", "price"
  status     String   // "success", "error"
  message    String?  @db.Text
  createdAt  DateTime @default(now())
}

model Notification {
  id        String   @id @default(uuid())
  type      String   // "order", "status", "fulfillment"
  orderId   String?
  userId    String?
  email     String
  subject   String
  body      String   @db.Text
  sent      Boolean  @default(false)
  sentAt    DateTime?
  createdAt DateTime @default(now())
}
```

## Security Considerations

### Credential Storage
- Encrypt all API keys and passwords
- Use environment variables or secret management (AWS Secrets Manager, Vault)
- Never commit credentials to git
- Rotate credentials regularly

### Webhook Security
- Verify webhook signatures
- Use HMAC-SHA256 for signature validation
- Rate limit webhook endpoints
- Log all webhook requests

### API Security
- Use HTTPS for all API calls
- Implement API key rotation
- Rate limiting
- Request/response logging

## Next Steps

1. **Explore WesellCellular Interface**: 
   - Log in and explore order placement
   - Check for API documentation
   - Understand order status tracking

2. **Document PhoneX Integration**:
   - Capture API endpoints
   - Document webhook payloads
   - Map notification formats

3. **Design Implementation**:
   - Choose integration approach (direct vs PhoneX)
   - Build supplier connector framework
   - Implement webhook system

4. **Build Notification System**:
   - Email notification service
   - Real-time updates
   - Event logging

