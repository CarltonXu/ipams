from flask import Blueprint, request, jsonify
from app.models.models import db, ScanResult, ScanJob
from app.utils.auth import token_required
from sqlalchemy import desc
from datetime import datetime

result_bp = Blueprint('result', __name__)

@result_bp.route('/results', methods=['GET'])
@token_required
def get_results(current_user):
    """获取扫描结果列表"""
    try:
        # 获取查询参数
        job_id = request.args.get('job_id')
        ip_address = request.args.get('ip_address')
        open_ports = request.args.get('open_ports')
        service = request.args.get('service')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        # 构建基础查询
        query = ScanResult.query.join(ScanJob).filter(
            ScanJob.user_id == current_user.id,
            ScanResult.deleted == False
        )

        # 添加过滤条件
        if job_id:
            query = query.filter(ScanResult.job_id == job_id)
        if ip_address:
            query = query.filter(ScanResult.ip_address == ip_address)
        if open_ports:
            query = query.filter(ScanResult.port == open_ports)
        if service:
            query = query.filter(ScanResult.service == service)

        # 分页查询
        pagination = query.order_by(desc(ScanResult.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'results': [result.to_dict() for result in pagination.items]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@result_bp.route('/results/<result_id>', methods=['GET'])
@token_required
def get_result(current_user, result_id):
    """获取单个扫描结果详情"""
    try:
        result = ScanResult.query.join(ScanJob).filter(
            ScanResult.id == result_id,
            ScanJob.user_id == current_user.id,
            ScanResult.deleted == False
        ).first()

        if not result:
            return jsonify({'error': '结果不存在或无权访问'}), 404

        return jsonify(result.to_dict())

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@result_bp.route('/results/batch', methods=['POST'])
@token_required
def create_results(current_user):
    """批量创建扫描结果"""
    try:
        data = request.json
        job_id = data.get('job_id')
        results = data.get('results', [])

        if not job_id or not results:
            return jsonify({'error': '缺少必要参数'}), 400

        # 验证任务是否属于当前用户
        job = ScanJob.query.filter_by(
            id=job_id,
            user_id=current_user.id
        ).first()

        if not job:
            return jsonify({'error': '任务不存在或无权访问'}), 404

        # 批量创建结果
        new_results = []
        for result_data in results:
            result = ScanResult(
                job_id=job_id,
                ip_address=result_data['ip_address'],
                port=result_data.get('port'),
                protocol=result_data.get('protocol'),
                service=result_data.get('service'),
                version=result_data.get('version'),
                os_info=result_data.get('os_info'),
                status=result_data.get('status'),
                banner=result_data.get('banner'),
                raw_data=result_data.get('raw_data')
            )
            new_results.append(result)

        db.session.bulk_save_objects(new_results)
        db.session.commit()

        return jsonify({
            'message': '扫描结果保存成功',
            'count': len(new_results)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@result_bp.route('/results/<result_id>', methods=['DELETE'])
@token_required
def delete_result(current_user, result_id):
    """删除扫描结果"""
    try:
        result = ScanResult.query.join(ScanJob).filter(
            ScanResult.id == result_id,
            ScanJob.user_id == current_user.id,
            ScanResult.deleted == False
        ).first()

        if not result:
            return jsonify({'error': '结果不存在或无权访问'}), 404

        result.deleted = True
        result.deleted_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'message': '扫描结果删除成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 