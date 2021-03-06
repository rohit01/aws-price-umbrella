# -*- coding: utf-8 -*-
#

from sethji.model.report import TagReport
from flask import Blueprint, render_template, redirect, url_for, request, g
from sethji.util import pretty_date, get_current_month_and_year
from sethji.views.account import requires_login
from datetime import datetime
from functools import wraps
import time


mod = Blueprint('report', __name__, url_prefix='/report')
DEFAULT_REPORT = 'Owner'


def organize_details(item_details, friendly_names={}):
    tags = {}
    for tag_name in item_details.get('tag_keys', '').split(','):
        if not tag_name:
            continue
        if item_details.get('tag:%s' % tag_name):
            tags[tag_name] = item_details.pop('tag:%s' % tag_name)
    if item_details.get('tag_keys'):
        item_details.pop('tag_keys')
        item_details['tags'] = tags
    if item_details.get('timestamp'):
        time_now = int(round(time.time()))
        check_time = int(item_details.pop('timestamp'))
        item_details['Last checked'] = pretty_date(check_time)
    month, year = get_current_month_and_year()
    friendly_names['monthly_cost'] = '%s, %s cost (USD)' % (month, year)
    friendly_names['per_hour_cost'] = 'Hourly cost (USD)'
    for k, v in friendly_names.items():
        if k in ['monthly_cost', 'per_gbm_storage_cost', 'per_mior_cost',
                 'per_iops_cost']:
            try:
                item_details[k] = "$ %s" % round(float(item_details.get(k)), 3)
            except (ValueError, TypeError):
                pass
        if k in item_details:
            item_details[v] = item_details.pop(k)


