const INPUT_SHEET = 'Form Responses 1';

function getProp_(name) {
  const value = PropertiesService.getScriptProperties().getProperty(name);
  if (!value) throw new Error('Missing Script Property: ' + name);
  return value;
}

function normaliseKey_(text) {
  return String(text).trim().toLowerCase().replace(/[^a-z0-9]+/g, '_');
}

function extractJson_(text) {
  const start = text.indexOf('{');
  const end = text.lastIndexOf('}');
  if (start === -1 || end === -1) {
    throw new Error('No JSON found in model output: ' + text);
  }
  return JSON.parse(text.substring(start, end + 1));
}

function ensureHttpOk_(response) {
  const code = response.getResponseCode();
  if (code >= 300) {
    throw new Error('HTTP ' + code + ': ' + response.getContentText());
  }
}

function getInputSheet_() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(INPUT_SHEET);
  if (!sheet) {
    throw new Error('Sheet not found: ' + INPUT_SHEET);
  }
  return sheet;
}

function prepareOutputColumns_() {
  const sheet = getInputSheet_();
  const headers = [
    'Theme',
    'Sentiment',
    'Urgency',
    'Next Action',
    'Owner Suggestion',
    'Follow-up Draft',
    'Status'
  ];
  sheet.getRange(1, 5, 1, headers.length).setValues([headers]);
}

function rowToObject_(headers, values) {
  const obj = {};
  headers.forEach(function (header, i) {
    obj[normaliseKey_(header)] = values[i];
  });
  return obj;
}

function writeAnalysis_(sheet, row, result) {
  sheet.getRange(row, 5, 1, 6).setValues([[
    result.theme || '',
    result.sentiment || '',
    result.urgency || '',
    result.next_action || '',
    result.owner_suggestion || '',
    result.follow_up_email || ''
  ]]);
  sheet.getRange(row, 11).setValue('PROCESSED');
}

function postGoogleChatAlert_(message) {
  const webhook = PropertiesService.getScriptProperties().getProperty('GOOGLE_CHAT_WEBHOOK_URL');
  if (!webhook) return;

  UrlFetchApp.fetch(webhook, {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({ text: message }),
    muteHttpExceptions: true
  });
}

function emailManager_(subject, body) {
  const email = PropertiesService.getScriptProperties().getProperty('MANAGER_EMAIL');
  if (!email) return;
  MailApp.sendEmail(email, subject, body);
}

function deleteAllTriggers_() {
  ScriptApp.getProjectTriggers().forEach(function (trigger) {
    ScriptApp.deleteTrigger(trigger);
  });
}

function processFeedbackRow_(sheet, row, analyserFn) {
  if (row <= 1) return;

  const headers = sheet.getRange(1, 1, 1, 4).getValues()[0];
  const values = sheet.getRange(row, 1, 1, 4).getValues()[0];
  const record = rowToObject_(headers, values);

  const result = analyserFn(record);
  writeAnalysis_(sheet, row, result);

  const urgency = String(result.urgency || '').toLowerCase();
  if (urgency === 'high' || urgency === 'critical') {
    postGoogleChatAlert_(
      'Urgent feedback detected\n' +
      'Customer: ' + (record.customer || 'Unknown') + '\n' +
      'Channel: ' + (record.channel || 'Unknown') + '\n' +
      'Feedback: ' + (record.feedback || '')
    );

    emailManager_(
      'Urgent feedback detected',
      'Customer: ' + (record.customer || 'Unknown') + '\n' +
      'Channel: ' + (record.channel || 'Unknown') + '\n' +
      'Feedback: ' + (record.feedback || '') + '\n\n' +
      'Suggested next action: ' + (result.next_action || '')
    );
  }
}

function buildWeeklyRecords_() {
  const sheet = getInputSheet_();
  const rows = sheet.getDataRange().getValues();
  const headers = rows[0];
  const cutoff = Date.now() - 7 * 24 * 60 * 60 * 1000;

  return rows
    .slice(1)
    .filter(function (row) {
      return new Date(row[0]).getTime() >= cutoff;
    })
    .map(function (row) {
      return rowToObject_(headers, row);
    });
}

