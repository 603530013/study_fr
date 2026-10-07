#!/usr/bin/env python3
import anthropic
import os
from datetime import date

# ── 新排程：從 2026-09-11 起，每週一個主題 ────────────────────
# 週一～週五：新內容（同主題5天，逐步深入）
# 週六～週日：複習（遊戲強化 + 綜合測驗）

NEW_START = date(2026, 9, 11)   # 新排程起始日
today = date.today()
N = (today - NEW_START).days
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

week_num = N // 7 + 1           # 第幾週（從1起）
day_in_week = N % 7             # 0=週一, 1=週二... 4=週五, 5=週六, 6=週日
theme_idx = ((N // 7) % 20) + 1
theme = THEMES[theme_idx]

# 每天的內容焦點
DAY_FOCUS = {
    0: ('詞彙入門', f'介紹「{theme}」最核心的10個詞彙，搭配發音、IPA、例句、基礎語句5句和完整參考表'),
    1: ('語法深入', f'專注於「{theme}」相關的語法規則與變化，包含動詞變化表（若適用）、10個進階詞彙和語法練習'),
    2: ('情境對話', f'以真實生活情境為主，包含5組實用對話、情境相關詞彙10個，練習在對話中使用「{theme}」'),
    3: ('進階表達', f'擴展詞彙量，加入慣用語、文化背景知識，以及10個「{theme}」進階詞彙'),
    4: ('本週整理', f'回顧「{theme}」本週所有內容重點，20個精選詞彙複習，30題綜合測驗'),
}
REVIEW_FOCUS = {
    5: ('週末複習', f'強化「{theme}」詞彙記憶，以配對遊戲（20題）和填空練習為主，20題快速測驗'),
    6: ('週末挑戰', f'「{theme}」本週完整綜合測驗，30題混合題型，附詳細評分與學習建議'),
}

if day_in_week <= 4:
    day_num = day_in_week + 1   # 第1～5天
    focus_title, focus_desc = DAY_FOCUS[day_in_week]
    filename = f'fr_w{week_num}d{day_num}_{date_str}.html'
    title = f'第{week_num}週 Day{day_num}：{theme}（{focus_title}）'
    is_review = False
else:
    review_day = day_in_week - 4   # 1 or 2
    focus_title, focus_desc = REVIEW_FOCUS[day_in_week]
    filename = f'fr_w{week_num}r{review_day}_{date_str}.html'
    title = f'第{week_num}週 {focus_title}：{theme}'
    is_review = True

with open('/tmp/lesson_filename.txt', 'w') as f:
    f.write(filename)
with open('/tmp/lesson_title.txt', 'w') as f:
    f.write(title)

print(f'Week {week_num}, Day-in-week {day_in_week} → {filename}')
print(f'Title: {title}')

# ── 建立 prompt ───────────────────────────────────────────────
SPEAK_RULES = """
所有發音按鈕必須使用 data-text 屬性（法文含撇號，放 onclick 會出錯）：
正確：<button onclick="speak(this)" data-text="C'est un livre.">🔊</button>
禁止：<button onclick="speak('C\\'est')">🔊</button>

speak/speakBoth 函數（固定版本，放入 HTML）：
function speak(el) {
  var text = typeof el === 'string' ? el : el.dataset.text;
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(text);
  u.lang = 'fr-FR'; u.rate = 0.85;
  window.speechSynthesis.speak(u);
}
function speakBoth(el) {
  var textM = el.dataset.textM; var textF = el.dataset.textF;
  window.speechSynthesis.cancel();
  var u1 = new SpeechSynthesisUtterance(textM);
  u1.lang = 'fr-FR'; u1.rate = 0.85;
  var u2 = new SpeechSynthesisUtterance(textF);
  u2.lang = 'fr-FR'; u2.rate = 0.85;
  window.speechSynthesis.speak(u1);
  window.speechSynthesis.speak(u2);
}
"""

COMMON_FOOTER = "\n請直接輸出完整 HTML，不要任何說明文字或 markdown，直接從 <!DOCTYPE html> 開始。"

if not is_review:
    prompt = f"""你是一位專業法語老師。請生成「{theme}」主題第{day_in_week+1}天（{focus_title}）的完整互動式 HTML 法文課程。

主題：{theme}
今日焦點：{focus_desc}
日期：{date_display}，第{week_num}週 Day{day_num}

使用 Tailwind CSS CDN（https://cdn.tailwindcss.com），繁體中文，響應式設計。

頁面結構：
1. 標題區（法國旗幟漸層背景 from-blue-800 via-white to-red-600）
   顯示：第{week_num}週 · Day{day_num} · {theme} · {focus_title} · {date_display}
   副標：小標籤顯示本週5天進度（D1 D2 D3 D4 D5，今天高亮）

2. 今日詞彙10個（法文+IPA+詞性+陰陽性+中文+例句），卡片式
   - 有陰陽性變化的形容詞：陽性和陰性各一個發音按鈕
   - 單字本身和例句都必須有發音按鈕（data-text 屬性）

3. 完整參考表（若本主題有固定列表：7天、12月份、4季節、數字表、動詞六人稱變化等，必須列出全部，每項有發音按鈕）

4. 今日焦點內容（根據 {focus_title} 加入對應單元）：
   - 詞彙入門：基礎語句5句（法文+IPA+中文+發音按鈕）
   - 語法深入：完整語法說明卡、動詞變化表（若適用）
   - 情境對話：5組情境對話（每句有發音按鈕）
   - 進階表達：慣用語3-5個 + 文化小知識
   - 本週整理：本週重點摘要 + 文法回顧卡

5. 文法小提示1-2點

6. 配對遊戲：左10個法文（亂序）右10個中文（亂序），正確→綠色鎖定，錯誤→短暫紅色，X/10進度，禁止把IPA放進選項

7. 快問快答（{"30" if day_in_week == 4 else "15"}題），題型混合：
   - 中法互譯（4選1）
   - 拼字填空
   - 陰陽性選擇
   - 發音選擇（🔊聆聽後選正確單字）
   最後顯示總分+評語+重新挑戰按鈕
{SPEAK_RULES}{COMMON_FOOTER}"""

else:
    quiz_count = 20 if day_in_week == 5 else 30
    prompt = f"""你是一位專業法語老師。請生成「{theme}」主題{focus_title}的完整互動式 HTML 複習頁面。

主題：{theme}
今日焦點：{focus_desc}
日期：{date_display}，第{week_num}週 {'週六複習' if day_in_week == 5 else '週日挑戰'}

使用 Tailwind CSS CDN（https://cdn.tailwindcss.com），繁體中文，響應式設計。

頁面結構：
1. 標題區（{'藍紫漸層' if day_in_week == 5 else '金色漸層'}背景）
   顯示：第{week_num}週 · {focus_title} · {theme} · {date_display}

2. 本週詞彙總覽：20個「{theme}」核心詞彙快速回顧卡（法文+中文+發音按鈕）

3. {'大型配對遊戲（20題）：從本週詞彙中抽取，正確→綠色鎖定，錯誤→短暫紅色，顯示X/20進度' if day_in_week == 5 else '填空練習（10題）：給中文，填法文單字（或首字母提示），即時對錯回饋'}

4. 快問快答（{quiz_count}題），題型混合：
   - 中法互譯（4選1）
   - 拼字填空（給提示）
   - 陰陽性選擇
   - 例句填空
   - 發音選擇（🔊聆聽後選正確）
   最後顯示總分+詳細評語+{'重新挑戰按鈕' if day_in_week == 5 else '學習成就徽章（90%金牌/70%銀牌/50%銅牌）+重新挑戰'}
{SPEAK_RULES}{COMMON_FOOTER}"""

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
    for marker in ['<!DOCTYPE', '<html']:
        idx = html.find(marker)
        if idx != -1:
            html = html[idx:]
            break

with open(filename, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Done: {filename} ({len(html):,} chars)')
