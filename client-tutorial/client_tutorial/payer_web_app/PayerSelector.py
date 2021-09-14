#  Copyright (c) 2021 IBM Corporation
#  Henry Feldman, MD (CMO Development, IBM Watson Health)

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from ..InsuranceDao import InsuranceDao

bp = Blueprint('payer', __name__, url_prefix='/payer')

insuranceDao = InsuranceDao()

@bp.route('/payer', methods=('GET', 'POST'))
def selectPayer():
    if request.method == 'POST':
        payerId = request.form['payer_id']
        payer = insuranceDao.getPayer(payerId)