function writeWeeklyDoc_(title, summary) {
  const doc = DocumentApp.create(title);
  doc.getBody().appendParagraph(summary);
  doc.saveAndClose();
  return doc.getUrl();
}

function emailWeeklyDigest_(summary, docUrl) {
  const managerEmail = getProp_('MANAGER_EMAIL');
  const body = summary + '\n\nGoogle Doc: ' + docUrl;
  MailApp.sendEmail(managerEmail, 'Weekly Feedback Digest', body);
}

function onFormSubmitOpenAI(e) {
  const sheet = e.range.getSheet();
  const row = e.range.getRow();

  try {
    processFeedbackRow_(sheet, row, analyseWithOpenAI);
  } catch (err) {
    sheet.getRange(row, 11).setValue('MANUAL_REVIEW');
    Logger.log(err.stack || err);
    emailManager_('OpenAI Feedback Hub Error', String(err));
  }
}

function testOpenAIOnLastRow() {
  const sheet = getInputSheet_();
  processFeedbackRow_(sheet, sheet.getLastRow(), analyseWithOpenAI);
}

function setupTriggersOpenAI() {
  deleteAllTriggers_();
  prepareOutputColumns_();

  ScriptApp.newTrigger('onFormSubmitOpenAI')
    .forSpreadsheet(SpreadsheetApp.getActive())
    .onFormSubmit()
    .create();

  ScriptApp.newTrigger('weeklyDigestOpenAI')
    .timeBased()
    .onWeekDay(ScriptApp.WeekDay.MONDAY)
    .atHour(8)
    .create();
}

function analyseWithOpenAI(record) {
  const apiKey = getProp_('OPENAI_API_KEY');
  const model = PropertiesService.getScriptProperties().getProperty('OPENAI_MODEL') || 'gpt-4o-mini';

  const payload = {
    model: model,
    temperature: 0.2,
    response_format: { type: 'json_object' },
    messages: [
      {
        role: 'system',
        content: 'You are a customer operations analyst. Return JSON with keys: theme, sentiment, urgency, next_action, owner_suggestion, follow_up_email. sentiment must be one of positive, neutral, negative. urgency must be one of low, medium, high, critical.'
      },
      {
        role: 'user',
        content: JSON.stringify(record, null, 2)
      }
    ]
  };

  const response = UrlFetchApp.fetch('https://api.openai.com/v1/chat/completions', {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + apiKey
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  });

  ensureHttpOk_(response);

  const data = JSON.parse(response.getContentText());
  return JSON.parse(data.choices[0].message.content);
}

function summariseWithOpenAI(records) {
  const apiKey = getProp_('OPENAI_API_KEY');
  const model = PropertiesService.getScriptProperties().getProperty('OPENAI_MODEL') || 'gpt-4o-mini';

  const payload = {
    model: model,
    temperature: 0.2,
    messages: [
      {
        role: 'system',
        content: 'You are a business operations analyst. Write a concise weekly digest with sections: Top Themes, Urgent Items, Recommended Actions, Risks, and 3 representative quotes. Keep it under 400 words.'
      },
      {
        role: 'user',
        content: JSON.stringify(records, null, 2)
      }
    ]
  };

  const response = UrlFetchApp.fetch('https://api.openai.com/v1/chat/completions', {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + apiKey
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  });

  ensureHttpOk_(response);

  const data = JSON.parse(response.getContentText());
  return data.choices[0].message.content;
}

function weeklyDigestOpenAI() {
  const records = buildWeeklyRecords_();
  const summary = summariseWithOpenAI(records);
  const title = 'Weekly Feedback Digest - ' +
    Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');
  const docUrl = writeWeeklyDoc_(title, summary);
  emailWeeklyDigest_(summary, docUrl);
}