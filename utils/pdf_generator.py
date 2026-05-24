import os
from fpdf import FPDF
from datetime import datetime

def format_indo_date(dt):
    months = [
        'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ]
    return f"{dt.day} {months[dt.month - 1]} {dt.year}"

class RegistrationPDF(FPDF):
    def header(self):
        # Default white background, no rect drawing needed
        self.set_text_color(0, 0, 0)
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'logo_yamaguchi.png')
        if os.path.exists(logo_path):
            self.image(logo_path, 12, 10, 28)
        else:
            self.set_draw_color(0, 0, 0)
            self.cell(25, 25, 'LOGO', 1, 0, 'C') # Placeholder
            
        self.set_font('Times', 'B', 12)
        self.set_xy(45, 12)
        self.cell(0, 5, 'LEMBAGA PENDIDIKAN DAN KETERAMPILAN', ln=1)
        self.set_x(45)
        self.cell(0, 5, 'BAHASA DAN BUDAYA JEPANG - KOREA', ln=1)
        self.set_font('Times', 'B', 14)
        self.set_x(45)
        self.cell(0, 6, 'LPK YAMAGUCHI PURWOKERTO', ln=1)
        
        self.set_font('Times', '', 10)
        self.set_x(45)
        self.cell(0, 5, 'Gunung Putri Regency B3 Purwokerto, Jawa Tengah, Indonesia', ln=1)
        self.set_x(45)
        self.cell(0, 5, 'E-mail : yamaguchi.pwt@gmail.com Telp 081-2267-9292', ln=1)
        
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.4)
        self.line(15, 42, 195, 42)
        self.line(15, 43, 195, 43) # Double line effect
        
        # Watermark (looks wonderful on white background)
        if os.path.exists(logo_path):
            with self.local_context(fill_opacity=0.15, stroke_opacity=0.15):
                self.image(logo_path, 50, 90, 110)
                
        self.set_y(50)

