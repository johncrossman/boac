"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

from boac.api.util import advisor_required, scheduler_required
from boac.lib.http import tolerant_jsonify
from flask import current_app as app


@app.route('/api/appointments/<appointment_id>')
@advisor_required
def get_appointment(appointment_id):
    mock_appointment = {
        'id': appointment_id,
        'reason': 'Career Planning',
        'arrivalTime': '8:58am',
        'details': 'Looking to develop an action plan',
    }
    return tolerant_jsonify(mock_appointment)


@app.route('/api/appointments/<appointment_id>/check_in', methods=['POST'])
@scheduler_required
def appointment_check_in(appointment_id):
    return tolerant_jsonify({'status': f'Appointment check-in (id: {appointment_id})'}, status=200)


@app.route('/api/appointments/<appointment_id>/mark_read', methods=['POST'])
@advisor_required
def mark_appointment_read(appointment_id):
    return tolerant_jsonify({'status': f'Marked as read (id: {appointment_id})'}, status=200)
