"""
Database field helpers
"""
import datetime
import uuid
from string import ascii_lowercase
from django.db.models import Q
from jobboss.models import WorkCenter, Job, Vendor, Material

MAX_JOB_RETRIES = 20
DEFAULT_WORK_CENTER_NAME = 'OTHER'
DEFAULT_VENDOR_NAME = 'OTHER'


def shipping_option_summary(shipping_option_dict: dict) -> str:
    acct_number = shipping_option_dict.get('customers_account_number')
    carrier = shipping_option_dict.get('customers_carrier')
    shipping_method = shipping_option_dict.get('shipping_method')
    if acct_number:
        return '{} {}'.format(carrier, acct_number)
    else:
        return shipping_method


def terms_summary(payment_details_dict: dict) -> str:
    if payment_details_dict.get('payment_type') == 'credit_card':
        return 'Credit Card'
    else:
        return payment_details_dict.get('purchase_order_number')


def get_work_center(op_name: str) -> WorkCenter:
    if op_name:
        return WorkCenter.objects.filter(work_center__iexact=op_name).first()


def get_default_work_center(name: str = None) -> WorkCenter:
    if name is None:
        name = DEFAULT_WORK_CENTER_NAME
    qs = WorkCenter.objects.filter(work_center=name)
    if qs.count() > 0:
        return qs.first()
    return WorkCenter.objects.create(
        work_center=name,
        type='Direct',
        setup_labor_rate=0,
        run_labor_rate=0,
        labor_burden=0,
        machine_burden=0,
        ga_burden=0,
        queue_hrs=0,
        link_material=False,
        link_component=False,
        last_updated=datetime.datetime.now(),
        is_parent=False,
        has_parent=False,
        objectid=uuid.uuid4(),
        machines=1,
        operators=1,
        operators_per_machine=1,
        link_finishedgoods=False,
        link_hardware=False,
        link_supplies=False,
        link_misc=False,
        link_rawstock=False,
        finite_schedule=False,
        lag_hrs=0,
        uvamount1=0,
        uvamount2=0,
        uvnumeric1=0,
        uvnumeric2=0,
        uvdecimal1=0,
        equipment=False,
    )


def get_vendor(op_name: str) -> Vendor:
    if op_name:
        return Vendor.objects.filter(vendor__iexact=op_name).first()


def get_default_vendor(name: str = None) -> Vendor:
    if name is None:
        name = DEFAULT_VENDOR_NAME
    qs = Vendor.objects.filter(vendor=name)
    if qs.count() > 0:
        return qs.first()
    return Vendor.objects.create(
        vendor=name,
        status='Active',
        vendor_since=datetime.datetime.now(),
        lead_days=0,
        send_1099=False,
        currency_def=1,
        last_updated=datetime.datetime.now(),
        rating=10,
        send_report_by_email=False
    )


def increment_job(job_number):
    """Increment job number to find a unique value"""
    last_char = job_number[-1].lower()
    if last_char in ascii_lowercase and last_char != 'z':
        return job_number[0:-1] + \
               ascii_lowercase[ascii_lowercase.find(last_char) + 1]
    else:
        return job_number + 'a'


def get_available_job(order_number: int, sequence_number: int) -> str:
    """Returns an available job number given order number and job sequence
    number."""
    job_number = '{}-{}'.format(order_number, sequence_number)
    tries = 0
    while tries < MAX_JOB_RETRIES:
        if Job.objects.filter(job=job_number).count() == 0:
            return job_number
        job_number = increment_job(job_number)
        tries += 1
    raise ValueError("Can't find an unused job number for {}-{}".format(
        order_number, sequence_number))


def get_material(part_number: str) -> Material:
    pn = part_number.strip()
    return Material.objects.filter(material__iexact=pn).first()
