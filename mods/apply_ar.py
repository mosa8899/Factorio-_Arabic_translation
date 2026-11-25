#!/usr/bin/env python3
"""يضيف ملفات locale/ar/*.cfg إلى مودات Factorio المضغوطة.

الاستعمال:
  python3 apply_ar.py <مجلد_التعريب> <مجلد_مودات_اللعبة> [--dry-run]

مجلد التعريب يجب أن يحتوي على مجلدات باسم المود، وبداخلها locale/ar/*.cfg.
"""
import sys, os, zipfile, shutil, tempfile, argparse

def main():
    p = argparse.ArgumentParser()
    p.add_argument('locale_root')
    p.add_argument('mods_dir')
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    if not os.path.isdir(a.locale_root) or not os.path.isdir(a.mods_dir):
        p.error('المجلدات غير موجودة')
    done = skipped = 0
    for modkey in sorted(os.listdir(a.locale_root)):
        ar_dir = os.path.join(a.locale_root, modkey, 'locale', 'ar')
        if not os.path.isdir(ar_dir):
            continue
        ar_files = [f for f in os.listdir(ar_dir) if f.endswith('.cfg')]
        if not ar_files:
            continue
        # ابحث عن zip يبدأ باسم المود
        match = None
        for z in os.listdir(a.mods_dir):
            if z.lower().startswith(modkey.lower()) and z.endswith('.zip'):
                match = z
                break
        if not match:
            print(f'تخطي: لم يُعثر على {modkey}.zip')
            skipped += 1
            continue
        zpath = os.path.join(a.mods_dir, match)
        if a.dry_run:
            print(f'[معاينة] {match} ← {len(ar_files)} ملف عربي')
            done += 1
            continue
        tmp = zpath + '.ar.tmp'
        with zipfile.ZipFile(zpath, 'r') as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
            root = zin.namelist()[0].split('/')[0]
            for item in zin.infolist():
                zout.writestr(item, zin.read(item.filename))
            for f in ar_files:
                arc = f'{root}/locale/ar/{f}'
                zout.writestr(arc, open(os.path.join(ar_dir, f), 'rb').read())
        shutil.move(tmp, zpath)
        print(f'تم: {match} (+{len(ar_files)} ملف عربي)')
        done += 1
    print(f'\nالنتيجة: {done} مود عربي، {skipped} تخطي.")

if __name__ == '__main__':
    main()
