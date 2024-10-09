from rest_framework import viewsets, permissions, filters
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

from .models import Achievement, Cat, User

from .serializers import AchievementSerializer, CatSerializer, UserSerializer
from .permissions import OwnerOrReadOnly, ReadOnly
# Кастомный троттлинг
from .throttling import WorkingHoursRateThrottle
# Кастомный пагинатор
from .pagination import CatsPagination

from django_filters.rest_framework import DjangoFilterBackend


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    # Устанавливаем разрешение
    permission_classes = (OwnerOrReadOnly,)

    # ___ТРОТТЛИНГ___
    # Подключили класс AnonRateThrottle
    # throttle_classes = (AnonRateThrottle,)

    # Если кастомный тротлинг-класс вернёт True - запросы будут обработаны
    # Если он вернёт False - все запросы будут отклонены
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    # А далее применится лимит low_request
    # Для любых пользователей установим кастомный лимит 1 запрос в минуту
    throttle_scope = 'low_request'

    # ___ПАГИНАЦИЯ___
    # Если пагинация установлена на уровне проекта, то для отдельного класса
    # её можно отключить, установив для атрибута pagination_class значение None.
    # pagination_class = PageNumberPagination

    # Даже если на уровне проекта установлен PageNumberPagination
    # Для котиков будет работать LimitOffsetPagination
    # pagination_class = LimitOffsetPagination

    # Вот он наш собственный класс пагинации с page_size=20
    pagination_class = CatsPagination

    # ___ФИЛЬТРАЦИЯ И ПОИСК___
    # Указываем фильтрующий бэкенд DjangoFilterBackend из библиотеки django-filter
    # и поисковый бэкенд SearchFilter
    # и сортировочный бэкенд OrderingFilter
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter,)
    # Фильтровать будем по полям color и birth_year модели Cat
    filterset_fields = ('color', 'birth_year')
    # В атрибуте search_fields указываются поля модели, по которым разрешён поиск
    # Поиск можно проводить и по содержимому полей связанных моделей.
    # Доступные для поиска поля связанной модели указываются через нотацию с двойным подчёркиванием:
    # ForeignKey текущей модели__имя поля в связанной модели.
    search_fields = ('name', 'achievements__name', 'owner__username',)
    # Поля для сортировки перечисляются в атрибуте ordering_fields, если его не указать, то
    # можно сортировать по любым доступным для чтения полям сериализатора, указанного в атрибуте serializer_class
    ordering_fields = ('name', 'birth_year')
    # Упорядочим выдачу наших котиков по умолчанию по имени.
    ordering = ('name',)

    def get_permissions(self):
        # Если в GET-запросе требуется получить информацию об объекте
        if self.action == 'retrieve':
            # Вернём обновлённый перечень используемых пермишенов
            return (ReadOnly(),)
        # Для остальных ситуаций оставим текущий перечень пермишенов без изменений
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