def generate_registration_pdf(user_data):
    pdf = RegistrationPDF()
    pdf.add_page()
    
    pdf.set_text_color(0, 0, 0)
    
    # Title
    pdf.set_font('Times', 'B', 14)
    pdf.cell(0, 8, 'FORMULIR PENDAFTARAN', 0, 1, 'C')
    pdf.ln(8)
    
    # helper for label and value
    def print_row(label, value, indent=0, label_w=50):
        pdf.set_font('Times', '', 11)
        pdf.set_x(15 + indent)
        pdf.cell(label_w, 7, label)
        
        pdf.set_x(15 + indent + label_w)
        pdf.cell(5, 7, ':')
        
        pdf.set_x(15 + indent + label_w + 5)
        pdf.cell(0, 7, value, 0, 1)

    def print_multiline_row(label, value, indent=0, label_w=50):
        start_y = pdf.get_y()
        
        pdf.set_font('Times', '', 11)
        pdf.set_x(15 + indent)
        pdf.cell(label_w, 7, label)
        
        pdf.set_x(15 + indent + label_w)
        pdf.cell(5, 7, ':')
        
        start_x = 15 + indent + label_w + 5
        avail_w = 210 - 15 - start_x
        
        pdf.set_xy(start_x, start_y + 1.2)
        pdf.multi_cell(avail_w, 4.5, value, 0, 'L')
        
        end_y = pdf.get_y()
        next_y = max(end_y + 1.5, start_y + 7)
        pdf.set_y(next_y)

    full_name = user_data.get('full_name') or '..................................................................................'
    birth_place = user_data.get('birth_place') or '.......................'
    birth_date = user_data.get('birth_date') or '.........................'
    
    if birth_place != '.......................' and birth_date != '.........................':
        ttl = f"{birth_place} / {birth_date}"
    else:
        ttl = "............................................... / ..............................................."
        
    address = user_data.get('address') or '...................................................................................................'
    phone = user_data.get('phone') or '...................................................................................................'
    major = user_data.get('major', '') or ''
    education = user_data.get('education', '')
    
    # Extracted new fields
    nik = user_data.get('nik') or '...................................................................................................'
    
    # Calculate age if we have birth_date
    umur_val = '..................... Tahun'
    if user_data.get('birth_date') and user_data.get('birth_date') != '.........................':
        try:
            # Assumes format '%d-%m-%Y' or similar, let's just make it simple
            b_year = int(str(user_data.get('birth_date'))[-4:])
            current_year = datetime.now().year
            umur_val = f"{current_year - b_year} Tahun"
        except:
            pass

    label_width = 48
    
    print_row('NAMA LENGKAP', full_name, label_w=label_width)
    print_row('TEMPAT/TGL LAHIR', ttl, label_w=label_width)
    print_row('NO. NIK', nik, label_w=label_width)
    print_row('UMUR', umur_val, label_w=label_width)
    
    print_row('ASAL SEKOLAH', '', label_w=label_width)
    
    sd_name = user_data.get('sd_name') or ''
    sd_year = user_data.get('sd_year') or ''
    sd_val = f"{sd_name} Thn Lulus {sd_year}" if sd_name else (f"........................................... Thn Lulus {sd_year}" if sd_year else "........................................... Thn Lulus ...........")
    
    smp_name = user_data.get('smp_name') or ''
    smp_year = user_data.get('smp_year') or ''
    smp_val = f"{smp_name} Thn Lulus {smp_year}" if smp_name else (f"........................................... Thn Lulus {smp_year}" if smp_year else "........................................... Thn Lulus ...........")
    
    sma_name = user_data.get('sma_name') or ''
    sma_year = user_data.get('sma_year') or ''
    sma_val = f"{sma_name} Thn Lulus {sma_year}" if sma_name else (f"........................................... Thn Lulus {sma_year}" if sma_year else "........................................... Thn Lulus ...........")
    
    d3_name = user_data.get('d3_name') or ''
    d3_year = user_data.get('d3_year') or ''
    
    if d3_name:
        d3_val = f"{d3_name} Thn Lulus {d3_year}" if d3_year else f"{d3_name} Thn Lulus ..........."
    else:
        education_type = education if education in ['D3', 'S1', 'S2'] else ''
        if education_type:
            d3_val = f"{education_type} {major} Thn Lulus {d3_year}" if d3_year else f"{education_type} {major} Thn Lulus ..........."
        else:
            d3_val = f"........................................... Thn Lulus {d3_year}" if d3_year else "........................................... Thn Lulus ..........."
        
    print_row('SD/MI', sd_val, indent=15, label_w=33)
    print_row('SMP / MTs', smp_val, indent=15, label_w=33)
    print_row('SMA/SMK /MA', sma_val, indent=15, label_w=33)
    print_row('D3/S1', d3_val, indent=15, label_w=33)
    print_row('JURUSAN', major or '............................................................................', indent=15, label_w=33)
    
    print_multiline_row('ALAMAT LENGKAP', address, label_w=label_width)
    
    height = f"{user_data.get('height')} cm" if user_data.get('height') else '................ cm'
    weight = f"{user_data.get('weight')} kg" if user_data.get('weight') else '................ kg'
    blood_type = user_data.get('blood_type') or '................'
    
    print_row('NO. WA AKTIF', phone, label_w=label_width)
    print_row('TINGGI BADAN', height, label_w=label_width)
    print_row('BERAT BADAN', weight, label_w=label_width)
    print_row('GOLONGAN DARAH', blood_type, label_w=label_width)
    
    print_row('ORANG TUA/WALI', '', label_w=label_width)
    
    father = user_data.get('father_name') or '.........................................................................................'
    mother = user_data.get('mother_name') or '.........................................................................................'
    parent_phone = user_data.get('parent_phone') or '.........................................................................................'
    parent_address = user_data.get('parent_address') or '.........................................................................................'
    
    print_row('NAMA AYAH', father, indent=15, label_w=33)
    print_row('NAMA IBU', mother, indent=15, label_w=33)
    print_row('NO HP ORTU/WALI', parent_phone, indent=15, label_w=33)
    
    print_multiline_row('ALAMAT ORTU/WALI', parent_address, label_w=label_width)
    
    pdf.ln(12)
    y_before_photo = pdf.get_y()
    
    # Try to load Pas Foto file if provided
    pas_foto_file = user_data.get('pas_foto_file')
    photo_path = None
    if pas_foto_file:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        possible_path = os.path.join(project_root, 'static', 'uploads', pas_foto_file)
        if os.path.exists(possible_path):
            photo_path = possible_path
        else:
            fallback_path = os.path.join('static', 'uploads', pas_foto_file)
            if os.path.exists(fallback_path):
                photo_path = fallback_path

    # Pas Foto frame
    pdf.set_x(35)
    if photo_path:
        try:
            pdf.image(photo_path, 35, y_before_photo, 30, 40)
            # Add premium thin border around the image
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.3)
            pdf.rect(35, y_before_photo, 30, 40, 'D')
        except Exception as e:
            # Fallback if image load fails
            pdf.set_draw_color(0, 0, 0)
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(35, y_before_photo, 30, 40, 'DF')
            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(35, y_before_photo + 15)
            pdf.cell(30, 5, 'Pas Foto', 0, 1, 'C')
            pdf.set_x(35)
            pdf.cell(30, 5, '4 x 6', 0, 1, 'C')
    else:
        pdf.set_draw_color(0, 0, 0)
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(35, y_before_photo, 30, 40, 'DF')
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(35, y_before_photo + 15)
        pdf.cell(30, 5, 'Pas Foto', 0, 1, 'C')
        pdf.set_x(35)
        pdf.cell(30, 5, '4 x 6', 0, 1, 'C')
        
    # Signature line
    created_at = user_data.get('created_at')
    reg_date_str = ''
    if created_at:
        if isinstance(created_at, str):
            try:
                dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                reg_date_str = format_indo_date(dt)
            except:
                try:
                    dt = datetime.strptime(created_at, '%Y-%m-%d')
                    reg_date_str = format_indo_date(dt)
                except:
                    reg_date_str = str(created_at)
        elif hasattr(created_at, 'strftime'):
            reg_date_str = format_indo_date(created_at)
        else:
            reg_date_str = str(created_at)
    else:
        reg_date_str = format_indo_date(datetime.now())
        
    signature_place_date = f"Purwokerto, {reg_date_str}"
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(110, y_before_photo + 10)
    pdf.cell(85, 5, signature_place_date, 0, 1, 'C')
    
    # Try to load and render digital signature image if available
    signature_file = user_data.get('signature_file')
    sig_path = None
    if signature_file:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        possible_sig_path = os.path.join(project_root, 'static', 'uploads', signature_file)
        if os.path.exists(possible_sig_path):
            sig_path = possible_sig_path
        else:
            fallback_sig_path = os.path.join('static', 'uploads', signature_file)
            if os.path.exists(fallback_sig_path):
                sig_path = fallback_sig_path

    if sig_path:
        try:
            # Draw signature image centered in the signature zone (X: 132.5, Y: y_before_photo + 17, W: 40, H: 18)
            pdf.image(sig_path, 132.5, y_before_photo + 16, 40, 18)
        except Exception as e:
            print("Failed to render signature image in PDF:", e)
            
    pdf.ln(25)
    pdf.set_x(110)
    
    displayed_name = full_name if full_name and full_name != '..................................................................................' else 'Nama & Tanda Tangan Siswa'
    
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    pdf.cell(85, 5, displayed_name, 'T', 1, 'C')
    
    return pdf.output(dest='S')
