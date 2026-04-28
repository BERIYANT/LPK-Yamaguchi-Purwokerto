from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from utils.authentication import login_required
from models.material_model import MaterialModel
import os

material_bp = Blueprint('material', __name__)

@material_bp.route('/material/<int:material_id>')
@login_required
def view_material(material_id):
    material = MaterialModel.get_by_id(material_id)
    if not material:
        flash("Materi tidak ditemukan.")
        return redirect(url_for('main.dashboard')) 
    
    return render_template('material/view.html', material=material)

@material_bp.route('/material/<int:material_id>/download')
@login_required
def download_material(material_id):
    material = MaterialModel.get_by_id(material_id)
    if not material:
        flash("Materi tidak ditemukan.")
        return redirect(url_for('main.dashboard'))
    
    if not material.get('file_path'):
        flash("Materi ini tidak memiliki file.")
        return redirect(url_for('material.view_material', material_id=material_id))
    
    try:
        file_path = material['file_path']
        # Normalize path
        if file_path.startswith('uploads/'):
            file_path = file_path[8:]
        
        # Try different possible paths
        possible_paths = [
            os.path.join('static/uploads', file_path),
            os.path.join('static/uploads', file_path.replace('uploads/', '')),
            os.path.join('static', file_path)
        ]
        
        for full_path in possible_paths:
            if os.path.exists(full_path):
                # Get file extension for download name
                file_ext = file_path.split('.')[-1] if '.' in file_path else 'file'
                download_name = f"{material['title']}.{file_ext}"
                
                return send_file(
                    full_path,
                    as_attachment=True,
                    download_name=download_name
                )
        
        flash("File tidak ditemukan di server.")
        return redirect(url_for('material.view_material', material_id=material_id))
        
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('material.view_material', material_id=material_id))

        #DARMUJI