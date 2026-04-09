# Test Plan

## Test records
Submit at least:
- one positive item
- one neutral or ambiguous item
- one urgent negative item

## Expected checks
- output columns E to K are populated
- status becomes `PROCESSED`
- urgent items trigger manager email
- urgent items optionally trigger Google Chat
- weekly digest creates a Google Doc
- weekly digest sends an email to the manager

## Failure handling
- simulated provider errors should set status to `MANUAL_REVIEW`
- manager should receive an error email