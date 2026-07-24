from enum import Enum
from typing import TypedDict

class FaultType(Enum):
    ADVERTISER = 'ADVERTISER'
    PRINTER = 'PRINTER'
    HOST = 'HOST'
    PLATFORM = 'PLATFORM'
    NONE = 'NONE'

class SLAPenalty(TypedDict):
    fault: FaultType
    production_partner_paid: bool
    host_paid: bool
    advertiser_refunded: bool
    reroute_triggered: bool
    description: str

def get_sla_penalty(trigger: str, is_owner_produced: bool = False) -> SLAPenalty:
    if trigger == 'LATE_ARTWORK':
        return {
            'fault': FaultType.ADVERTISER,
            'production_partner_paid': True,
            'host_paid': True,
            'advertiser_refunded': False,
            'reroute_triggered': False,
            'description': 'Advertiser forfeited campaign time due to late artwork.'
        }
    elif trigger in ['MISSED_DEADLINE', 'MACHINE_FAILURE', 'MACHINE_BREAKDOWN', 'MISSED_SHIPPING_DEADLINE']:
        if is_owner_produced:
            return {
                'fault': FaultType.HOST,
                'production_partner_paid': False,
                'host_paid': False,
                'advertiser_refunded': True,
                'reroute_triggered': False,
                'description': 'Owner-produced job failed. Owner forfeits fees, advertiser refunded, reliability hit applied.'
            }
        return {
            'fault': FaultType.PRINTER,
            'production_partner_paid': False, # Clawback
            'host_paid': True,
            'advertiser_refunded': False,
            'reroute_triggered': True,
            'description': 'Job rerouted to backup production partner. Original production partner forfeits fee.'
        }
    elif trigger in ['MISSED_ACCEPT_WINDOW', 'DOUBLE_QA_FAIL']:
        if is_owner_produced:
            return {
                'fault': FaultType.HOST,
                'production_partner_paid': False,
                'host_paid': False,
                'advertiser_refunded': True,
                'reroute_triggered': False,
                'description': 'Owner-produced job failed. Owner forfeits fees, advertiser refunded, reliability hit applied.'
            }
        return {
            'fault': FaultType.PRINTER,
            'production_partner_paid': False,
            'host_paid': True,
            'advertiser_refunded': False,
            'reroute_triggered': True,
            'description': 'Job rerouted. Original production partner forfeits fee.'
        }
    elif trigger == 'TIME_SENSITIVE_MISS':
        if is_owner_produced:
            return {
                'fault': FaultType.HOST,
                'production_partner_paid': False,
                'host_paid': False,
                'advertiser_refunded': True,
                'reroute_triggered': False,
                'description': 'Owner-produced time-sensitive job missed. Owner forfeits fees, advertiser refunded, reliability hit applied.'
            }
        return {
            'fault': FaultType.PRINTER,
            'production_partner_paid': False,
            'host_paid': True,
            'advertiser_refunded': True,
            'reroute_triggered': False,
            'description': 'Time-sensitive campaign missed. Production partner penalized, advertiser refunded.'
        }
    else:
        return {
            'fault': FaultType.NONE,
            'production_partner_paid': True,
            'host_paid': True,
            'advertiser_refunded': False,
            'reroute_triggered': False,
            'description': 'No penalty.'
        }

def apply_forfeit_penalty(production_partner_id: str, job_id: str, forfeit_amount: float) -> dict:
    backup_fee = forfeit_amount * 0.7
    overnight_shipping_premium = forfeit_amount * 0.15
    host_compensation = forfeit_amount * 0.15

    return {
        'backup_fee': backup_fee,
        'overnight_shipping_premium': overnight_shipping_premium,
        'host_compensation': host_compensation
    }
