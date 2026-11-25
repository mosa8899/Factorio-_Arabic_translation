#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تطبيق تعريب مودات Factorio — ذكي وآمن

- يتعرّف على المود من info.json داخلو (اسم المود الحقيقي)، مش من اسم الملف.
- يشتغل مع أي إصدار وأي اسم ملف (حتى لو سمّيتو "موسى" أو "عبد الله").
- يضيف locale/ar/ فقط — ما يمسح ولا يبدّل أي ملف من اللعبة أو من المود.
- إعادة التشغيل بعد تحديث أي مود تعاود تعريبه تلقائياً.

الاستعمال: فكّ الحزمة داخل مجلد mods، ثم شغّل run.bat أو ./run.sh
"""
import os, re, sys, json, zipfile, shutil, argparse

def read_identity(path, is_zip):
    """يرجع اسم المود من info.json أو None"""
    try:
        if is_zip:
            with zipfile.ZipFile(path) as z:
                for n in z.namelist():
                    if n.lower().endswith('/info.json') or n.lower() == 'info.json':
                        data = z.read(n).decode('utf-8', errors='replace')
                        return json.loads(data).get('name', '').lower()
        else:
            for root, dirs, files in os.walk(path):
                if 'info.json' in files:
                    data = open(os.path.join(root, 'info.json'), encoding='utf-8', errors='replace').read()
                    return json.loads(data).get('name', '').lower()
                if root.count(os.sep) > path.count(os.sep) + 2:
                    break
    except Exception:
        pass
    return None

def patch_zip(zpath, ar_files, dry=False):
    if dry:
        return len(ar_files)
    tmp = zpath + '.ar.tmp'
    with zipfile.ZipFile(zpath, 'r') as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        names = zin.namelist()
        root = names[0].split('/')[0] + '/' if names and '/' in names[0] else ''
        existing = set(names)
        for item in zin.infolist():
            zout.writestr(item, zin.read(item.filename))
        for fname, data in ar_files:
            arc = f'{root}locale/ar/{fname}'
            if arc in existing:      # موجود أصلاً → ما نكرّروش
                continue
            zout.writestr(arc, data)
    shutil.move(tmp, zpath)
    return len(ar_files)

def patch_dir(dpath, ar_files, dry=False):
    if dry:
        return len(ar_files)
    dst = os.path.join(dpath, 'locale', 'ar')
    os.makedirs(dst, exist_ok=True)
    for fname, data in ar_files:
        p = os.path.join(dst, fname)
        if not os.path.exists(p):
            open(p, 'wb').write(data)
    return len(ar_files)

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()
    # إذا كنا داخل مجلد الحزمة (اللي حطّيتو داخل mods) → المودات في المجلد الأب
    is_pack = os.path.basename(here).lower().startswith('mods_arabic_locale')
    base = os.path.dirname(here) if is_pack else here
    if os.path.isdir(os.path.join(cwd, 'locales')) and not is_pack:
        base = cwd
    p = argparse.ArgumentParser(description='تعريب مودات Factorio (ذكي — يتجاهل الإصدار)')
    p.add_argument('--base', default=base)
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()

    loc_root = os.path.join(here, 'locales') if is_pack else os.path.join(a.base, 'locales')
    if not os.path.isdir(loc_root):
        print('❌ ما لقيت مجلد locales — فكّ الحزمة داخل مجلد mods أولاً.')
        return 1

    # خريطة: اسم المود الحقيقي ← مجلد التعريب
    mp_path = os.path.join(loc_root, 'mod_map.json')
    mp = {}
    if os.path.isfile(mp_path):
        try:
            mp = {k.lower(): v for k, v in json.load(open(mp_path, encoding='utf-8')).items()}
        except Exception:
            pass
    keys = {k.lower(): k for k in os.listdir(loc_root)
            if os.path.isdir(os.path.join(loc_root, k, 'locale', 'ar'))}
    for k in keys:
        mp.setdefault(k, keys[k])

    patched = 0
    log = ['=== بدء التعريب ===', f'مجلد المودات: {a.base}', f'مجلد التعريب: {loc_root}', '']
    items = []
    for name in sorted(os.listdir(a.base)):
        full = os.path.join(a.base, name)
        if name.lower().endswith('.zip'):
            items.append((full, True, name))
        elif os.path.isdir(full) and name.lower() not in ('locales',):
            items.append((full, False, name))

    for full, is_zip, label in items:
        ident = read_identity(full, is_zip)
        key = mp.get(ident or '') if ident else None
        if not key:
            # fallback: مطابقة بالاسم كـ prefix (أي إصدار)
            low = label.lower()
            if low.endswith('.zip'):
                low = low[:-4]
            for k in keys:
                if low == k or re.match(r'^' + re.escape(k) + r'[-_.]?\d', low):
                    key = keys[k]
                    break
        if not key:
            continue
        ar_dir = os.path.join(loc_root, key, 'locale', 'ar')
        if not os.path.isdir(ar_dir):
            continue
        ar_files = [(f, open(os.path.join(ar_dir, f), 'rb').read())
                    for f in sorted(os.listdir(ar_dir)) if f.endswith('.cfg')]
        if not ar_files:
            continue
        n = patch_zip(full, ar_files, a.dry_run) if is_zip else patch_dir(full, ar_files, a.dry_run)
        line = ('🔍 ' if a.dry_run else '✅ ') + f'{label}  ←  {n} ملف عربي'
        print(line); log.append(line)
        patched += 1

    result = f'النتيجة: {patched} مود تعرّب.' + (' (معاينة فقط)' if a.dry_run else '')
    print('\n' + result)
    log.append('')
    log.append(result)
    if patched == 0:
        tip = '⚠️ ما لقيت أي مود مطابق. تأكد فكّيت الحزمة داخل مجلد mods نفسه (جنب المودات).'
        print(tip); log.append(tip)
    log.append('=== انتهى ===')
    try:
        open(os.path.join(here, 'translation_result.txt'), 'w', encoding='utf-8').write('\n'.join(log) + '\n')
    except Exception:
        pass
    return 0

if __name__ == '__main__':
    sys.exit(main())
