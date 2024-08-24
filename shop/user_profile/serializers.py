from rest_framework import serializers



class InAvatarSerializer(serializers.ModelSerializer):
    src = serializers.CharField(allow_blank=False, required=True)
    alt = serializers.CharField(allow_blank=False, required=True)

class InProfileSerializer(serializers.Serializer):
    fullName = serializers.CharField(allow_blank=True, required=False)
    email = serializers.EmailField(allow_blank=True, required=False)
    phone = serializers.CharField(allow_blank=True, required=False)
    avatar = InAvatarSerializer(required=False)

class InChangePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(allow_blank=False, required=True)
    newPassword = serializers.CharField(allow_blank=False, required=True)




# class ProfileImageSerializer(ModelSerializer):
#     class Meta:
#         model = ProfileImage
#         fields = ["src", "alt"]
#
#
# class ProfileSerializer(ModelSerializer):
#     avatar = ProfileImageSerializer()
#
#     class Meta:
#         model = Profile
#         fields = ["middle_name", "email", "phone", "avatar"]
