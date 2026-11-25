#!/usr/bin/env bash
# شغّل هذا الملف — يظهر لك تأكيد واضح ويحفظ النتيجة في ملف
cd "$(dirname "$0")" || exit 1

echo "=================================="
echo "   تعريب مودات Factorio  🧩"
echo "=================================="
echo

if command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi

"$PY" apply_ar.py 2>&1

echo
echo "📄 النتيجة محفوظة هنا: translation_result.txt"
echo "   افتح الملف إذا ما قرأت الرسائل فوق."
echo

if [ -t 0 ]; then
  read -r -p "اضغط Enter للخروج..." _
else
  sleep 6
fi
