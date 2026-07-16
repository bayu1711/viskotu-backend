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
