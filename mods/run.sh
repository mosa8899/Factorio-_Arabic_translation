#!/usr/bin/env bash
# شغّل هذا الملف من نفس مجلد mods — ما تحتاج تكتب أي أمر
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  python3 apply_ar.py
else
  python apply_ar.py
fi
echo
echo "خلاص. أغلق النافذة متاعك وأعد تشغيل Factorio."
read -r -p "اضغط Enter للخروج..." _ || true
