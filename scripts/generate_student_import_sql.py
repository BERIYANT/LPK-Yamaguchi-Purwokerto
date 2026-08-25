#!/usr/bin/env python3
from datetime import datetime, timedelta
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

SOURCE = Path('/Users/mac/Downloads/DATA H2H SISWA LPK YAMAGUCHI.xlsx')
DETAIL_SOURCE = Path('/Users/mac/Downloads/DATA SISWA YAMAGUCHI 2026.xlsx')
OUTPUT = Path(__file__).resolve().parents[1] / 'student_profiles_import.sql'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
PKG_NS = {'p': 'http://schemas.openxmlformats.org/package/2006/relationships'}


def clean(value):
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', str(value)).strip()


def workbook_rows(path):
    with zipfile.ZipFile(path) as zf:
        shared = []
        if 'xl/sharedStrings.xml' in zf.namelist():
            root = ET.fromstring(zf.read('xl/sharedStrings.xml'))
            for item in root.findall('m:si', NS):
                shared.append(''.join(t.text or '' for t in item.iterfind('.//m:t', NS)))
        workbook = ET.fromstring(zf.read('xl/workbook.xml'))
        rels = ET.fromstring(zf.read('xl/_rels/workbook.xml.rels'))
        targets = {r.attrib['Id']: r.attrib['Target'] for r in rels.findall('p:Relationship', PKG_NS)}
        result = {}
        for sheet in workbook.find('m:sheets', NS):
            name = sheet.attrib['name']
            target = targets[sheet.attrib['{'+NS['r']+'}id']]
            target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
            target = re.sub(r'^xl/\.\./', '', target)
            root = ET.fromstring(zf.read(target))
            rows = []
            for row in root.findall('.//m:sheetData/m:row', NS):
                values = {}
                for cell in row.findall('m:c', NS):
                    ref = cell.attrib['r']
                    col = 0
                    for char in re.match(r'[A-Z]+', ref).group():
                        col = col * 26 + ord(char) - 64
                    value = ''
                    if cell.attrib.get('t') == 'inlineStr':
                        value = ''.join(t.text or '' for t in cell.iterfind('.//m:t', NS))
                    else:
                        node = cell.find('m:v', NS)
                        if node is not None:
                            value = node.text or ''
                            if cell.attrib.get('t') == 's':
                                value = shared[int(value)]
                    values[col - 1] = value
                if values:
                    width = max(values) + 1
                    rows.append([values.get(i, '') for i in range(width)])
            result[name] = rows
        return result


def excel_date(value):
    text = clean(value)
    if not text or not re.fullmatch(r'\d+(?:\.0+)?', text):
        return None
    return (datetime(1899, 12, 30) + timedelta(days=float(text))).date().isoformat()


def sql_value(value):
    if value in (None, ''):
        return 'NULL'
    return "'" + str(value).replace('\\', '\\\\').replace("'", "''") + "'"


