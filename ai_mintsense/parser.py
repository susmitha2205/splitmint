import json
import re
import os
from .prompts import EXPENSE_PARSE_PROMPT, GROUP_SUMMARY_PROMPT, CATEGORIZE_PROMPT


def _call_groq(prompt: str, max_tokens: int = 300) -> str:
    """Call Groq API and return raw text response."""
    try:
        from groq import Groq
    except ImportError:
        raise RuntimeError("groq package not installed. Run: pip install groq")

    api_key = os.getenv('GROQ_API_KEY', '')
    if not api_key or api_key == 'your-groq-api-key-here':
        raise ValueError("No valid GROQ_API_KEY configured in .env")

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"Groq API error: {str(e)}")


def parse_expense_from_text(user_input: str) -> dict:
    """
    Parse a natural language expense description into structured data.
    Returns: {title, amount, category, note, error}
    """
    prompt = EXPENSE_PARSE_PROMPT.format(user_input=user_input)
    try:
        raw = _call_groq(prompt, max_tokens=300)
        # Strip possible markdown code fences
        raw = re.sub(r'```json|```', '', raw).strip()
        data = json.loads(raw)
        return {
            'title': data.get('title', ''),
            'amount': float(data.get('amount', 0)),
            'category': data.get('category', 'other'),
            'note': data.get('note', ''),
            'error': None,
        }
    except json.JSONDecodeError:
        return _fallback_parse(user_input)
    except RuntimeError as e:
        return _fallback_parse(user_input, str(e))


def _fallback_parse(user_input: str, error_msg: str = None) -> dict:
    """Rule-based fallback parser when AI is unavailable."""
    amount = 0.0
    matches = re.findall(r'[\d,]+\.?\d*', user_input)
    for m in matches:
        try:
            val = float(m.replace(',', ''))
            if val > 0:
                amount = val
                break
        except ValueError:
            continue

    # Guess category from keywords
    category = 'other'
    lower = user_input.lower()
    if any(w in lower for w in ['food', 'dinner', 'lunch', 'breakfast', 'restaurant',
                                  'pizza', 'zomato', 'swiggy', 'burger', 'biryani']):
        category = 'food'
    elif any(w in lower for w in ['uber', 'ola', 'cab', 'taxi', 'metro', 'bus',
                                   'petrol', 'fuel', 'auto', 'transport', 'flight', 'train']):
        category = 'transport'
    elif any(w in lower for w in ['hotel', 'airbnb', 'rent', 'stay', 'hostel', 'resort']):
        category = 'accommodation'
    elif any(w in lower for w in ['movie', 'cinema', 'concert', 'game', 'netflix',
                                   'spotify', 'park', 'entertainment']):
        category = 'entertainment'
    elif any(w in lower for w in ['shopping', 'amazon', 'flipkart', 'mall', 'clothes',
                                   'shoes', 'market']):
        category = 'shopping'
    elif any(w in lower for w in ['electricity', 'water', 'wifi', 'internet', 'bill',
                                   'recharge', 'mobile', 'dth']):
        category = 'utilities'
    elif any(w in lower for w in ['doctor', 'hospital', 'medicine', 'pharmacy',
                                   'medical', 'clinic']):
        category = 'medical'

    title = ' '.join(user_input.split()[:5]).title() if user_input else 'Expense'

    return {
        'title': title,
        'amount': amount,
        'category': category,
        'note': f'Parsed from: {user_input}',
        'error': error_msg,
        'fallback': True,
    }


def get_group_ai_summary(group) -> str:
    """Generate an AI-written summary for a group's expenses using Groq."""
    from collections import Counter

    expenses = group.expenses.all()
    if not expenses.exists():
        return "No expenses recorded yet for this group."

    total = sum(e.amount for e in expenses)
    categories = [e.category for e in expenses]
    top_cat = Counter(categories).most_common(1)[0][0] if categories else 'other'
    largest = max(expenses, key=lambda e: e.amount)
    unsettled = sum(
        s.amount for e in expenses for s in e.splits.filter(is_settled=False)
        if s.user != e.paid_by
    )

    prompt = GROUP_SUMMARY_PROMPT.format(
        group_name=group.name,
        total=total,
        count=expenses.count(),
        top_category=top_cat,
        largest=f"{largest.title} (Rs.{largest.amount})",
        unsettled=unsettled,
    )

    try:
        return _call_groq(prompt, max_tokens=250)
    except RuntimeError:
        return (
            f"Your group '{group.name}' has {expenses.count()} expense(s) "
            f"totalling Rs.{total:.2f}. "
            f"The most common category is {top_cat}. "
            f"Rs.{unsettled:.2f} is still pending settlement."
        )


def auto_categorize(title: str) -> str:
    """Auto-categorize an expense title using Groq AI."""
    prompt = CATEGORIZE_PROMPT.format(title=title)
    valid = {'food', 'transport', 'accommodation', 'entertainment',
             'shopping', 'utilities', 'medical', 'other'}
    try:
        result = _call_groq(prompt, max_tokens=10).lower().strip()
        first_word = result.split()[0] if result else 'other'
        return first_word if first_word in valid else 'other'
    except RuntimeError:
        return 'other'
