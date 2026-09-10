#!/usr/bin/env python3
import anthropic
import os
from datetime import date

# ── 計算今天的課次 ────────────────────────────────────────────
START = date(2026, 9, 4)
today = date.today()
N = (today - START).days
date_str = today.strftime('%Y%m%d')
date_display = today.strftime('%Y-%m-%d')

THEMES = [
    '',
    '打招呼與基本禮貌用語', '數字 0-20', '顏色', '家庭成員',
    '食物與飲料', '星期與月份', '身體部位', '衣物', '情緒與感受',
    '動詞 être（是）', '動詞 avoir（有）', '動詞 aller（去）',
    '動詞 faire（做）', '動詞 vouloir/pouvoir', '地點與方向',
    '天氣與季節', '時間表達', '購物用語', '餐廳點餐用語', '複習與綜合練習',
]

if N % 11 == 10:
    r = N // 11 + 1
    s1 = (r - 1) * 10 + 1
    s2 = r * 10
    filename = f'fr_review_{r}_{date_str}.html'
    title = f'第{r}次總複習（第{s1}～{s2}課）'
    review_list = '\n'.join(
        f'第{s1+i}課：{THEMES[((s1+i-1)%20)+1]}' for i in range(10)
    )
    prompt = f"""你是一位專業法語老師。請生成第{r}次法文總複習的完整互動式 HTML 頁面。

涵蓋課程：第{s1}～{s2}課，日期：{date_display}
{review_list}

使用 Tailwind CSS CDN（https://cdn.tailwindcss.com），繁體中文，響應式設計。

頁面包含：
1. 特別標題區（金色漸層背景，顯示「第{r}次總複習 · 第{s1}-{s2}課」，{date_display}）
2. 複習摘要：10個主題各3個重點單字（共30個），每個單字有發音按鈕
3. 文法重點回顧：條列重要文法，卡片式
4. 大型配對遊戲（20題）：每個主題各抽2個單字
5. 綜合測驗（30題）：涵蓋全部主題，題型混合，最後顯示總分+評語+重新挑戰
6. 學習成就徽章：90%+金牌、70%+銀牌、50%+銅牌

所有發音按鈕必須使用 data-text 屬性：
<button onclick="speak(this)" data-text="法文">🔊</button>

speak 函數：
function speak(el) {{
  var text = typeof el === 'string' ? el : el.dataset.text;
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(text);
  u.lang = 'fr-FR'; u.rate = 0.85;
  window.speechSynthesis.speak(u);
}}

請直接輸出完整 HTML，不要任何說明文字或 markdown，直接從 <!DOCTYPE html> 開始。"""

else:
    ln = (N // 11) * 10 + (N % 11) + 1
    ti = ((ln - 1) % 20) + 1
    theme = THEMES[ti]
    filename = f'fr_lesson_{ln}_{date_str}.html'
    title = f'第{ln}課：{theme}'

    prompt = f"""你是一位專業法語老師。請生成第{ln}課「{theme}」的完整互動式 HTML 法文課程。

課次：{ln}，主題：{theme}，日期：{date_display}

使用 Tailwind CSS CDN（https://cdn.tailwindcss.com），繁體中文，響應式設計。

頁面包含：
1. 標題區（法國旗幟漸層背景 from-blue-800 via-white to-red-600，顯示第{ln}課/{date_display}/{theme}）
2. 今日單字10個（法文+IPA+詞性+陰陽性+中文+例句），卡片式
   - 單字本身必須有發音按鈕
   - 例句必須有獨立的發音按鈕（data-text 屬性）
3. 完整參考表（重要！）：若本課主題有固定完整列表（如12個月份、7個星期、4個季節、數字表、動詞六人稱變化等），必須用表格列出全部項目，每項有發音按鈕。
4. 基礎語句5句（法文+IPA+中文+發音按鈕）
5. 文法小提示1-2點
6. 配對遊戲：左10個法文單字（亂序），右10個中文（亂序），正確→綠色鎖定，錯誤→短暫紅色，顯示X/10進度，禁止把IPA放進選項。
7. 快問快答15題，題型混合（中法互譯+拼字題+陰陽性題+發音選擇題），最後顯示總分+評語+重新挑戰

所有發音按鈕必須使用 data-text 屬性（法文含撇號放 onclick 會出錯）：
正確：<button onclick="speak(this)" data-text="C'est un livre.">🔊</button>
禁止：<button onclick="speak('C\\'est')">🔊</button>

speak/speakBoth 函數固定版本（放入 HTML）：
function speak(el) {{
  var text = typeof el === 'string' ? el : el.dataset.text;
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(text);
  u.lang = 'fr-FR'; u.rate = 0.85;
  window.speechSynthesis.speak(u);
}}
function speakBoth(el) {{
  var textM = el.dataset.textM; var textF = el.dataset.textF;
  window.speechSynthesis.cancel();
  var u1 = new SpeechSynthesisUtterance(textM);
  u1.lang = 'fr-FR'; u1.rate = 0.85;
  var u2 = new SpeechSynthesisUtterance(textF);
  u2.lang = 'fr-FR'; u2.rate = 0.85;
  window.speechSynthesis.speak(u1);
  window.speechSynthesis.speak(u2);
}}

請直接輸出完整 HTML，不要任何說明文字或 markdown，直接從 <!DOCTYPE html> 開始。"""

# ── 存 metadata ───────────────────────────────────────────────
with open('/tmp/lesson_filename.txt', 'w') as f:
    f.write(filename)
with open('/tmp/lesson_title.txt', 'w') as f:
    f.write(title)

print(f'Generating: {filename}')
print(f'Title: {title}')

# ── 呼叫 Claude API ───────────────────────────────────────────
client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

message = client.messages.create(
    model='claude-sonnet-4-6',
    max_tokens=16000,
    messages=[{'role': 'user', 'content': prompt}],
)

html = message.content[0].text

# 移除可能的 markdown code block
if html.startswith('```'):
    lines = html.split('\n')
    end = len(lines) - 1 if lines[-1].strip() == '```' else len(lines)
    html = '\n'.join(lines[1:end])

# 確保從 <!DOCTYPE html> 開始
stripped = html.strip()
if not stripped.startswith('<!DOCTYPE') and not stripped.startswith('<html'):
    idx = html.find('<!DOCTYPE')
    if idx == -1:
        idx = html.find('<html')
    if idx != -1:
        html = html[idx:]

# ── 寫入檔案 ──────────────────────────────────────────────────
with open(filename, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Done: {filename} ({len(html):,} chars)')
