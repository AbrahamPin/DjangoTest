from rest_framework.views import APIView
from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from django.http import HttpResponse
from django.http import Http404

from yassapp.models import Auction
from yassapp.serializers import AuctionSerializer

@api_view(['GET'])
@renderer_classes([JSONRenderer,])
def blog_list(request):
    auctions = Auction.objects.all()
    serializer = AuctionSerializer(auctions, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def blog_detail(request, pk):
    try:
        auction = Auction.objects.get(pk=pk)
    except Auction.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = AuctionSerializer(auction)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.DATA
        print (request.DATA)
        serializer = AuctionSerializer(auction, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

class TokenAuthView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        data = request.data
        serializer = AuctionSerializer(data=data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)

class AuthView(APIView):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Auction.objects.get(pk=pk)
        except Auction.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        blog = self.get_object(pk)
        serializer = AuctionSerializer(blog)
        return Response(serializer.data)