# SMA Outfits — Claude Trading Rules

## Robinhood MCP Trading Authorization

Live trade execution via the `robinhood-trading` MCP server is authorized for this project.

## Trade Approval Policy

### Always require explicit user approval before executing a trade UNLESS one of the urgent conditions below applies.

**Standard flow (most trades):**
1. Identify the intended trade (ticker, direction, size, rationale).
2. Present the trade to the user and wait for explicit confirmation before submitting.
3. Only execute after the user says yes.

### Urgent conditions — execute immediately, notify the user right after:

These two situations are **time-sensitive** and must bypass the approval wait:

1. **Portfolio double opportunity (≥ 100% gain)**: A signal indicates the trade or position has the potential to double or more the total portfolio value. Execute immediately, then notify the user with what was placed and why.

2. **Portfolio loss threshold (≥ 30% drawdown)**: An open position or adverse market move is on track to reduce total portfolio value by 30% or more. Close or hedge immediately, then notify the user with full details.

**After any urgent execution**, always send a summary that includes:
- What trade was placed (ticker, action, quantity, price)
- Why the urgent threshold was triggered
- Current position and P&L impact

## General Trading Conduct

- Never place a trade that exceeds the user's available buying power.
- Prefer limit orders over market orders unless urgency requires market execution.
- Always confirm the account state (positions, cash) before acting.
- Log every trade action in the conversation thread.
