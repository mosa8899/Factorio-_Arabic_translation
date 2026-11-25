#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تطبيق تعريب مودات Factorio — النسخة السهلة

كيف تستعملو (بدون أوامر):
  1. فكّ Mods_Arabic_Locale_Pack.zip مباشرة داخل مجلد mods بتاع اللعبة.
  2. شغّل run.bat (ويندوز) أو run.sh (لينكس/ماك) — أو شغّل هذا الملف.
  3. خلاص. السكريبت يعرف المودات لوحده ويضيفlocale/ar/.

يعمل مع المودات المضغوطة (.zip) والمفكوكة (مجلدات)،
ومع أي إصدار من نفس المود (المطابقة بالاسم مش بالإصدار).
"""
import os, re, sys, zipfile, shutil, argparse

def norm(s):
    return s.lower().replace('_', '-')

def matches(key, filename, is_dir=False):
    """هل هذا الملف/المجلد هو نفس المود (أي إصدار كان)؟"""
    k = norm(key)
    f = norm(filename)
    if f.endswith('.zip'):
        f = f[:-4]
    if is_dir:
        return f == k
    # aai-containers_0.4.0 -> aai-containers
    return f == k or bool(re.match(r'^' + re.escape(k) + r'[-_.]?\d', f))

def patch_zip(zpath, ar_files, backup=False, dry=False):
    if dry:
        return len(ar_files)
    if backup:
        shutil.copy2(zpath, zpath + '.ar-backup')
    tmp = zpath + '.ar.tmp'
    with zipfile.ZipFile(zpath, 'r') as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        names = zin.namelist()
        root = names[0].split('/')[0] + '/' if names and '/' in names[0] else ''
        existing = set(names)
        for item in zin.infolist():
            zout.writestr(item, zin.read(item.filename))
        for name, data in ar_files:
            arc = f'{root}locale/ar/{name}'
            if arc in existing:
                continue
            zout.writestr(arc, data)
    shutil.move(tmp, zpath)
    return len(ar_files)

def patch_dir(dpath, ar_files, dry=False):
    if dry:
        return len(ar_files)
    dst = os.path.join(dpath, 'locale', 'ar')
    os.makedirs(dst, exist_ok=True)
    for name, data in ar_files:
        with open(os.path.join(dst, name), 'wb') as f:
            f.write(data)
    return len(ar_files)

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()
    # إذا كان المستخدم فكّ الحزمة في مجلد المودات وفتح المجلد، نستعمل مكان تشغيله
    base = cwd if os.path.isdir(os.path.join(cwd, 'locales')) else here
    p = argparse.ArgumentParser(description='تطبيق تعريب المودات على مجلد mods')
    p.add_argument('--locale-root', default=os.path.join(base, 'locales'))
    p.add_argument('--mods-dir', default=base)
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--backup', action='store_true', help='احتفظ بنسخة .ar-backup قبل التعديل')
    p.add_argument('--skip-existing', action='store_true')
    a = p.parse_args()

    if not os.path.isdir(a.locale_root):
        print(f'❌ ما لقيت مجلد التعريب: {a.locale_root}')
        print('   فكّ Mods_Arabic_Locale_Pack.zip داخل مجلد mods أولاً.')
        return 1
    if not os.path.isdir(a.mods_dir):
        print(f'❌ ما لقيت مجلد المودات: {a.mods_dir}')
        return 1

    entries = os.listdir(a.mods_dir)
    zips = [x for x in entries if x.lower().endswith('.zip')]
    dirs = [x for x in entries if os.path.isdir(os.path.join(a.mods_dir, x)) and x.lower() not in ('locales',)]

    keys = [k for k in sorted(os.listdir(a.locale_root))
            if os.path.isdir(os.path.join(a.locale_root, k, 'locale', 'ar'))]
    patched = skipped = 0

    for key in keys:
        ar_dir = os.path.join(a.locale_root, key, 'locale', 'ar')
        ar_files = [(f, open(os.path.join(ar_dir, f), 'rb').read())
                    for f in sorted(os.listdir(ar_dir)) if f.endswith('.cfg')]
        if not ar_files:
            continue
        found = []

        # 1) مجلدات مودات مفكوكة
        for d in dirs:
            if matches(key, d, is_dir=True):
                found.append((os.path.join(a.mods_dir, d), 'dir', d))
        # 2) ملفات zip
        for z in zips:
            if matches(key, z):
                found.append((os.path.join(a.mods_dir, z), 'zip', z))

        if not found:
            print(f'⏭️  {key}: المود غير مثبّت (عادي)')
            skipped += 1
            continue

        for path, kind, label in found:
            n = patch_zip(path, ar_files, a.backup, a.dry_run) if kind == 'zip' \
                else patch_dir(path, ar_files, a.dry_run)
            state = '[معاينة] ' if a.dry_run else '✅ '
            print(f'{state}{label} ← {n} ملف عربي')
            patched += 1

    print(f'\nالنتيجة: {patched} مود عربي، {skipped} غير مثبّت.')
    if a.dry_run:
        print('(كانت معاينة فقط — ما تغيّر شي)')
    return 0

if __name__ == '__main__':
    sys.exit(main())
