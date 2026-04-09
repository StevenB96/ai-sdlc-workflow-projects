# Runbook

## Purpose
This Apps Script workflow processes Google Form responses and classifies them with AI.

## Setup checks
- Form is linked to the correct sheet
- Sheet name is `Form Responses 1`
- Script Properties are configured
- Triggers have been created with the correct setup function

## Common failures
1. Missing Script Property
   - Add the missing property in Apps Script settings

2. HTTP error from provider
   - Check API key
   - Check model name
   - Review provider quota or billing

3. JSON parsing error
   - Inspect raw response
   - Tighten the prompt
   - Re-run on a sample row

## Manual recovery
- Mark failed rows as `MANUAL_REVIEW`
- Review the feedback manually
- Add notes in the sheet if needed

## Weekly digest
- Can run automatically every Monday
- Can also be run manually from the Apps Script editor

## Safety
- Do not auto-send customer responses
- Use outputs as drafts only
- Do not send secrets or production-sensitive content to the model