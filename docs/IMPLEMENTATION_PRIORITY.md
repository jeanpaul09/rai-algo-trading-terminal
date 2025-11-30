# Implementation Priority: Supplier Integration System

## Critical Path

The supplier integration is **THE CORE VALUE** of PhoneExport. This must be implemented first and correctly.

## Phase 1: Supplier Connector Framework (HIGH PRIORITY)

### 1.1 Database Schema
```prisma
model Supplier {
  id            String   @id @default(uuid())
  name          String
  type          String   // "direct", "phonex", "custom"
  apiEndpoint   String?
  apiKey        String?  @db.Text // Encrypted
  credentials   Json?    // Encrypted supplier credentials
  webhookUrl    String?
  webhookSecret String?  @db.Text // Encrypted
  active        Boolean  @default(true)
  
  orders        SupplierOrder[]
  syncLogs      SupplierSyncLog[]
  
  @@map("suppliers")
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
  
  @@index([orderId])
  @@index([supplierOrderId])
  @@map("supplier_orders")
}

model SupplierSyncLog {
  id         String   @id @default(uuid())
  supplierId String
  supplier   Supplier @relation(fields: [supplierId], references: [id])
  type       String   // "inventory", "order", "price"
  status     String   // "success", "error"
  message    String?  @db.Text
  createdAt  DateTime @default(now())
  
  @@index([supplierId, createdAt])
  @@map("supplier_sync_logs")
}

model Notification {
  id        String   @id @default(uuid())
  type      String   // "order", "status", "fulfillment", "offer"
  orderId   String?
  userId    String?
  email     String
  subject   String
  body      String   @db.Text
  sent      Boolean  @default(false)
  sentAt    DateTime?
  createdAt DateTime @default(now())
  
  @@index([email, sent])
  @@index([orderId])
  @@map("notifications")
}
```

### 1.2 Supplier Adapter Interface
```typescript
// lib/suppliers/base.ts
export interface SupplierAdapter {
  name: string
  
  // Order Management
  createOrder(order: Order): Promise<SupplierOrderResponse>
  getOrderStatus(orderId: string): Promise<OrderStatus>
  cancelOrder(orderId: string): Promise<void>
  
  // Inventory
  syncInventory(): Promise<InventoryUpdate[]>
  getInventoryItem(sku: string): Promise<InventoryItem | null>
  
  // Webhooks
  handleWebhook(payload: unknown, signature: string): Promise<WebhookEvent>
  verifyWebhookSignature(payload: string, signature: string): boolean
}
```

### 1.3 WesellCellular Adapter
```typescript
// lib/suppliers/wesellcellular.ts
export class WesellCellularAdapter implements SupplierAdapter {
  private apiBase = 'https://rrizry2l60.execute-api.us-east-1.amazonaws.com/Integration/px-api-gateway'
  private apiKey: string
  
  async createOrder(order: Order): Promise<SupplierOrderResponse> {
    // Transform PhoneExport order to WesellCellular format
    // POST to /sales-orders
    // Return supplier order ID
  }
  
  async getOrderStatus(orderId: string): Promise<OrderStatus> {
    // GET /sales-orders/{orderId}
  }
  
  async handleWebhook(payload: unknown, signature: string): Promise<WebhookEvent> {
    // Verify signature
    // Parse webhook payload
    // Return structured event
  }
}
```

## Phase 2: Order Forwarding Service

### 2.1 Order Service
```typescript
// lib/services/order-forwarding.ts
export class OrderForwardingService {
  async forwardOrder(orderId: string) {
    // 1. Get order from database
    // 2. Get supplier from order
    // 3. Get supplier adapter
    // 4. Transform order to supplier format
    // 5. Create order via supplier adapter
    // 6. Save supplier order ID
    // 7. Send confirmation email
  }
}
```

### 2.2 Webhook Handler
```typescript
// app/api/webhooks/supplier/route.ts
export async function POST(req: Request) {
  // 1. Verify webhook signature
  // 2. Parse payload
  // 3. Update order status
  // 4. Send notification email
  // 5. Update UI (via WebSocket/SSE)
}
```

## Phase 3: Notification System

### 3.1 Email Service
```typescript
// lib/services/notifications.ts
export class NotificationService {
  async sendOrderNotification(order: Order, type: 'created' | 'status_change' | 'fulfilled') {
    // Generate email template
    // Send via email service (SendGrid, SES, etc.)
    // Log notification
  }
}
```

### 3.2 Real-time Updates
```typescript
// lib/services/realtime.ts
export class RealtimeService {
  // WebSocket or Server-Sent Events
  // Push updates to connected clients
}
```

## Phase 4: Implementation Steps

1. **Update Prisma Schema** - Add supplier integration tables
2. **Create Supplier Adapter Interface** - Base contract
3. **Implement WesellCellular Adapter** - First supplier
4. **Build Order Forwarding Service** - Core integration logic
5. **Create Webhook Endpoints** - Receive supplier updates
6. **Build Notification Service** - Email notifications
7. **Add Real-time Updates** - WebSocket/SSE
8. **Testing** - E2E integration tests

## Success Criteria

✅ Orders placed in PhoneExport automatically forward to WesellCellular  
✅ Order status updates from WesellCellular sync back to PhoneExport  
✅ Email notifications sent for all order events  
✅ Real-time UI updates when orders change  
✅ Support for multiple suppliers (extensible framework)

