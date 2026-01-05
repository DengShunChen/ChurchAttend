# routes/stats.py
# 統計資訊路由
# Statistics Routes

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from database import get_db
from models import SessionModel

logger = logging.getLogger(__name__)

# 建立藍圖
stats_bp = Blueprint('stats', __name__, url_prefix='/stats')


@stats_bp.route('', methods=['GET'])
def get_statistics():
    """
    取得統計資訊
    Get statistics
    """
    try:
        db = get_db()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 今日出勤人數
        today_count = db.attendance.count_documents({'date': today})
        
        # 總出勤記錄數
        total_count = db.attendance.count_documents({})
        
        # 會友總數
        member_count = db.members.count_documents({})
        
        # 訪客總數
        visitor_count = db.visitors.count_documents({})
        
        # 最近一筆記錄
        latest = db.attendance.find_one(sort=[('date', -1)])
        
        stats = {
            'today_count': today_count,
            'total_count': total_count,
            'member_count': member_count,
            'visitor_count': visitor_count,
            'latest_date': latest['date'] if latest else None
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': '無法取得統計資訊 / Failed to get statistics'}), 500


@stats_bp.route('/sessions', methods=['GET'])
def get_session_statistics():
    """
    獲取場次統計
    Get session statistics
    """
    try:
        db = get_db()
        today = datetime.now().strftime('%Y-%m-%d')
        date_param = request.args.get('date', today)
        
        # 各場次人數統計
        session_stats = []
        sessions = SessionModel.get_all()
        
        for session in sessions:
            count = db.attendance.count_documents({
                'date': date_param,
                'session': session['id']
            })
            session_stats.append({
                'session_id': session['id'],
                'session_name': session['name'],
                'session_time': session['time'],
                'count': count
            })
        
        # 總人數
        total_count = db.attendance.count_documents({'date': date_param})
        
        return jsonify({
            'date': date_param,
            'total_count': total_count,
            'sessions': session_stats
        })
        
    except Exception as e:
        logger.error(f"Error getting session statistics: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@stats_bp.route('/weekly', methods=['GET'])
def get_weekly_statistics():
    """
    獲取週統計
    Get weekly statistics
    """
    try:
        db = get_db()
        from datetime import timedelta
        
        # 計算這週的開始和結束日期
        today = datetime.now()
        week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        week_end = (today + timedelta(days=6 - today.weekday())).strftime('%Y-%m-%d')
        
        # 查詢這週的出勤記錄
        weekly_records = db.attendance.find({
            'date': {'$gte': week_start, '$lte': week_end}
        })
        
        # 按日期分組統計
        daily_stats = {}
        for record in weekly_records:
            date = record['date']
            if date not in daily_stats:
                daily_stats[date] = 0
            daily_stats[date] += 1
        
        # 格式化結果
        result = []
        current_date = datetime.strptime(week_start, '%Y-%m-%d')
        for i in range(7):
            date_str = current_date.strftime('%Y-%m-%d')
            result.append({
                'date': date_str,
                'day': current_date.strftime('%A'),
                'count': daily_stats.get(date_str, 0)
            })
            current_date += timedelta(days=1)
        
        return jsonify({
            'week_start': week_start,
            'week_end': week_end,
            'daily_stats': result,
            'total': sum(r['count'] for r in result)
        })
        
    except Exception as e:
        logger.error(f"Error getting weekly statistics: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500


@stats_bp.route('/monthly', methods=['GET'])
def get_monthly_statistics():
    """
    獲取月統計
    Get monthly statistics
    """
    try:
        db = get_db()
        
        # 取得年月參數
        year = request.args.get('year', datetime.now().year)
        month = request.args.get('month', datetime.now().month)
        
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return jsonify({'error': '無效的年月參數 / Invalid year/month parameters'}), 400
        
        # 計算月份的開始和結束日期
        from calendar import monthrange
        month_start = f"{year}-{month:02d}-01"
        last_day = monthrange(year, month)[1]
        month_end = f"{year}-{month:02d}-{last_day}"
        
        # 查詢這個月的出勤記錄
        monthly_count = db.attendance.count_documents({
            'date': {'$gte': month_start, '$lte': month_end}
        })
        
        # 統計會友和訪客數量
        member_count = db.attendance.count_documents({
            'date': {'$gte': month_start, '$lte': month_end},
            'member_type': 'member'
        })
        
        visitor_count = db.attendance.count_documents({
            'date': {'$gte': month_start, '$lte': month_end},
            'member_type': 'visitor'
        })
        
        return jsonify({
            'year': year,
            'month': month,
            'month_start': month_start,
            'month_end': month_end,
            'total_count': monthly_count,
            'member_count': member_count,
            'visitor_count': visitor_count
        })
        
    except Exception as e:
        logger.error(f"Error getting monthly statistics: {str(e)}")
        return jsonify({'error': '伺服器錯誤 / Server error'}), 500
