from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Flight, Booking, Profile
import datetime

class FlightSerializer(serializers.ModelSerializer):
	class Meta:
		model = Flight
		fields = ['destination', 'time', 'price', 'id']

class BookingSerializer(serializers.ModelSerializer):
	# flight = serializers.SlugRelatedField(slug_field = 'destination', read_only=True)
	flight = serializers.SerializerMethodField()
	class Meta:
		model = Booking
		fields = ['flight', 'date', 'id']
	def get_flight(self, obj):
		return obj.flight.destination



class BookingDetailsSerializer(serializers.ModelSerializer):
	flight = FlightSerializer()
 # we are using the flightserializer because that is where we find the price of the flight model!
	total = serializers.SerializerMethodField()
	class Meta:
		model = Booking
		fields = ['total', 'flight', 'date', 'passengers', 'id']
	def get_total (self, obj):
		return obj.passengers * obj.flight.price




class AdminUpdateBookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['date', 'passengers']


class UpdateBookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['passengers']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name',]

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        new_user = User(username=username, first_name=first_name, last_name=last_name)
        new_user.set_password(password)
        new_user.save()
        return validated_data

class UserSerializer(serializers.ModelSerializer):
	class Meta:	
		model = User
		fields = ['first_name', 'last_name',]
		

class ProfileSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	past_bookings = serializers.SerializerMethodField()
# if you want to create new fields or override fields, you must define it above class Meta
	tier = serializers.SerializerMethodField()
	class Meta:
		model = Profile
		fields = ['user', 'miles', 'past_bookings', 'tier',]
	
	def get_tier (self, obj):	
		miles = obj.miles
		if miles >= 100000:
			return "Platinum"
		elif miles >= 60000:
			return "Gold"
		elif miles >= 10000:
			return "Silver"
		else:
			return "Blue"

	def get_past_bookings (self, obj):
		user_obj = obj.user
# 						^^ this pulls the user object from the Profile
		booking_list = user_obj.bookings.filter(date__lt= datetime.date.today())
# 					     ^^ this is in reference to the related name "bookings" because we have the user attribute as a ForeignKey in the Booking model
		# booking_list = Booking.objects.filter (user = user_obj)
# this is a second methold we can use too!
		return BookingSerializer(booking_list, many = True).data
# 												^^ we need to add this because we want to return a list not an individual object... The .data at the end converts the info to JSON


