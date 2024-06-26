from rest_framework import serializers
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserProfile
		fields = ('id', 'username', 'email', 'password') #fields = '__all__'
		extra_kwargs = {'password': {'write_only': True}}
	
	def create(self, validated_data):
		password = validated_data.pop('password', None)
		instance = self.Meta.model(**validated_data)
		if password is not None:
			instance.set_password(password)
		instance.save()
		return instance
	
	#	user = UserProfile.objects.create_user(
	#		id=validated_data['id'],
	#		username=validated_data['username'],
	#		email=validated_data['email'],
	#		password=validated_data['password']
	#	)
		#return user