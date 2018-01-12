from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.lib import util
from boac.lib.http import tolerant_jsonify
from boac.merged import calnet
from boac.merged import member_details
from boac.models.cohort_filter import CohortFilter
from boac.models.student import Student
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/cohorts/all')
@login_required
def all_cohorts():
    cohorts = {}
    for cohort in CohortFilter.all():
        for uid in cohort['owners']:
            if uid not in cohorts:
                cohorts[uid] = []
            cohorts[uid].append(cohort)
    owners = []
    for uid in cohorts.keys():
        owner = calnet.get_calnet_user_for_uid(app, uid)
        owner.update({
            'cohorts': sorted(cohorts[uid], key=lambda c: c['name']),
        })
        owners.append(owner)
    owners = sorted(owners, key=lambda o: (o['firstName'], o['lastName']))
    return tolerant_jsonify(owners)


@app.route('/api/cohorts/my')
@login_required
def my_cohorts():
    return tolerant_jsonify(CohortFilter.all_owned_by(current_user.get_id()))


@app.route('/api/intensive_cohort')
@login_required
def get_intensive_cohort():
    order_by = util.get(request.args, 'orderBy', None)
    offset = util.get(request.args, 'offset', 0)
    limit = util.get(request.args, 'limit', 50)
    results = Student.get_students(in_intensive_cohort=True, order_by=order_by, offset=offset, limit=limit)
    member_details.merge_all(results['students'])
    return tolerant_jsonify({
        'code': 'intensive',
        'label': 'Intensive',
        'name': 'Intensive',
        'members': results['students'],
        'totalMemberCount': results['totalStudentCount'],
    })


@app.route('/api/cohort/<cohort_id>')
@login_required
def get_cohort(cohort_id):
    order_by = util.get(request.args, 'orderBy', None)
    offset = util.get(request.args, 'offset', 0)
    limit = util.get(request.args, 'limit', 50)
    cohort = CohortFilter.find_by_id(int(cohort_id), order_by, int(offset), int(limit))
    if not cohort:
        raise ResourceNotFoundError('No cohort found with identifier: {}'.format(cohort_id))
    member_details.merge_all(cohort['members'])
    return tolerant_jsonify(cohort)


@app.route('/api/cohort/create', methods=['POST'])
@login_required
def create_cohort():
    params = request.get_json()
    label = util.get(params, 'label', None)
    gpa_ranges = util.get(params, 'gpaRanges')
    group_codes = util.get(params, 'groupCodes')
    levels = util.get(params, 'levels')
    majors = util.get(params, 'majors')
    unit_ranges_eligibility = util.get(params, 'unitRangesEligibility')
    unit_ranges_pacing = util.get(params, 'unitRangesPacing')
    if not label:
        raise BadRequestError('Cohort creation requires \'label\'')
    cohort = CohortFilter.create(uid=current_user.get_id(), label=label, gpa_ranges=gpa_ranges, group_codes=group_codes,
                                 levels=levels, majors=majors, unit_ranges_eligibility=unit_ranges_eligibility,
                                 unit_ranges_pacing=unit_ranges_pacing)
    return tolerant_jsonify(cohort)


@app.route('/api/cohort/update', methods=['POST'])
@login_required
def update_cohort():
    params = request.get_json()
    uid = current_user.get_id()
    label = params['label']
    if not label:
        raise BadRequestError('Requested cohort label is empty or invalid')
    cohort = get_cohort_owned_by(params['id'], uid)
    if not cohort:
        raise BadRequestError('Cohort does not exist or is not owned by {}'.format(uid))
    CohortFilter.update(cohort_id=cohort['id'], label=label)
    return tolerant_jsonify({'message': 'Cohort updated (label: {})'.format(label)}), 200


@app.route('/api/cohort/delete/<cohort_id>', methods=['DELETE'])
@login_required
def delete_cohort(cohort_id):
    if cohort_id.isdigit():
        cohort_id = int(cohort_id)
        uid = current_user.get_id()
        cohort = get_cohort_owned_by(cohort_id, uid)
        if cohort:
            CohortFilter.delete(cohort_id)
            return tolerant_jsonify({'message': 'Cohort deleted (id={})'.format(cohort_id)}), 200
        else:
            raise BadRequestError('User {uid} does not own cohort_filter with id={id}'.format(uid=uid, id=cohort_id))
    else:
        raise ForbiddenRequestError('Programmatic deletion of canned cohorts is not allowed (id={})'.format(cohort_id))


def get_cohort_owned_by(cohort_filter_id, uid):
    return next((c for c in CohortFilter.all_owned_by(uid) if c['id'] == cohort_filter_id), None)
