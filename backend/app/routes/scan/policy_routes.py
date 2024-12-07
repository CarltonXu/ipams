from flask import Blueprint, request, jsonify
from ...models import db, ScanPolicy, ScanSubnet
from ...auth import token_required
from .validators import validate_scan_request
from datetime import datetime

policy_bp = Blueprint('policy', __name__)

@policy_bp.route('', methods=['GET'])
@token_required
def get_policies(current_user):
    """Get all scan policies for current user"""
    policies = ScanPolicy.query.filter_by(user_id=current_user.id).all()
    return jsonify([policy.to_dict() for policy in policies])

@policy_bp.route('', methods=['POST'])
@token_required
@validate_scan_request
def add_policy(current_user):
    """Add new scan policy"""
    data = request.json
    
    # Verify subnet exists and belongs to user
    subnet = ScanSubnet.query.filter_by(
        id=data.get('subnet_id'),
        user_id=current_user.id,
        deleted=False
    ).first()
    
    if not subnet:
        return jsonify({'error': 'Invalid subnet'}), 400
    
    new_policy = ScanPolicy(
        name=data.get('name'),
        user_id=current_user.id,
        subnet_id=data.get('subnet_id'),
        strategies=data.get('strategies'),
        threads=data.get('threads', 1)
    )
    
    db.session.add(new_policy)
    db.session.commit()
    
    return jsonify({
        'message': 'Policy created successfully',
        'policy': new_policy.to_dict()
    }), 201

@policy_bp.route('/<policy_id>', methods=['PUT'])
@token_required
def update_policy(current_user, policy_id):
    """Update existing policy"""
    policy = ScanPolicy.query.filter_by(
        id=policy_id,
        user_id=current_user.id
    ).first()
    
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
        
    data = request.json
    
    if 'subnet_id' in data:
        subnet = ScanSubnet.query.filter_by(
            id=data['subnet_id'],
            user_id=current_user.id,
            deleted=False
        ).first()
        if not subnet:
            return jsonify({'error': 'Invalid subnet'}), 400
        policy.subnet_id = data['subnet_id']
    
    policy.name = data.get('name', policy.name)
    policy.strategies = data.get('strategies', policy.strategies)
    policy.threads = data.get('threads', policy.threads)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Policy updated successfully',
        'policy': policy.to_dict()
    })

@policy_bp.route('/<policy_id>', methods=['DELETE'])
@token_required
def delete_policy(current_user, policy_id):
    """Delete policy"""
    policy = ScanPolicy.query.filter_by(
        id=policy_id,
        user_id=current_user.id
    ).first()
    
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
        
    db.session.delete(policy)
    db.session.commit()
    
    return jsonify({'message': 'Policy deleted successfully'})