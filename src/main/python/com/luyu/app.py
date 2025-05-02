import sys

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from prophet import Prophet
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import logging
import traceback
import os

from waitress import serve
from werkzeug.exceptions import HTTPException
from pythonjsonlogger import jsonlogger

# 初始化Flask应用
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 生产环境配置
app.config.update(
    ENV='production',
    DEBUG=False,
    PROPAGATE_EXCEPTIONS=True
)

# 结构化日志配置
log_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s'
)
log_handler.setFormatter(formatter)
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)

# 数据库连接池配置
engine = create_engine(
    os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@localhost:3306/intelligent_dim_system"),
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)


class ValidationError(Exception):
    pass


@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        # 参数验证部分保持不变
        if not request.is_json:
            raise ValidationError("请求格式必须为JSON")

        data = request.get_json()
        batch_no = data.get('batch_no')
        periods = data.get('periods', 30)

        if not batch_no:
            raise ValidationError("缺少批次号参数")
        try:
            periods = int(periods)
            if periods <= 0:
                raise ValueError
        except ValueError:
            raise ValidationError("无效的预测周期参数")

        # 检查批次存在性
        batch_check_query = "SELECT batch_no FROM medicine_batches WHERE batch_no = %s"
        batch_exists = pd.read_sql_query(batch_check_query, engine, params=(batch_no,))
        if batch_exists.empty:
            return jsonify({
                "error": "批次不存在",
                "suggestion": "请确认批次号是否正确"
            }), 10404

        # 数据查询逻辑
        logging.info(f"查询批次{batch_no}的库存数据...")
        query = """
            SELECT ds, y FROM (
                SELECT 
                    ds,
                    SUM(daily_net) OVER (ORDER BY ds) AS y 
                FROM (
                    SELECT 
                        DATE(transaction_time) AS ds,
                        SUM(CASE 
                            WHEN transaction_type='IN' THEN quantity 
                            ELSE -quantity 
                        END) AS daily_net
                    FROM inventory_transactions
                    WHERE batch_no = %s
                    GROUP BY ds
                ) AS daily_summary
            ) AS final
            ORDER BY ds
        """
        df = pd.read_sql_query(query, engine, params=(batch_no,))

        # 数据校验（移除了重复检查）
        logging.info(f"数据校验: 共获取{len(df)}条数据")
        if df.empty:
            return jsonify({
                "error": "未找到库存记录",
                "detail": "该批次存在但无任何出入库记录",
                "suggestion": "请确认已完成入库操作"
            }), 10404
        if len(df) < 2:
            return jsonify({
                "error": "历史数据不足，无法预测",
                "detail": f"需要至少2个不同日期的数据（当前{len(df)}个）",
                "solution": [
                    "1. 确认该批次已完成多次出入库操作",
                    "2. 确保操作记录分布在不同日期"
                ]
            }), 10400

        # 模型训练部分保持不变
        try:
            model = Prophet(
                seasonality_mode='additive',
                weekly_seasonality=True,
                daily_seasonality=False
            )
            model.fit(df)
        except Exception as e:
            logging.error(f"模型训练失败: {str(e)}")
            return jsonify({"error": "预测模型初始化失败"}), 10500

        # 生成预测结果
        future = model.make_future_dataframe(periods=periods, include_history=False)
        forecast = model.predict(future)

        predictions = forecast[['ds', 'yhat']].rename(columns={
            'ds': 'date',
            'yhat': 'stock'
        })
        predictions['stock'] = predictions['stock'].clip(lower=0)
        predictions['date'] = predictions['date'].dt.strftime('%Y-%m-%d')

        return jsonify(predictions.to_dict(orient='records'))

    except ValidationError as e:
        logging.warning(f"参数验证失败: {str(e)}")
        return jsonify({"error": str(e)}), 10400
    except pd.io.sql.DatabaseError as e:
        logging.error(f"数据库错误: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "数据库操作失败"}), 10500
    except Exception as e:
        logging.error(f"系统错误: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "服务器内部错误"}), 10500

@app.route('/api/batches/<batch_no>', methods=['GET'])
def get_batch_info(batch_no):
    try:
        query = "SELECT medicine_id FROM medicine_batches WHERE batch_no = %s"
        batch_info = pd.read_sql_query(query, engine, params=(batch_no,))
        if batch_info.empty:
            return jsonify({"error": "批次不存在"}), 404
        return jsonify(batch_info.iloc[0].to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/alerts/<int:medicine_id>', methods=['GET'])
def get_alert_info(medicine_id):
    try:
        # 查询指定药品的预警阈值
        query = """
            SELECT 
                alert_level,
                min_quantity 
            FROM stock_alerts 
            WHERE medicine_id = %s
        """
        alert = pd.read_sql_query(query, engine, params=(medicine_id,))

        # 处理空结果情况
        if alert.empty:
            return jsonify({
                "medicine_id": medicine_id,
                "alert_threshold": 0  # 返回默认阈值0
            })

        # 返回实际配置
        alert_data = alert.iloc[0].to_dict()
        return jsonify(alert_data)

    except Exception as e:
        logging.error(f"预警查询错误: {str(e)}")
        return jsonify({
            "error": "预警配置查询失败",
            "detail": str(e)
        }), 10500


@app.route('/api')
def health_check():
    return "库存预测服务运行中"


# 统一处理所有HTTP错误
@app.errorhandler(HTTPException)
def handle_http_error(e):
    return jsonify({
        "error": e.name,
        "detail": e.description,
        "solution": "请检查请求地址是否正确"
    }), e.code


# 处理所有未捕获的异常
@app.errorhandler(Exception)
def handle_unexpected_error(e):
    logging.error(f"未捕获异常: {str(e)}\n{traceback.format_exc()}")
    return jsonify({
        "error": "服务器内部错误",
        "detail": "请求处理过程发生意外错误",
        "solution": [
            "1. 检查服务日志获取详细信息",
            "2. 确认输入数据格式正确",
            "3. 联系系统管理员"
        ]
    }), 10500


if __name__ == '__main__':
    if not getattr(sys, 'frozen', False):
        # 仅在非打包环境显示警告
        app.logger.warning("请不要直接运行python app.py，生产环境应使用gunicorn启动")
    else:
        # EXE运行模式使用生产配置
        from waitress import serve
        app.logger.info("项目启动成功！")
        serve(app, host="0.0.0.0", port=5000)
