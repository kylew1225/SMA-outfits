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

1. **Large profit opportunity**: A high-conviction signal indicates a significant imminent gain (e.g., breakout, momentum surge, arbitrage window). Act first, then immediately message the user with what was executed and why.

2. **Large loss risk**: An open position is approaching or breaching a critical stop-loss level, or a sudden adverse move threatens significant capital loss. Close or hedge immediately, then notify the user with full details.

**After any urgent execution**, always send a summary that includes:
- What trade was placed (ticker, action, quantity, price)
- Why the urgent threshold was triggered
- Current position and P&L impact

## General Trading Conduct

- Never place a trade that exceeds the user's available buying power.
- Prefer limit orders over market orders unless urgency requires market execution.
- Always confirm the account state (positions, cash) before acting.
- Log every trade action in the conversation thread.