def main():
    master = workbook_rows(SOURCE)
    detail = workbook_rows(DETAIL_SOURCE)['DATA SISWA']
    canonical_nis = {}
    notes = {}
    for sheet_name in ('2024', '2025', '2026', 'MJ'):
        for row in master.get(sheet_name, [])[3:]:
            if len(row) >= 7 and clean(row[5]) and clean(row[6]):
                canonical_nis[clean(row[6]).upper()] = clean(row[5])
                notes[clean(row[6]).upper()] = clean(row[13]) if len(row) > 13 else ''

    records = []
    for row in detail[2:]:
        if len(row) < 16 or not clean(row[2]) or not clean(row[3]):
            continue
        name = clean(row[3])
        nis = canonical_nis.get(name.upper())
        if not nis:
            raise ValueError(f'NIS resmi tidak ditemukan untuk {name}')
        gender = clean(row[4]).upper() if clean(row[4]).upper() in ('L', 'P') else None
        school = clean(row[5])
        address = clean(row[7]) if len(row) > 7 else ''
        rt_rw = clean(row[8]) if len(row) > 8 else ''
        village = clean(row[9]) if len(row) > 9 else ''
        district = clean(row[10]) if len(row) > 10 else ''
        city = clean(row[11]) if len(row) > 11 else ''
        province = clean(row[12]) if len(row) > 12 else ''
        nik = clean(row[13]) if len(row) > 13 else ''
        phone = clean(row[14]) if len(row) > 14 else ''
        enrollment = excel_date(row[15])
        if not enrollment:
            raise ValueError(f'Tanggal masuk tidak valid untuk {name}: {row[15]!r}')
        group = clean(row[1]).upper()
        if group == 'MJ':
            program = 'Matching Job'
        elif 'KM' in group:
            program = 'Kelas Malam'
        else:
            program = f'Pelatihan Bahasa Jepang - Angkatan {group}' if group else 'Pelatihan Bahasa Jepang'
        note = notes.get(name.upper(), '').upper()
        graduated = excel_date(row[16]) if len(row) > 16 else None
        flight = excel_date(row[17]) if len(row) > 17 else None
        if 'KELUAR' in note or clean(row[16]).upper() == 'KELUAR':
            status = 'keluar'
        elif 'PENDING' in note:
            status = 'pending'
        elif flight:
            status = 'terbang'
        elif graduated:
            status = 'lulus'
        else:
            status = 'aktif'
        sector = clean(row[18]) if len(row) > 18 else ''
        placement = clean(row[19]) if len(row) > 19 else ''
        records.append((
            nis, name, gender, school or None, nik or None, phone or None,
            address or None, rt_rw or None, village or None, district or None,
            city or None, province or None, program, enrollment, graduated, flight,
            sector or None, placement or None, status, notes.get(name.upper()) or None
        ))

    if len({r[0] for r in records}) != len(records):
        raise ValueError('Terdapat NIS duplikat pada sumber')

    lines = [
        '-- Impor profil siswa LPK Yamaguchi dari workbook yang diberikan.',
        '-- Aman dijalankan ulang: NIS yang sudah ada akan diperbarui, bukan digandakan.',
        'SET NAMES utf8mb4;',
        'START TRANSACTION;',
        '',
        'INSERT INTO `student_profiles`',
        '    (`nis`, `full_name`, `gender`, `school_name`, `nik`, `phone`, `address`,',
        '     `rt_rw`, `village`, `district`, `city`, `province`, `program_name`,',
        '     `enrollment_date`, `graduation_date`, `departure_date`, `job_sector`,',
        '     `placement`, `status`, `notes`)',
        'VALUES'
    ]
    values = []
    for record in records:
        values.append('    (' + ', '.join(sql_value(v) for v in record) + ')')
    lines.append(',\n'.join(values))
    lines.extend([
        'ON DUPLICATE KEY UPDATE',
        '    `full_name` = VALUES(`full_name`),',
        '    `gender` = VALUES(`gender`),',
        '    `school_name` = VALUES(`school_name`),',
        '    `nik` = VALUES(`nik`),',
        '    `phone` = VALUES(`phone`),',
        '    `address` = VALUES(`address`),',
        '    `rt_rw` = VALUES(`rt_rw`),',
        '    `village` = VALUES(`village`),',
        '    `district` = VALUES(`district`),',
        '    `city` = VALUES(`city`),',
        '    `province` = VALUES(`province`),',
        '    `program_name` = VALUES(`program_name`),',
        '    `enrollment_date` = VALUES(`enrollment_date`),',
        '    `graduation_date` = VALUES(`graduation_date`),',
        '    `departure_date` = VALUES(`departure_date`),',
        '    `job_sector` = VALUES(`job_sector`),',
        '    `placement` = VALUES(`placement`),',
        '    `status` = VALUES(`status`),',
        '    `notes` = VALUES(`notes`);',
        '',
        'COMMIT;',
        '',
        '-- Verifikasi setelah impor:',
        "SELECT COUNT(*) AS total_data_workbook FROM `student_profiles` WHERE `nis` LIKE '02%';",
        "SELECT YEAR(`enrollment_date`) AS tahun, COUNT(*) AS jumlah FROM `student_profiles` WHERE `nis` LIKE '02%' GROUP BY YEAR(`enrollment_date`) ORDER BY tahun;",
        ''
    ])
    OUTPUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f'{len(records)} records written to {OUTPUT}')


if __name__ == '__main__':
    main()
