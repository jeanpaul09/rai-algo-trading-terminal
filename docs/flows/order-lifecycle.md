# Order Lifecycle Flow

## States
- `draft` - Order being created/edited
- `submitted` - Order submitted for approval
- `approved` - Order approved, awaiting payment
- `paid` - Payment received, ready for fulfillment
- `fulfilled` - Order shipped/delivered
- `canceled` - Order canceled before fulfillment
- `returned` - Order returned after fulfillment

## Transitions

```
draft → submitted (User submits order)
submitted → approved (Admin/Manager approves)
submitted → canceled (Admin/Manager cancels)
approved → paid (Payment processed)
paid → fulfilled (Warehouse fulfills)
fulfilled → returned (Customer returns)
paid → canceled (Cancel before fulfillment)
```

## Guards
- `submitted → approved`: Requires admin/manager role
- `approved → paid`: Requires payment verification
- `paid → fulfilled`: Requires inventory availability
- `fulfilled → returned`: Requires return authorization

## Side Effects
- `submitted`: Send notification to approvers
- `approved`: Reserve inventory, send invoice
- `paid`: Update inventory quantities, generate shipping label
- `fulfilled`: Update reseller credit, mark inventory as sold
- `canceled`: Release reserved inventory
- `returned`: Restore inventory, process refund

## Notes
- TBD: Actual API endpoints and validation rules
- TBD: Email notifications workflow
- TBD: Payment gateway integration details

