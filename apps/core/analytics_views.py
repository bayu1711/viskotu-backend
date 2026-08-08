from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from apps.campaigns.models import Campaign
from apps.placements.models import AdPlacement
from apps.spaces.models import Space
from apps.jobs.models import PrintJob
from apps.payments.models import Payment, Payout
from django.utils import timezone
import datetime

class DashboardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = user.role

        if role == 'advertiser':
            return self.get_advertiser_stats(user)
        elif role == 'space-owner':
            return self.get_space_owner_stats(user)
        elif role == 'production-partner':
            return self.get_production_partner_stats(user)
        elif role == 'admin':
            return self.get_admin_stats(user)
        
        return Response({"detail": "Role not recognized"}, status=400)

    def get_advertiser_stats(self, user):
        campaigns = Campaign.objects.filter(advertiser=user)
        active_campaigns = campaigns.filter(status='active').count()
        total_spent = Payment.objects.filter(payer=user, status='succeeded').aggregate(total=Sum('amount'))['total'] or 0
        total_placements = AdPlacement.objects.filter(campaign__advertiser=user).count()
        total_impressions = campaigns.aggregate(total=Sum('impressions'))['total'] or 0
        
        return Response({
            "active_campaigns": active_campaigns,
            "total_spent": float(total_spent),
            "total_placements": total_placements,
            "est_impressions": total_impressions,
            "trends": {
                "spent": {"value": 0, "direction": "up"},
                "impressions": {"value": 0, "direction": "up"},
                "campaigns": {"value": 0, "direction": "up"},
                "placements": {"value": 0, "direction": "up"},
            },
            "recent_activity": [] # Add recent activity if needed
        })

    def get_space_owner_stats(self, user):
        spaces = Space.objects.filter(owner=user)
        active_listings = spaces.filter(status='ACTIVE').count()
        total_spaces = spaces.count()
        occupied_spaces = spaces.filter(status='OCCUPIED').count()
        occupancy_rate = (occupied_spaces / total_spaces * 100) if total_spaces > 0 else 0

        revenue = Payout.objects.filter(recipient=user, status='paid').aggregate(total=Sum('amount'))['total'] or 0
        pending_requests = AdPlacement.objects.filter(space__owner=user, status='PENDING').count()
        
        return Response({
            "active_listings": active_listings,
            "total_revenue": float(revenue),
            "pending_requests": pending_requests,
            "occupancy_rate": occupancy_rate,
            "trends": {
                "revenue": {"value": 0, "direction": "neutral"},
                "occupancy": {"value": 0, "direction": "neutral"}
            }
        })

    def get_production_partner_stats(self, user):
        jobs = PrintJob.objects.filter(production_partner=user)
        completed_jobs = jobs.filter(status='JOB_COMPLETED').count()
        revenue = Payout.objects.filter(recipient=user, status='paid').aggregate(total=Sum('amount'))['total'] or 0
        pending_jobs = jobs.filter(status='JOB_PENDING_ACCEPT').count()
        active_jobs = jobs.exclude(status__in=['JOB_COMPLETED', 'JOB_PENDING_ACCEPT', 'JOB_FORFEITED']).count()

        return Response({
            "completed_jobs": completed_jobs,
            "active_jobs": active_jobs,
            "pending_jobs": pending_jobs,
            "total_revenue": float(revenue),
        })

    def get_admin_stats(self, user):
        return Response({
            "total_users": 0,
            "total_campaigns": 0,
            "total_revenue": 0
        })
