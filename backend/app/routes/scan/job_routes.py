from flask import Blueprint, request, jsonify
from backend.app.models import db, ScanJob, ScanPolicy, ScanSubnet
from backend.app.utils.auth import token_required
from datetime import datetime

job_bp = Blueprint('job', __name__)

@job_bp.route('', methods=['GET'])
@token_required
def get_jobs(current_user):
    """Get all scan jobs for current user"""
    jobs = ScanJob.query.filter_by(user_id=current_user.id).all()
    return jsonify([job.to_dict() for job in jobs])

@job_bp.route('', methods=['POST'])
@token_required
def create_job(current_user):
    """Create new scan job"""
    data = request.json
    subnet_id = data.get('subnet_id')
    
    # Verify subnet exists and belongs to user
    subnet = ScanSubnet.query.filter_by(
        id=subnet_id,
        user_id=current_user.id,
        deleted=False
    ).first()
    
    if not subnet:
        return jsonify({'error': 'Invalid subnet'}), 400
    
    new_job = ScanJob(
        user_id=current_user.id,
        subnet_id=subnet_id
    )
    
    db.session.add(new_job)
    db.session.commit()
    
    # Here you would typically trigger the actual scan job
    # This could be done using Celery or another task queue
    
    return jsonify({
        'message': 'Scan job created successfully',
        'job': new_job.to_dict()
    }), 201

@job_bp.route('/<job_id>', methods=['GET'])
@token_required
def get_job_status(current_user, job_id):
    """Get scan job status"""
    job = ScanJob.query.filter_by(
        id=job_id,
        user_id=current_user.id
    ).first()
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
        
    return jsonify(job.to_dict())

@job_bp.route('/<job_id>/cancel', methods=['POST'])
@token_required
def cancel_job(current_user, job_id):
    """Cancel running scan job"""
    job = ScanJob.query.filter_by(
        id=job_id,
        user_id=current_user.id
    ).first()
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
        
    if job.status not in ['pending', 'running']:
        return jsonify({'error': 'Job cannot be cancelled'}), 400
        
    job.status = 'failed'
    job.end_time = datetime.utcnow()
    db.session.commit()
    
    # Here you would typically cancel the actual scan job
    # This depends on your task queue implementation
    
    return jsonify({'message': 'Job cancelled successfully'})