from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Space, SpacePhoto, SpaceAvailability
from .serializers import (
    SpaceSerializer, SpaceListSerializer,
    SpaceCreateUpdateSerializer, SpacePhotoSerializer,
    SpaceAvailabilitySerializer,
)


class SpaceViewSet(viewsets.ModelViewSet):
    """
    CRUD for spaces.
    - GET /spaces/         → list (browse, public)
    - GET /spaces/{id}/    → detail (public)
    - POST /spaces/        → create (auth required)
    - PATCH /spaces/{id}/  → update (owner only)
    - DELETE /spaces/{id}/ → delete (owner only)
    - GET /spaces/mine/    → my listings (auth required)
    - GET /spaces/reach/   → targeting reach estimate (auth required)
    """
    queryset = Space.objects.select_related('owner').prefetch_related('photos')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'city', 'state', 'category']
    ordering_fields = ['base_rate', 'created_at', 'occupancy_rate']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return SpaceListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return SpaceCreateUpdateSerializer
        return SpaceSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        # Filter by status (default: available for browse, all for owner)
        status_filter = params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        elif self.action == 'list' and not params.get('owner'):
            # Public browse: only show available spaces
            qs = qs.filter(status='available')

        # Filter by category
        category = params.get('category')
        if category and category != 'all':
            qs = qs.filter(category=category)

        # Price range
        price_min = params.get('price_min')
        price_max = params.get('price_max')
        if price_min:
            qs = qs.filter(base_rate__gte=price_min)
        if price_max:
            qs = qs.filter(base_rate__lte=price_max)

        # Featured only
        if params.get('featured') == 'true':
            qs = qs.filter(is_featured=True)

        # Owner filter (for space owner dashboard)
        if params.get('owner') == 'me':
            qs = qs.filter(owner=self.request.user)
        elif self.request.user.is_staff and params.get('all') == 'true':
            # Admin seeing all spaces
            pass

        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'mine']:
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mine(self, request):
        """GET /spaces/mine/ — my listings for the space owner dashboard."""
        spaces = Space.objects.filter(owner=request.user).prefetch_related('photos')
        serializer = SpaceSerializer(spaces, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_photo(self, request, pk=None):
        """POST /spaces/{id}/upload_photo/ — add a photo to a space."""
        space = self.get_object()
        if space.owner != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)

        file = request.FILES.get('image')
        if not file:
            return Response({'detail': 'No image provided.'}, status=status.HTTP_400_BAD_REQUEST)

        is_primary = not space.photos.exists()
        photo = SpacePhoto.objects.create(space=space, image=file, is_primary=is_primary)
        return Response(SpacePhotoSerializer(photo, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def availability(self, request, pk=None):
        """GET/POST /spaces/{id}/availability/ — blocked dates."""
        space = self.get_object()
        if request.method == 'GET':
            avail = SpaceAvailability.objects.filter(space=space)
            return Response(SpaceAvailabilitySerializer(avail, many=True).data)

        if space.owner != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = SpaceAvailabilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(space=space)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def pause(self, request, pk=None):
        space = self.get_object()
        if space.owner != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        space.status = 'paused'
        space.save(update_fields=['status'])
        return Response(SpaceSerializer(space, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unpause(self, request, pk=None):
        space = self.get_object()
        if space.owner != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        space.status = 'available'
        space.save(update_fields=['status'])
        return Response(SpaceSerializer(space, context={'request': request}).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='reach')
    def reach(self, request):
        """
        GET /spaces/reach/
        Query params (one set required):
          Spot / Region  → lat, lng, radius_km        (default radius_km=5)
          Route          → lat1, lng1, lat2, lng2, corridor_km (default 10)

        Returns:
          { space_count: int, total_daily_impressions: int }
        """
        import math

        def haversine(lat1, lng1, lat2, lng2):
            R = 6371
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlambda = math.radians(lng2 - lng1)
            a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
            return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        def point_to_segment_km(plat, plng, lat1, lng1, lat2, lng2):
            ax, ay = lng1, lat1
            bx, by = lng2, lat2
            px, py = plng, plat
            abx, aby = bx - ax, by - ay
            apx, apy = px - ax, py - ay
            denom = abx ** 2 + aby ** 2
            t = max(0.0, min(1.0, (apx * abx + apy * aby) / denom)) if denom > 1e-9 else 0.0
            return haversine(plat, plng, ay + t * aby, ax + t * abx)

        def parse_impressions(val):
            if not val:
                return 0
            try:
                return int(val)
            except (ValueError, TypeError):
                s = str(val).strip().upper().replace(',', '')
                if s.endswith('M'):
                    return int(float(s[:-1]) * 1_000_000)
                if s.endswith('K'):
                    return int(float(s[:-1]) * 1_000)
                return 0

        params = request.query_params

        # --- Spot / Region mode ---
        if params.get('lat') and params.get('lng'):
            try:
                lat = float(params['lat'])
                lng = float(params['lng'])
                radius_km = float(params.get('radius_km', 5))
            except (ValueError, TypeError):
                return Response({'detail': 'Invalid lat/lng/radius_km.'}, status=status.HTTP_400_BAD_REQUEST)

            deg = radius_km / 111.0
            qs = Space.objects.filter(
                status='available',
                latitude__isnull=False, longitude__isnull=False,
                latitude__gte=lat - deg, latitude__lte=lat + deg,
                longitude__gte=lng - deg, longitude__lte=lng + deg,
            ).only('latitude', 'longitude', 'impressions_estimate')

            matched = [s for s in qs if haversine(lat, lng, float(s.latitude), float(s.longitude)) <= radius_km]

        # --- Route mode ---
        elif params.get('lat1') and params.get('lng1') and params.get('lat2') and params.get('lng2'):
            try:
                lat1, lng1 = float(params['lat1']), float(params['lng1'])
                lat2, lng2 = float(params['lat2']), float(params['lng2'])
                corridor_km = float(params.get('corridor_km', 10))
            except (ValueError, TypeError):
                return Response({'detail': 'Invalid route params.'}, status=status.HTTP_400_BAD_REQUEST)

            deg = corridor_km / 111.0
            qs = Space.objects.filter(
                status='available',
                latitude__isnull=False, longitude__isnull=False,
                latitude__gte=min(lat1, lat2) - deg, latitude__lte=max(lat1, lat2) + deg,
                longitude__gte=min(lng1, lng2) - deg, longitude__lte=max(lng1, lng2) + deg,
            ).only('latitude', 'longitude', 'impressions_estimate')

            matched = [
                s for s in qs
                if point_to_segment_km(float(s.latitude), float(s.longitude), lat1, lng1, lat2, lng2) <= corridor_km
            ]

        else:
            return Response(
                {'detail': 'Provide lat+lng+radius_km (spot/region) or lat1+lng1+lat2+lng2 (route).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            'space_count': len(matched),
            'total_daily_impressions': sum(parse_impressions(s.impressions_estimate) for s in matched),
        })
