# coding:utf-8
from flask import Flask, jsonify, request
import xunjia

app = Flask(__name__)


@app.route('/feizhuxunjia', methods=['GET'])
def get_tasks():
    depair = request.args.get('depair')
    arrair = request.args.get('arrair')
    deptime = request.args.get('deptime')
    tasks = xunjia.main(depair, arrair, deptime)
    return jsonify({'flag': 1, 'msg': '询价成功', 'data': tasks})


if __name__ == '__main__':
    app.run(debug=True)