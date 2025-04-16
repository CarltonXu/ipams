from flask import Blueprint, request, jsonify
from app.models import db, ScanSubnet
from app.utils.auth import token_required
from app.routes.scan.validators import validate_scan_request

subnet_bp = Blueprint('subnet', __name__)

@subnet_bp.route('/subnets', methods=['GET'])
@token_required
def get_subnets(current_user):
    """Get all scan subnets for current user"""
    subnets = ScanSubnet.query.filter_by(
        user_id=current_user.id,
        deleted=False
    ).all()
    return jsonify([subnet.to_dict() for subnet in subnets])

@subnet_bp.route('/subnets', methods=['POST'])
@token_required
@validate_scan_request
def add_subnet(current_user):
    """Add new scan subnet"""
    data = request.json
    
    new_subnet = ScanSubnet(
        user_id=current_user.id,
        name=data.get('name'),
        subnet=data.get('subnet')
    )
    
    db.session.add(new_subnet)
    db.session.commit()
    
    return jsonify({
        'message': 'Subnet added successfully',
        'subnet': new_subnet.to_dict()
    }), 201

@subnet_bp.route('/subnets/<subnet_id>', methods=['PUT'])
@token_required
@validate_scan_request
def update_subnet(current_user, subnet_id):
    """Update existing subnet"""
    subnet = ScanSubnet.query.filter_by(
        id=subnet_id,
        user_id=current_user.id,
        deleted=False
    ).first()
    
    if not subnet:
        return jsonify({'error': 'Subnet not found'}), 404
        
    data = request.json
    subnet.name = data.get('name', subnet.name)
    subnet.subnet = data.get('subnet', subnet.subnet)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Subnet updated successfully',
        'subnet': subnet.to_dict()
    })

@subnet_bp.route('/subnets/<subnet_id>', methods=['DELETE'])
@token_required
def delete_subnet(current_user, subnet_id):
    """Soft delete subnet"""
    subnet = ScanSubnet.query.filter_by(
        id=subnet_id,
        user_id=current_user.id,
        deleted=False
    ).first()
    
    if not subnet:
        return jsonify({'error': 'Subnet not found'}), 404
        
    subnet.deleted = True
    db.session.commit()
    
    return jsonify({'message': 'Subnet deleted successfully'})