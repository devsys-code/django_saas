from rest_framework import generics, status, exceptions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from utl.permissions import IsAuthenticatedTenant, IsAdminRole
from mod.usr.models import User
from .serializers import LoginSerializer, UserMeSerializer
from .services import (
  check_password_hash,
  generate_tokens,
  set_refresh_cookie,
  clear_refresh_cookie,
  extract_refresh_token_from_request,
  refresh_tokens,
  logout_user,
  clean_expired_blacklist,
)

class LoginView(generics.GenericAPIView):
  permission_classes = [AllowAny]
  serializer_class = LoginSerializer

  def post(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    try:
      user = User.objects.get(email=email, deleted_at__isnull=True)
    except User.DoesNotExist:
      raise exceptions.AuthenticationFailed('Usuario no registrado')

    if not user.is_active:
      raise exceptions.AuthenticationFailed('Usuario no registrado')

    if not check_password_hash(password, user.password):
      raise exceptions.AuthenticationFailed('Contraseña incorrecta')

    access_token, refresh_token = generate_tokens(user)
    user_data = UserMeSerializer(user).data

    response = Response(
      {
        'access_token': access_token,
        'user': user_data,
      },
      status=status.HTTP_201_CREATED,
    )
    set_refresh_cookie(response, refresh_token)
    return response

class MeView(generics.RetrieveAPIView):
  permission_classes = [IsAuthenticatedTenant]

  def get(self, request, *args, **kwargs):
    return Response(
      {'user': UserMeSerializer(request.user).data},
      status=status.HTTP_200_OK,
    )

class RefreshView(generics.GenericAPIView):
  permission_classes = [AllowAny]

  def post(self, request, *args, **kwargs):
    refresh_token_str = extract_refresh_token_from_request(request)
    if not refresh_token_str:
      return Response(
        {'message': 'No refresh token proporcionado'},
        status=status.HTTP_201_CREATED,
      )

    new_access_token, new_refresh_token = refresh_tokens(refresh_token_str)
    response = Response(
      {'access_token': new_access_token},
      status=status.HTTP_201_CREATED,
    )
    set_refresh_cookie(response, new_refresh_token)
    return response

class LogoutView(generics.GenericAPIView):
  permission_classes = [IsAuthenticatedTenant]

  def post(self, request, *args, **kwargs):
    auth_header = request.headers.get('Authorization', '')
    access_token = auth_header.replace('Bearer ', '').strip()
    refresh_token = extract_refresh_token_from_request(request)

    logout_user(access_token, refresh_token)
    response = Response(
      {'message': 'Sesión cerrada exitosamente'},
      status=status.HTTP_201_CREATED,
    )
    clear_refresh_cookie(response)
    return response

class CleanupBlacklistView(generics.GenericAPIView):
  permission_classes = [IsAuthenticatedTenant, IsAdminRole]

  def post(self, request, *args, **kwargs):
    deleted = clean_expired_blacklist()
    return Response(
      {'message': f'{deleted} tokens expirados eliminados'},
      status=status.HTTP_201_CREATED,
    )