def set_tags_info(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        reports = TagReport()
        g.tags_info = reports.get_tags_info()
        return f(*args, **kwargs)
    return decorated_function


@mod.route("/")
@requires_login
@set_tags_info
def index():
    redirect_default = request.args.get('redirect', 'true').lower() != 'false'
    if (DEFAULT_REPORT in g.tags_info) and redirect_default:
        return redirect(url_for('report.report', tag_name=DEFAULT_REPORT,
                        tag_value='all'))
    elif g.tags_info and redirect_default:
        return redirect(url_for('report.report', tag_name=g.tags_info.keys()[0],
                        tag_value='all'))
    else:
        return render_template('report/index.html')


@mod.route("/<tag_name>/<tag_value>")
@requires_login
@set_tags_info
def report(tag_name, tag_value='all'):
    reports = TagReport()
    if tag_name not in g.tags_info:
        return redirect(url_for('report.index', redirect=False))
    tag_resources = reports.get_tag_resources(tag_name, tag_value)
    current_month, current_year = get_current_month_and_year()
    return render_template(
        'report/report.html',
        selected_tag=tag_name,
        selected_tag_value=tag_value,
        tag_resources=tag_resources,
        current_month=current_month,
        current_year=current_year,
    )


@mod.route("/instance/<region>/<instance_id>")
@requires_login
@set_tags_info
def instance_details(region, instance_id):
    friendly_names = {
        'zone': 'Zone',
        'instance_type': 'Instance Type',
        'ec2_private_dns': 'Private DNS',
        'region': 'Region',
        'state': 'State',
        'platform': 'Platform',
        'instance_id': 'Instance ID',
        'ec2_dns': 'Public DNS',
        'private_ip_address': 'Private IP Address',
        'ip_address': 'IP Address',
        'instance_elb_names': 'ELB Name(s)',
        'root_device_type': 'Root Device Type',
        'ebs_optimized': 'EBS Optimized',
        'ebs_ids': 'EBS Volumes',
        'launch_time': 'Launch Time',
        'architecture': 'Architecture',
        'vpc_id': 'VPC ID',
    }
    page_meta = {
        'title': "Instance details - %s" % instance_id,
        'name': "EC2 instance details",
        '404': "Instance not found!",
    }
    reports = TagReport()
    details = reports.get_instance_details(region, instance_id)
    if details.get('launch_time'):
        launch_time = datetime.strptime(
            details.get('launch_time').split('.')[0], "%Y-%m-%dT%H:%M:%S")
        details['launch_time'] = pretty_date(launch_time)
    organize_details(details, friendly_names)
    return render_template(
        'report/item_details.html',
        item_details=details,
        page_meta=page_meta,
    )


@mod.route("/ebs_volume/<region>/<volume_id>")
@requires_login
@set_tags_info
def ebs_volume_details(region, volume_id):
    current_month, current_year = get_current_month_and_year()
    friendly_names = {
        'create_time': 'Create Time',
        'volume_id': 'Volume ID',
        'instance_id': 'Instance ID',
        'iops': 'IOPS',
        'region': 'Region',
        'size': 'Size (in GB)',
        'parent_snapshot_id': 'Parent Snapshot ID',
        'status': 'Status',
        'type': 'Type',
        'zone': 'Zone',
        'per_gbm_storage_cost': 'Per GB per month cost (USD)',
        'per_mior_cost': 'Per million I/O requests cost (USD)',
        'per_iops_cost': 'Per IOPS cost (USD)',
    }
    page_meta = {
        'title': "EBS volume details - %s" % volume_id,
        'name': "EBS volume details",
        '404': "EBS volume not found!",
    }
    reports = TagReport()
    details = reports.get_ebs_volume_details(region, volume_id)
    if 'create_time' in details:
        create_time = datetime.strptime(
            details.get('create_time').split('.')[0], "%Y-%m-%dT%H:%M:%S")
        details['create_time'] = pretty_date(create_time)
    organize_details(details, friendly_names)
    return render_template(
        'report/item_details.html',
        item_details=details,
        page_meta=page_meta,
    )


@mod.route("/ebs_snapshot/<region>/<snapshot_id>")
@requires_login
@set_tags_info
def ebs_snapshot_details(region, snapshot_id):
    current_month, current_year = get_current_month_and_year()
    friendly_names = {
        'owner_alias': 'Owner alias',
        'owner_id': 'Owner ID',
        'start_time': 'Start Time',
        'description': 'Description',
        'snapshot_id': 'Snapshot ID',
        'progress': 'Progress',
        'status': 'Status',
        'parent_volume_id': 'Parent Volume ID',
        'encrypted': 'Encrypted',
        'size': 'Size (in GB)',
        'region': 'Region',
        'per_gbm_storage_cost': 'Per GB per month cost (USD)',
        'instance_id': 'Instance ID',
    }
    page_meta = {
        'title': "EBS snapshot details - %s" % snapshot_id,
        'name': "EBS snapshot details",
        '404': "EBS snapshot not found!",
    }
    reports = TagReport()
    details = reports.get_ebs_snapshot_details(region, snapshot_id)
    if 'start_time' in details:
        start_time = datetime.strptime(
            details.get('start_time').split('.')[0], "%Y-%m-%dT%H:%M:%S")
        details['start_time'] = pretty_date(start_time)
    organize_details(details, friendly_names)
    return render_template(
        'report/item_details.html',
        item_details=details,
        page_meta=page_meta,
    )


@mod.route("/elb/<region>/<elb_name>")
@requires_login
@set_tags_info
def elb_details(region, elb_name):
    friendly_names = {
        'elb_name': 'ELB Name',
        'region': 'Region',
        'elb_dns': 'DNS',
        'elb_instances': 'Instances',
        'subnets': 'Subnets',
        'created_time': 'Created Time',
        'vpc_id': 'VPC ID',
    }
    page_meta = {
        'title': "ELB details - %s" % elb_name,
        'name': "Elastic load balancer details",
        '404': "Elastic load balancer not found!",
    }
    reports = TagReport()
    details = reports.get_elb_details(region, elb_name)
    if 'elb_instances' in details:
        details['elb_instances'] = details['elb_instances'].replace(',', ', ')
    if 'created_time' in details:
        created_time = datetime.strptime(
            details.get('created_time').split('.')[0], "%Y-%m-%dT%H:%M:%S")
        details['created_time'] = pretty_date(created_time)
    organize_details(details, friendly_names)
    return render_template(
        'report/item_details.html',
        item_details=details,
        page_meta=page_meta,
    )


@mod.route("/elastic_ip/<elastic_ip>")
@requires_login
@set_tags_info
def elastic_ip_details(elastic_ip):
    friendly_names = {
        'region': 'Region',
        'elastic_ip': 'Elastic IP',
        'instance_id': 'Instance ID',
    }
    page_meta = {
        'title': "Elastic IP details - %s" % elastic_ip,
        'name': "Elastic IP details",
        '404': "Elastic IP not found!",
    }
    reports = TagReport()
    details = reports.get_elastic_ip_details(elastic_ip)
    organize_details(details, friendly_names)
    return render_template(
        'report/item_details.html',
        item_details=details,
        page_meta=page_meta,
    )
